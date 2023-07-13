import requests
import json

from app.core.YAMLFileManager import YAMLFileManager

query_url = "https://hackerone.com/programs/search?query=type:hackerone&sort=published_at:descending&page={page}"

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

scope_query = """
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


def hackerone_to_list():
    targets = {
        'domains': [],
        'with_bounty': [],
    }
    csv = [['handle', 'domain', 'eligible_for_bounty']]
    page = 1
    with requests.Session() as session:
        while True:
            r = session.get(query_url.format(page=page))
            page += 1
            if r.status_code != 200:
                break
            resp = json.loads(r.text)
            for program in resp['results']:
                r = session.get("https://hackerone.com{program}".format(
                    program=program['url']),
                    headers={'Accept': 'application/json'})
                if r.status_code != 200:
                    print('unable to retreive %s', program['name'])
                    continue

                resp = json.loads(r.text)
                print('policy scope ', resp['handle'])
                yaml = YAMLFileManager("../../resources/programs.yaml")
                data = yaml.read_data()
                new_name = {'name': resp['handle'], 'platform': "hackerone"}
                data["programs"].append(new_name)
                yaml.write_data(data)

    return targets, csv


def get_all_programs_scope_data_bugcrowd():
    targets = {
        'domains': [],
        'with_bounty': [],
    }
    page = 1
    with requests.Session() as session:
        while True:
            r = session.get(
                "https://bugcrowd.com/programs.json?hidden[]=false&page[]={page}&sort[]=promoted-desc".format(
                    page=page))
            page += 1
            if r.status_code != 200:
                break
            resp = json.loads(r.text)

            for program in resp["programs"]:
                print(program['name'])
                yaml = YAMLFileManager("../../resources/programs.yaml")
                data = yaml.read_data()
                new_name = {'name': program['name'], 'platform': "bugcrowd"}
                data["programs"].append(new_name)
                yaml.write_data(data)

    return targets


if __name__ == "__main__":
    targets = hackerone_to_list()
    targets2 = get_all_programs_scope_data_bugcrowd()
