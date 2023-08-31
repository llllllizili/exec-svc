#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   jk_rpa_mq.py
@Time    :   2021/05/07 10:13:59
'''

import json
from datetime import datetime
from utils.jklog import jklog
from utils.rabbitmqApi.mq import MessageQueueHandle
from utils.elasticApi.es import ElasticHandle
from django.conf import settings


class ListenError(Exception):
    pass


class RpaMQHandle(object):
    def __init__(self, func, job_num, node_num, task_num, exec_type, exec_async, custom_data, kwargs, log_server):
        self.func = func
        self.job_num = job_num
        self.task_num = task_num
        self.exec_type = exec_type
        self.log_server = log_server
        self.time_out = kwargs.get('timeout', 120)
        self.client = kwargs.get('client')
        self.args = kwargs.get('args')

        self.es_handle = ElasticHandle()

        self.rpa_result = None

    def __msg_push(self):
        try:
            push_rpa_msg = {'task_id': self.job_num, 'client': self.client, 'lua_path': self.args}  # 脚本路径还是脚本文件待商议
            # mq_handler = MessageQueueHandle(task_num=settings.JK_RPA_REQUEST)  # 推送消息给rpa client , 队列为固定队列
            mq_handler = MessageQueueHandle(task_num=self.client)  # 推送消息给rpa client 
            mq_handler.publish_job_status(message=push_rpa_msg)

            return True

        except Exception as e:
            return False

    # rpa_exec_engine
    def __msg_listen(self):

        # result = list()
        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # mq_handler = MessageQueueHandle(task_num=settings.JK_RPA_RESPONSE)  # rpa_response , 监听rpa的队列,执行成功,则任务成功
        mq_handler = MessageQueueHandle(task_num=self.job_num,)  # rpa_response , 监听rpa的队列,执行成功,则任务成功

        def __listen_callback(ch, method, properties, body):

            data = json.loads(body.decode())

            self.rpa_result = data

            ch.basic_ack(delivery_tag=method.delivery_tag)
            mq_handler.stop_listen_rpa_status()

            # task_id = data.get('task_id')
            
            # if task_id == self.job_num:
            #     ch.basic_ack(delivery_tag=method.delivery_tag)
            #     mq_handler.stop_listen_rpa_status()
            # else:
            #     ch.basic_reject(delivery_tag=method.delivery_tag)

        if self.__msg_push():

            mq_handler._listen_rpa_mq_status(__listen_callback)

            print("_____________________________________mq - _listen_rpa_mq_status - data")
            print(self.rpa_result)

            try:

                if self.log_server == 1:
                    log = '[{}: {} INFO/{}] {}\n'.format(start_date, self.exec_type, self.task_num, self.rpa_result)

                    self.es_handle.send_result(job_num=self.job_num, result=self.rpa_result, log=log)

                if self.rpa_result.get('code') == 0:
                    return True, 200, self.rpa_result

                return False, 500, self.rpa_result

            except Exception as e:

                return False, 500, '执行RPA task失败'

    def execute(self):
        if self.func == 'rpa.run':
            return self.__msg_listen()
