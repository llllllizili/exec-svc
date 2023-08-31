#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   jkredis.py
@Time    :   2020/07/20 21:47:04
'''

import redis

from django.conf import settings


class ResiHandle(object):

    def __init__(self,**kwargs):

        self.conn = None

    def __declare_connect(self):
        if not self.conn:
            try:
                pool = redis.ConnectionPool(
                    host=settings.JK_REDIS_HOST,
                    port=settings.JK_REDIS_PORT,
                    password=settings.JK_REDIS_PASSWORD,
                    db='11',
                    socket_connect_timeout=3,
                    decode_responses=True
                )
                self.conn = redis.Redis(connection_pool=pool)
                
                return True, 'CONNECT SUCCESS'

            except Exception as ex:
                print(repr(ex))
                return False, repr(ex)
        else:
            return True, 'CONNECT SUCCESS'

    
    def get_msg(self,key):

        status,res = self.__declare_connect()

        if status:
            data = self.conn.get(key)
            # print(data)
            # if not data:
            #     self.conn.set(key,1)

            return True, data
        else:
            return False, 'CONNECT FAILED'

    def incr_msg(self,key):

        status,res = self.__declare_connect()

        if status:
            self.conn.incr(key, amount=1)

            return True, 'Increasing SUCCESS'
            
        else:
            return False, 'Increasing FAILED'


# if __name__ == "__main__":
#     ResiHandle(key='192.168.1.1').get_msg()