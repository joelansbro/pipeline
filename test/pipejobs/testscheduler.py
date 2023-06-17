"""
For testing and debugging

Use to test the scheduler, to ensure that the pipe runs

"""
import requests

res = requests.get('http://localhost:5000/test_scheduler')

if res.ok:
    print("pong")



