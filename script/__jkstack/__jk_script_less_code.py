#!/usr/bin/python
# -*- encoding: utf-8 -*-


import sys
import ast
import getopt

url = None
header = None
body = None

try:
    options, args = getopt.getopt(sys.argv[1:], "", ["header=", "body=", "url="])
except getopt.GetoptError as e:
    print('getopt error')
    print(e)
    sys.exit()

for option, value in options:
    if option in ("--header"):
        try:
            header = ast.literal_eval(value)
        except SyntaxError as e:
            header = value
    if option in ("--body"):
        try:
            body = ast.literal_eval(value)
        except SyntaxError as e:
            body = value
    if option in ("--url"):
        try:
            url = ast.literal_eval(value)
        except SyntaxError as e:
            url = value

# 以上为 自动生成部分


import json
import requests

def dpatest():

    result = requests.post(url=url, json=body, timeout=3, headers=header, verify=False)

    if result.status_code == 200:
        res = json.loads(result.content.decode('utf-8').replace('\'', '"'))
        print(res)


class ApiHandle(object):
    
    def __init__(self,body):
        self.url = url
        self.header = header
        self.args = body
    
    def exec_post(self):
        result = requests.post(url=self.url, json=self.args, timeout=3, headers=self.header, verify=False)

        if result.status_code == 200:
            res = json.loads(result.content.decode('utf-8').replace('\'', '"'))
            print(res)
if __name__ == '__main__':
    dpatest()

    # ApiHandle(body={"userName":"admin","userPwd":"MTIzNDU2","userType":"PLATFORM"}).exec_post()



# python a.py --url 'http://192.168.3.186:10001/user/userinfo/login' --header '{"Content-Type":"application/json"}' --body '{"userName":"admin","userPwd":"MTIzNDU2","userType":"PLATFORM"}'