

import requests
import json

title = "8 Reasons Python Sucks"
title = title.replace(" ", "%20")

res = requests.get('http://localhost:5000/outbound/get_article/{}'.format(title))

if res.ok:
    print(res.content)
    data = res.json()
    title = title.replace("%20", " ")
    with open ('{}.json'.format(title), 'w') as f:
        json.dump(data, f)