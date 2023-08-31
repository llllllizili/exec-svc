#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   command.py
@Time    :   2020/05/29 16:42:26
'''

import shlex
import subprocess
from datetime import datetime
from utils.elasticApi.es import ElasticHandle
# from utils.websocketApi.base import WebSocketHandle


def except_handler(es, job_num, log, task_num=None):
    if not es:
        es = ElasticHandle()
    es.send_log(job_num=job_num, log=log)


def command(job_num, kwargs, exec_async, log_server, is_shell=False, task_num=None, node_num=None, custom_data=None):

    data = list()
    cmd = kwargs.get('args', '')
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if exec_async != 0:
        if log_server == 1:
            log = '[{}: INFO/command] {}'.format(current_date, cmd)
            es_handle = ElasticHandle()
            es_handle.send_log(job_num=job_num, log=log)

    if not is_shell:
        cmd = shlex.split(cmd)

    results = dict()
    results['start_date'] = current_date
    results['target'] = '127.0.0.1'

    try:
        command_log = ''
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=is_shell)

        while True:

            buff = proc.stdout.readline()
            try:
                command_received = buff.decode('utf-8')
            except UnicodeDecodeError as e:
                command_received = buff.decode('gb2312')

            # log += command_received
            # es_handle.send_log(job_num=job_num, log=command_received.strip('\n'))

            command_log += command_received

            if command_received == '' and proc.poll() is not None:
                break

        results['status'] = 'SUCCESS'
        results['result'] = command_log.strip('\n')
        results['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if exec_async != 0 and log_server == 1:
            es_handle.send_result(job_num=job_num, result=results, log=command_log.strip('\n'))

        if proc.returncode != 0:
            return False, 500, command_log
        else:
            return True, 200, results

    except subprocess.CalledProcessError as e:
        # es_handle.send_log(job_num=job_num, log=repr(e))
        if exec_async != 0:
            if log_server == 1:
                except_handler(job_num=job_num, es=es_handle, task_num=task_num, log=repr(e))
            return False, 500, repr(e)
        return False, 500, repr(e)
    except FileNotFoundError as e:
        # es_handle.send_log(job_num=job_num, log=repr(e))
        if exec_async != 0:
            if log_server == 1:
                except_handler(job_num=job_num, es=es_handle, task_num=task_num, log=repr(e))
            return False, 500, repr(e)
        return False, 500, repr(e)
    except Exception as e:
        # es_handle.send_log(job_num=job_num, log=repr(e))
        if exec_async != 0:
            if log_server == 1:
                except_handler(job_num=job_num, es=es_handle, task_num=task_num, log=repr(e))
            return False, 500, repr(e)
        return False, 500, repr(e)
