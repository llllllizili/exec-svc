#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   init_server.py
@Time    :   2020/10/26 20:32:43
'''

import os
import json
import uuid
import time
# import socket
# import nacos
import datetime
import requests
from threading import Timer
from exec_config import DPA_ADDRESS, EXEC_ENGINE_NAME, EXEC_ENGINE_IP

                         
CMDP_ADDRESS = None


def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


def dpa_registry():
    try:
        dpa_url = 'http://{}/process/executionengine/opSave'.format(DPA_ADDRESS)
        post_data = {'ip': str(EXEC_ENGINE_IP), 'name': str(EXEC_ENGINE_NAME), 'macAddress': get_mac_address()}
        headers = {"Content-Type": "application/json"}
        req_res = requests.post(dpa_url, data=json.dumps(post_data), headers=headers, timeout=5)
    except Exception as e:
        print(repr(e))
        pass

def cmdp_registry():
    try:
        pass
    except Exception as e:
        print(repr(e))
        pass

if DPA_ADDRESS:
    dpa_registry()
if CMDP_ADDRESS:
    cmdp_registry()


# 定时注册
def dpa_exec_engine_check():
    if DPA_ADDRESS:
        try:
            exec_url = 'http://{}:8093/token/access/'.format(EXEC_ENGINE_IP)
            login_data = {'username': 'admin', 'password': 'admin'}
            headers = {"Content-Type": "application/json"}
            time.sleep(10)
            req_res = requests.post(exec_url, data=json.dumps(login_data), headers=headers, timeout=5)
            print('exec: {}'.format(req_res.text))

            if 'access' in req_res.json() and 200 == req_res.status_code:
                dpa_url = 'http://{}/process/executionengine/opSave'.format(DPA_ADDRESS)
                post_data = {'ip': str(EXEC_ENGINE_IP), 'name': str(EXEC_ENGINE_NAME), 'macAddress': get_mac_address()}
                headers = {"Content-Type": "application/json","timestamp":(str(round(time.time() * 1000)))}

                req_res = requests.post(dpa_url, data=json.dumps(post_data), headers=headers, timeout=5)
                print('dpa: {}'.format(req_res.text))


                if 'code' in req_res.json() and 200 == req_res.json()['code']:
                    return 'engine is running & dpa registry success'
                #dpa 注册判断
                return 'engine is running & dpa registry failed'
            else:
                return 'engine is not running & dpa registry failed'
        except Exception as e:
            return repr(e)
 
def cmdp_exec_engine_check():
    if CMDP_ADDRESS:
        return 'engine is running & dpa registry failed'

def dpa_run():
    time.sleep(10)
    print('{} : {}'.format((datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), dpa_exec_engine_check()))
    Timer(30, dpa_run).start()

def cmdp_run():
    print('{} : {}'.format((datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), cmdp_exec_engine_check()))
    Timer(40, cmdp_run).start()


if __name__ == "__main__":
    if DPA_ADDRESS:
        dpa_run()
    if CMDP_ADDRESS:
        cmdp_run()
# nohup python /opt/jksreExecEngine/jksreExecEngine/init_server.py > /var/log/jkexec_init.log 2>&1 &
