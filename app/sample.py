# coding=utf-8
__author__ = 'ffuuugor'
import requests
import json

def answer():
    data={"answer":"Юрий долгорукий"}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post("http://127.0.0.1:8080/answer?task_id=2", data=json.dumps(data), headers=headers)

    print r.status_code
    print r.json()
    print r.text
