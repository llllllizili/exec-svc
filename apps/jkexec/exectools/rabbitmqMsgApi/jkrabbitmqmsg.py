#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   jkemptymsg.py
@Time    :   2021/04/28 19:29:53
'''

import json
from datetime import datetime
from utils.jklog import jklog
from utils.elasticApi.es import ElasticHandle


class RabbitmqMsgHandle():
    def __init__(self, func, job_num, exec_type, exec_async, task_num, node_num, custom_data, kwargs, log_server):
        '''
        :param hostid:
        :param type  cmd, script,scp_file,fetch_file:
        :param kwargs:
        '''

        self.func = func
        self.job_num = job_num
        self.task_num = task_num
        self.node_num = node_num
        self.log_server = log_server
        self.custom_data = custom_data
        self.exec_type = exec_type
        self.exec_async = exec_async
        self.time_out = kwargs.get('timeout', 60)
        self.args = kwargs.get('args')

        self.es_handle = ElasticHandle()

    def push_msg(self):

        jklog('file', '{} - __push_msg '.format(__file__))

        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        res_dict = dict(target='exec engine', start_date=start_date, status='SUCCESS', result=str(self.args), end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        log = '[{}: {} INFO/{}] {}\n'.format(start_date, self.exec_type, self.task_num, res_dict)

        if self.exec_async != 0:
            if self.log_server == 1:
                self.es_handle.send_result(job_num=self.job_num, result=res_dict, log=log)

        jklog('info', '{} exec success '.format(self.func))

        return True, 200, res_dict

    def execute(self):
        if self.func == 'msg.push':
            return self.push_msg()
        else:
            return False, 500, '不支持的方法 [ func not supported ]'