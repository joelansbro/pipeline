"""
For testing and debugging

to see celery's task queue history, check out result.sqlite within sqlitebrowser

"""
import requests
res = requests.post('http://localhost:5000/inboundapi/add_message/1234', json={"mytext":"lalala"})

if res.ok:
    print(res.json())