import json
import uuid

import aiohttp
import requests
from fastapi import WebSocket


class HackerOneManager:
    query_url = "https://hackerone.com/programs/search?query=type:hackerone &sort=published_at:descending&page={page}"
    policy_scope_query = """
    query PolicySearchStructuredScopesQuery($handle: String!) {
      team(handle: $handle) {
        structured_scopes_search {
          nodes {
            ... on StructuredScopeDocument {
              identifier
              eligible_for_bounty
              eligible_for_submission
              display_name
              instruction
            }
          }
        }
      }
    }
    """

    def __init__(self, sessionManager, session_id):
        self.sessionManager = sessionManager
        self.session_id = session_id
        self.search_url = "https://hackerone.com/programs/search?query=type:hackerone {name}&sort=published_at:descending"
        self.policy_scope_query = """
        query PolicySearchStructuredScopesQuery($handle: String!) {
          team(handle: $handle) {
            structured_scopes_search {
              nodes {
                ... on StructuredScopeDocument {
                  identifier
                  eligible_for_bounty
                  eligible_for_submission
                  display_name
                  instruction
                }
              }
            }
          }
        }
        """

        self.scope_query = """
        query TeamAssets($handle: String!) {
          team(handle: $handle) {
            in_scope_assets: structured_scopes(
              archived: false
              eligible_for_submission: true
            ) {
              edges {
                node {
                  asset_identifier
                  asset_type
                  eligible_for_bounty
                }
              }
            }
          }
        }
        """

    def searchPrograms(self, name):
        r = requests.get(self.search_url.format(name=name))

    async def getScope(self, name, websocket: WebSocket):
        chatID = self.sessionManager.createChat(sessionId_=self.session_id, question=name)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://hackerone.com/{name}",
                                   headers={'Accept': 'application/json'}) as r:
                if r.status != 200:
                    print(f"Unable to retrieve {name}")
                    return

                resp = await r.json()
                print(resp)
                await websocket.send_json({"moderation_id": str(uuid.uuid4()),
                                           "data": "hackerone in-scope domains \n --------------------------"})
                self.sessionManager.updateChat(self.session_id, chatID,
                                               "hackerone in-scope domains \n --------------------------")
                # new scope
                query = json.dumps({'query': self.policy_scope_query,
                                    'variables': {'handle': resp['handle']}})
                async with session.post("https://hackerone.com/graphql",
                                        data=query,
                                        headers={'content-type': 'application/json'}) as r:
                    policy_scope_resp = await r.json()
                    print(policy_scope_resp)
                    for e in policy_scope_resp['data']['team']['structured_scopes_search']['nodes']:
                        if (e['display_name'] == 'Domain' and e['eligible_for_submission']) or \
                                (e['eligible_for_submission'] and e['identifier'].startswith('*')):
                            identifier = e['identifier']
                            for i in identifier.split(','):
                                self.sessionManager.updateChat(self.session_id, chatID, i)
                                await websocket.send_json({"moderation_id": str(uuid.uuid4()), "data": i})

                # old scope
                query = json.dumps({'query': self.scope_query,
                                    'variables': {'handle': resp['handle']}})
                async with session.post("https://hackerone.com/graphql",
                                        data=query,
                                        headers={'content-type': 'application/json'}) as r:
                    scope_resp = await r.json()
                    for e in scope_resp['data']['team']['in_scope_assets']['edges']:
                        node = e['node']
                        if node['asset_type'] == 'Domain' or node['asset_identifier'].startswith('*') or \
                                node['asset_type'] == 'URL':
                            identifier = node['asset_identifier']
                            for i in identifier.split(','):
                                self.sessionManager.updateChat(self.session_id, chatID, i)
                                await websocket.send_json({"moderation_id": str(uuid.uuid4()), "data": i})
