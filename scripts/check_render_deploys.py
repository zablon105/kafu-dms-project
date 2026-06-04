import requests
import os

api_key = 'rnd_sNjda28EJkOCl6IrXkwB68ddq1fc'
service_id = 'srv-d77u2j3uibrs73c6eca0'

resp = requests.get(
    f'https://api.render.com/v1/services/{service_id}/deploys?limit=5',
    headers={'Authorization': f'Bearer {api_key}'}
)

if resp.status_code == 200:
    deploys = resp.json()
    for item in deploys:
        d = item['deploy']
        print(f"{d['id']} {d['status']:20} {d['commit']['message'][:60]}")
else:
    print(f"Error: {resp.status_code} {resp.text}")
