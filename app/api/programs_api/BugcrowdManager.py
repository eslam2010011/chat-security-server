import json
import uuid

import aiohttp
import requests
from fastapi import WebSocket


class BugcrowdManager:

    def __init__(self, sessionManager, session_id):
        self.sessionManager = sessionManager
        self.session_id = session_id
        self.bugcrowd_url = "https://bugcrowd.com"

    def get_program_scope_data(self, code):
        scope_data = []
        targets = []
        target_groups_url = "%s/%s/target_groups.json" % (self.bugcrowd_url, code)
        resp = requests.get(target_groups_url)
        if (resp.status_code != 404):
            try:
                data = json.loads(resp.text)
            except:
                pass
            try:
                targets_url = data["groups"][0]["targets_url"]
                target_url = "%s/%s.json" % (self.bugcrowd_url, targets_url)
                target_resp = requests.get(target_url)
                data = json.loads(target_resp.text)
                targets = data["targets"]
            except:
                pass
            for target in targets:
                target_data = {"code": code, "name": target["name"], "uri": target["uri"],
                               "category": target["category"]}
                scope_data.append(target_data)
        return scope_data

    async def getScope(self, name, websocket: WebSocket):
        chatID = self.sessionManager.createChat(sessionId_=self.session_id, question=name)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://bugcrowd.com/programs.json?sort[]=promoted-desc&search[]={}&page[]=0".format(name),
                    headers={'Accept': 'application/json'}) as r:
                if r.status != 200:
                    print(f"Unable to retrieve {name}")
                    return

                data = await r.json()

                await websocket.send_json({"moderation_id": str(uuid.uuid4()),
                                           "data": "Bugcrowd in-scope domains \n --------------------------"})
                self.sessionManager.updateChat(self.session_id, chatID,
                                               "hackerone in-scope domains \n --------------------------")
                for program in data["programs"]:
                    targets = []
                    target_groups_url = "%s/%s/target_groups.json" % (self.bugcrowd_url, program["code"])
                    resp = requests.get(target_groups_url)
                    if (resp.status_code != 404):
                        try:
                            data = json.loads(resp.text)
                        except:
                            pass
                        try:
                            targets_url = data["groups"][0]["targets_url"]
                            target_url = "%s/%s.json" % (self.bugcrowd_url, targets_url)
                            target_resp = requests.get(target_url)
                            data = json.loads(target_resp.text)
                            targets = data["targets"]
                        except:
                            pass
                        for target in targets:
                            self.sessionManager.updateChat(self.session_id, chatID, target["name"])
                            await websocket.send_json({"moderation_id": str(uuid.uuid4()), "data": target["name"]})
