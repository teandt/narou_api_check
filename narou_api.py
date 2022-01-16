import json
import requests
import gzip


url = "http://api.syosetu.com/novelapi/api/"

payload = {"out": "json", "gzip": "5", "order": "old", "lim": "10"}

res = requests.get(url, params=payload)
cont = gzip.decompress(res.content).decode("utf-8")

res_json = json.loads(cont)

for i in res_json:
    print(i)


# for i in res_json:
#     if("title" in i):
#         print(i)

