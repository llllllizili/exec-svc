#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   mq.py
@Time    :   2020/05/29 16:42:13
'''


import json
import ssl
import pika
import logging
# from config_dev import JK_MQ_USER, JK_MQ_HOST, JK_MQ_PORT, JK_MQ_PASSWORD, JK_MQ_EXCHANGE
from django.conf import settings
from pika import BlockingConnection, BasicProperties, URLParameters
from pika.credentials import ExternalCredentials
from utils.jklog import jklog

logger = logging.getLogger('console')


class ListenError(Exception):
    pass

class MessageQueueHandle(object):

    def __init__(self, task_num):

        self.conn = None
        self.channel = None
        self.properties = None

        self.task_num = task_num

    def __conn(self):
        all_endpoints = []

        # if ENABLE_OTHER_MQ_CLUSTER_SSL:
            # 这里走ssl

        if settings.ENABLE_OTHER_MQ_CLUSTER_SSL:

            context = ssl._create_unverified_context(
                    cafile=settings.PIKA_SSL_CERT.get('ssl_options').get('ca_certs')
                )
            context.load_cert_chain(
                    settings.PIKA_SSL_CERT.get('ssl_options').get('certfile'),
                    settings.PIKA_SSL_CERT.get('ssl_options').get('keyfile'),
                    )
            ssl_options = pika.SSLOptions(context, settings.PIKA_PUSH_MSG_MQ_CLUSTER)


            node = pika.ConnectionParameters(
                host=settings.PIKA_PUSH_MSG_MQ_CLUSTER,
                virtual_host='/',
                heartbeat=300,
                port=5671,
                ssl_options=ssl_options,
                credentials = ExternalCredentials()
            )

            all_endpoints.append(node)
       
        else:
            mq_list = settings.PIKA_PUSH_MSG_MQ_CLUSTER

            for conn in mq_list:
                node = URLParameters(conn)
                all_endpoints.append(node)

        return  all_endpoints


    def __declare_channel(self):
        """

        :return:
        """

        if self.__check_alive():
            return
        else:
            self.__clear()

        
        if not self.conn:
            self.conn = BlockingConnection(self.__conn())

        if not self.channel:
            self.channel = self.conn.channel()
            self.channel.queue_declare(
                queue=self.task_num,
                durable=True
            )

            self.properties = BasicProperties(delivery_mode=2)

    def publish_job_status(self, message):
        """

        :param message:
        :return:
        """
        logger.debug('send mq msg to DPA, the task is completed')

        try:
            self.__declare_channel()

            data = None
            if isinstance(message, dict):
                data = json.dumps(message)

            if isinstance(message, str):
                data = message

            if data:
                self.channel.basic_publish(
                    # exchange=settings.JK_MQ_EXCHANGE,
                    exchange='',
                    routing_key=self.task_num,
                    body=data,
                    properties=self.properties
                )
                success = True
            else:
                success = False

        except Exception as e:
            # print('{} - publish_job_status'.format(__file__))
            # print('ERROR: {}'.format(repr(e)))
            logger.error(repr(e))

            success = False

        return success
    
    # django command 测试函数
    def zili(self):
        return 'zzzzz'

    def _listen_rpa_mq_status(self,callback_func):
        # dpa 发送的消息
        """
        :param message:
        :return:
        """

        self.__declare_channel()

        try:
            # create the auto-delete queue
            self.channel.queue_declare(queue=self.task_num, durable=True)
            # self.channel.basic_qos(prefetch_count=1) #开启客户端最大的未处理消息队列大小为1
            self.channel.basic_consume(
                on_message_callback=callback_func,
                queue=self.task_num,
                # auto_ack=True
            )

            self.channel.start_consuming()

        except Exception as e:
            logger.error(repr(e))
            return repr(e)

    
    def stop_listen_rpa_status(self):
         self.channel.stop_consuming()
         self.channel.queue_delete(self.task_num)  #队列删除

    def __check_alive(self):
        """

        :return:
        """
        return self.channel and self.channel.is_open and self.conn and self.conn.is_open

    def __clear(self):
        """
        :return:
        """
        try:
            if self.conn and self.conn.is_open:
                self.conn.close()
            self.conn = None
            if self.channel and self.channel.is_open:
                self.channel.close()
            self.channel = None
        except Exception as e:
            self.channel = None
            self.conn = None
            # print("WARING: {}".format(repr(e)))
            logger.error(repr(e))

    def __del__(self):
        """

        :return:
        """
        # SSL: not clear
        if not settings.ENABLE_OTHER_MQ_CLUSTER_SSL :
            self.__clear()


if __name__ == '__main__':

    msg_handler = MessageQueueHandle(task_num='command-12312312312')

    message = {'job_num': 'command-12312312312', 'status': 'PENDING'}

    msg_handler.publish_job_status(message=message)
