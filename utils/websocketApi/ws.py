#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   ws.py
@Time    :   2020/05/29 11:39:24
'''


import json
from utils.jklog import jklog
from django.conf import settings
from websocket import WebSocket, WebSocketBadStatusException, WebSocketTimeoutException, WebSocketException


class WebSocketHandle(object):
    """
    """

    def __init__(self, task_num):

        self.ws = WebSocket()
        
        try:
            ws_url = '{}/{}'.format(settings.WS_SERVER, task_num)
            self.ws.connect(url=ws_url, timeout=20)
        except WebSocketBadStatusException as e:
            jklog('file','{} - WebSocketHandle'.format(__file__))
            jklog('error',repr(e))
            pass
        except WebSocketTimeoutException as e:
            jklog('file','{} - WebSocketHandle'.format(__file__))
            jklog('error',repr(e))
            pass
        except WebSocketException as e:
            jklog('file','{} - WebSocketHandle'.format(__file__))
            jklog('error',repr(e))
            pass

        
    def send_message(self, data):
        """

        :param data:
        :return:
        """
        try:
            if self.ws.connected:
                if isinstance(data, str):
                    self.ws.send(data)

                if isinstance(data, dict):
                    self.ws.send(json.dumps(data))

        except Exception as e:
            jklog('file','{} - send_message'.format(__file__))
            jklog('error',repr(e))
            pass

    def __del__(self):
        if self.ws.connected:
            self.ws.close(timeout=20)


if __name__ == '__main__':
    ws_client = WebSocketHandle(task_num='12345')

    data = {
        'job_num': '12345',
        'status': 'STARTED',
        'logs': 'test1'
    }

    ws_client.send_message(data=data)

    import time

    time.sleep(2)

    data = {
        'job_num': '12345',
        'status': 'STARTED',
        'logs': 'test2'
    }

    ws_client.send_message(data=data)

    time.sleep(2)

    data = {
        'job_num': '12345',
        'status': 'STARTED',
        'logs': 'test3'
    }

    ws_client.send_message(data=data)

    time.sleep(2)

    data = {
        'job_num': '12345',
        'status': 'SUCCESS',
        'logs': 'test4'
    }

    ws_client.send_message(data=data)