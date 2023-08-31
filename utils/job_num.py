#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   job_num.py
@Time    :   2020/05/29 16:47:47
'''


import time
import logging

logger = logging.getLogger('console')


def generate_exec_num(exec_type):
    """

    :return: exec_task_num
    """

    try:
        job_num = '{}-{}{}'.format(exec_type, str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))),
                                  str(time.time()).replace('.', '')[-7:])
    except Exception as e:
        logger.error(repr(e))
        return None

    return job_num