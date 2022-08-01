import requests


project = "Test-Project"

res = requests.get('http://localhost:5050/outbound/get_report/{}'.format(project))

if res.ok:
    print(res.content)