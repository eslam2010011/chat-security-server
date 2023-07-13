# import json
#
# import requests
#
# from app.core.YAMLFileManager import YAMLFileManager
#
# bugcrowd_url = "https://bugcrowd.com"
#
#
# def get_program_scope_data(code):
#     scope_data = []
#     targets = []
#     target_groups_url = "%s/%s/target_groups.json" % (bugcrowd_url, code)
#     resp = requests.get(target_groups_url)
#     if (resp.status_code != 404):
#         try:
#             data = json.loads(resp.text)
#         except:
#             pass
#         try:
#             targets_url = data["groups"][0]["targets_url"]
#             target_url = "%s/%s.json" % (bugcrowd_url, targets_url)
#             target_resp = requests.get(target_url)
#             data = json.loads(target_resp.text)
#             targets = data["targets"]
#         except:
#             pass
#         for target in targets:
#             target_data = {"code": code, "name": target["name"], "uri": target["uri"], "category": target["category"]}
#             scope_data.append(target_data)
#     return scope_data
#
#
# def get_all_programs_scope_data():
#     programs_url = "%s/programs.json" % (bugcrowd_url)
#     resp = requests.get(programs_url, )
#     # print(resp.text)
#     data = json.loads(resp.text)
#     progtotal = data["meta"]["quickFilterCounts"]["all"]
#     print("[+] Total Programs : %s " % (progtotal), flush=1, end='\n')
#     offsets = 25
#     progcount = 0
#     all_targets_data = []
#
#     for offset in range(progcount, progtotal, offsets):
#         search_url = "%s?%s&offset[]=%d" % (programs_url, "sort[]=promoted-desc&hidden[]=false", offset)
#         resp = requests.get(search_url)
#         try:
#             data = json.loads(resp.text)
#         except:
#             continue
#         progcount += len(data["programs"])
#         print("[+] Collecting... (%d programs)                              " % (progcount), flush=1, end='\n')
#         for program in data["programs"]:
#             print(program['name'])
#             yaml = YAMLFileManager("../programs.yaml")
#             data = yaml.read_data()
#             new_name = {'name':program['name'], 'platform': "bugcrowd"}
#             data["programs"].append(new_name)
#             yaml.write_data(data)
#
#
#
# def write_csv_output(output):
#     keys = output[0].keys()
#
#
# if __name__ == "__main__":
#     get_all_programs_scope_data()
