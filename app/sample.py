# coding=utf-8
__author__ = 'ffuuugor'
import requests
import json

def answer():
    data={"answer":"Юрий долгорукий"}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post("http://52.10.86.71/answer?task_id=1", data=json.dumps(data), headers=headers)

    print r.status_code
    print r.json()
    print r.text

def add_pos():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data=[{"lat":55.758098, "lng":37.628775},
          {"lat":55.754862, "lng":37.633238},
          {"lat":55.753365, "lng":37.635040},
          {"lat":55.753461, "lng":37.639332},
          {"lat":55.752012, "lng":37.640963}]

    for d in data:
        r = requests.post("http://localhost:80/add_mrx_pos", data=json.dumps(d), headers=headers)
        print r.status_code
        print r.json()

def use_task():
    r = requests.post("http://localhost:80/use_task?task_id=2")
    print r.status_code
    print r.json()

def get_pos():
    r = requests.get("http://localhost:80/get_exposed_pos")
    print r.status_code
    print r.text

if __name__ == '__main__':
    get_pos()
