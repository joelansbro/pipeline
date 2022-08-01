

import requests
import json

title = "From Python to Numpy"
title = title.replace(" ", "%20")

res = requests.get('http://localhost:5050/outbound/get_article/{}'.format(title))

if res.ok:
    print(res.content)
    data = res.json()
    title = title.replace("%20", " ")
    with open ('{}.json'.format(title), 'w') as f:
        json.dump(data, f)