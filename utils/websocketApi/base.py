#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   base.py
@Time    :   2020/05/29 11:20:40
'''

from .ws import WebSocketHandle
from utils.jklog import jklog


def socket_handler(task_num, job_num, node_num, status, log, custom_data):
    """
    :param task_num:
    :param job_num:
    :param status:
    :param log:
    :return:
    """
    status_data = {'job_name': job_num, 'node_num': node_num, 'status': status, 'log': log, 'custom_data': custom_data}

    jklog('file', '{} - web_socket_handler'.format(__file__))
    jklog('info', '{}- ws connect success,node is {}'.format(job_num, node_num))
    # jklog('debug',status_data)

    try:
        ws_handler = WebSocketHandle(task_num=task_num)
        ws_handler.send_message(data=status_data)
    except Exception as e:
        jklog('file', '{} - web_socket_handler'.format(__file__))
        jklog('error', repr(e))
        pass
