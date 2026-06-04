import json
data = json.load(open(r'D:\kafu dms-project\kafu dms-project\render_deploys.json'))
for x in data:
    d = x['deploy']
    print(d['id'], d['status'], d['commit']['message'][:60])
