#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   jktask.py
@Time    :   2020/05/31 10:50:57
'''

import datetime
import json
import os
import django
import logging
from django.conf import settings
from celery import Celery, Task, platforms, states
from celery.exceptions import TaskError
from celery.signals import task_prerun

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jksreExecEngine.settings')
django.setup()
from jkexec.exectools.restful_api import HttpHandle
from jkexec.exectools.command import command
from jkexec.exectools.saltstackApi.jksalt import SaltHandle
from jkexec.exectools.rabbitmqMsgApi.jkrabbitmqmsg import RabbitmqMsgHandle
from jkexec.exectools.ansibleApi.ansible_restful_api import AnsibleHandle
from jkexec.exectools.smartagentApi.handlesmart import HandleSmart
from jkexec.exectools.rpaApi.jk_rpa_mq import RpaMQHandle
from utils.jklog import jklog
from utils.jkaes import jkAes
from utils.elasticApi.es import ElasticHandle, get_status
from utils.rabbitmqApi.mq import MessageQueueHandle
from utils.websocketApi.base import WebSocketHandle
from utils.redisApi.jkredis import ResiHandle

from apps.jkhdcollect.jksnmp.collect_api import SnmpDataCollect
from apps.jkhdcollect.jkipmi.ipmicollect import IpmiDataCollect

app = Celery('jksreExecEngine')
app.now = datetime.datetime.now()
app.config_from_object('django.conf:settings')
platforms.C_FORCE_ROOT = True

logger = logging.getLogger('console')

def is_json(data):
    result = None

    try:
        result = json.loads(data)
    except ValueError:
        return False, result
    return True, result


def mq_socket_handle(task_num, job_num, node_num, custom_data, status, log, result=None):
    if isinstance(result, TaskError):
        status = 'FAILURE'
        result = list(result.args)

    if not isinstance(result, list):
        result = [result]

    status_data = {'task_num': task_num, 'job_num': job_num, 'node_num': node_num, 'custom_data': custom_data,
                   'status': status, 'log': log, 'result': result}

    try:
        mq_handler = MessageQueueHandle(task_num=task_num)
        mq_handler.publish_job_status(message=status_data)

    except Exception as e:
        pass


def dispatch_build_cluster(targets):
    index_list = list()
    count_list = list()

    build_cluster = settings.BUILD_CLUSTER

    if len(build_cluster) < 2:
        logger.debug('build node is : {}'.format(build_cluster[0]['ip']))
        return build_cluster
    else:
        redis_conn = ResiHandle()

        for num in range(len(build_cluster)):

            status, count = redis_conn.get_msg(key=build_cluster[num]['ip'])

            if not status:
                logger.warning('connect failed, will use redis default config')

                logger.debug('default build node is : {}'.format(build_cluster[0]['ip']))

                return [build_cluster[0]]  # default host

            if not count:
                count = '0'

            index_list.append(num)

            count_list.append(count)

        if len(index_list) == len(count_list):
            target = build_cluster[index_list[count_list.index(min(count_list))]]

            redis_conn.incr_msg(target['ip'])

            logger.debug('build node is : {}'.format(target['ip']))

            return [target]


@task_prerun.connect()
def task_start(task_id, task, *args, **kwargs):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    job_data = kwargs.get('kwargs').get('job_data')

    job_num = job_data.get('job_num')
    node_num = job_data.get('node_num')
    task_num = job_data.get('task_num')
    custom_data = job_data.get('custom_data')
    exec_type = job_data.get('exec_type')
    log_server = job_data.get('log_server', 1)

    log = '[{}: INFO/{}] Job({}) is STARTED'.format(current_date, exec_type, job_num)

    #  dpa 取值对接mq，日志需传递到结果中
    logs = job_data.get("logs") if job_data.get("logs") else ''
    logs += log + '\n'
    # job_data['logs'] = logs

    if log_server == 1:
        es_handle = ElasticHandle()
        es_handle.update_signal(job_num=job_num, status='STARTED', log=log)

    if task_num:
        mq_socket_handle(task_num=task_num, job_num=job_num, node_num=node_num, custom_data=custom_data,
                         status='STARTED', log=logs)


class MyTask(Task):
    """

    """

    def on_success(self, retval, task_id, args, kwargs):
        """任务成功处理逻辑

        :param retval:
        :param task_id:
        :param args:
        :param kwargs:
        :return:
        """
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        job_data = kwargs.get('job_data')

        job_num = job_data.get('job_num')
        node_num = job_data.get('node_num')
        custom_data = job_data.get('custom_data')
        task_num = job_data.get('task_num')

        exec_type = job_data.get('exec_type')
        log_server = job_data.get('log_server', 1)

        log = '[{}: INFO/{}] Job({}) is SUCCESS'.format(current_date, exec_type, job_num)

        logger.debug(log)

        #  dpa 取值对接mq，日志需传递到结果中
        exec_log = '[{}: INFO/{}] {} '.format(
            current_date,
            job_data.get('exec_option').get('runtime_type'),
            job_data.get('exec_option').get('args'),
            )
        logs = exec_log + '\n' + str(retval) + '\n' + log

        if log_server == 1:
            es_handle = ElasticHandle()
            es_handle.update_signal(job_num=job_num, status='SUCCESS', log=log, result=retval)

            exectool_result_ack = es_handle._get_response(job_num)

            if not exectool_result_ack and task_num:
                log = '[{}: ERROR/{}] Job({}) is FAILURE'.format(current_date, '_get_response', job_num)
                mq_socket_handle(task_num=task_num, job_num=job_num, node_num=node_num, custom_data=custom_data,
                                 status='FAILURE', log=logs, result=retval)

            if exectool_result_ack and task_num:
                mq_socket_handle(task_num=task_num, job_num=job_num, node_num=node_num, custom_data=custom_data,
                                 status='SUCCESS', log=logs, result=retval)
        else:
            mq_socket_handle(task_num=task_num, job_num=job_num, node_num=node_num, custom_data=custom_data,
                             status='SUCCESS', log=logs, result=retval)
        logger.debug('Task exec success')
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败处理逻辑

        :param einfo:
        :param exc:
        :param task_id:
        :param args:
        :param kwargs:
        :return:
        """
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        job_data = kwargs.get('job_data')

        job_num = job_data.get('job_num')
        node_num = job_data.get('node_num')
        custom_data = job_data.get('custom_data')
        task_num = job_data.get('task_num')

        exec_type = job_data.get('exec_type')
        log_server = job_data.get('log_server', 1)

        log = '[{}: ERROR/{}] Job({}) is FAILURE'.format(current_date, exec_type, job_num)

        logger.error(log)

        #  dpa 取值对接mq，日志需传递到结果中
        exec_log = '[{}: INFO/{}] {} '.format(
            current_date,
            job_data.get('exec_option').get('runtime_type'),
            job_data.get('exec_option').get('args'),
            )
        logs = exec_log + '\n' + repr(exc) + '\n' + log

        if log_server == 1:
            es_handle = ElasticHandle()
            es_handle.update_signal(job_num=job_num, status='FAILURE', log=log, result=repr(exc))

            exectool_result_ack = es_handle._get_response(job_num)
            if not exectool_result_ack and task_num:
                log = '[{}: ERROR/{}] Job({}) is FAILURE'.format(current_date, '_get_response', job_num)
                mq_socket_handle(task_num=task_num, job_num=job_num, node_num=node_num, custom_data=custom_data,
                                 status='FAILURE', log=logs, result=exc)
            if exectool_result_ack and task_num:
                mq_socket_handle(task_num=task_num, job_num=job_num, node_num=node_num, custom_data=custom_data,
                                 status='FAILURE', log=logs, result=exc)
        else:
            mq_socket_handle(task_num=task_num, job_num=job_num, node_num=node_num, custom_data=custom_data,
                             status='FAILURE', log=logs, result=exc)
        logger.error('Task exec failure')

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """任务重试处理逻辑

        :param exc:
        :param task_id:
        :param args:
        :param kwargs:
        :param einfo:
        :return:
        """
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        job_data = kwargs.get('job_data')

        job_num = job_data.get('job_num')
        node_num = job_data.get('node_num')
        custom_data = job_data.get('custom_data')
        task_num = job_data.get('task_num')

        exec_type = job_data.get('exec_type')
        log_server = job_data.get('log_server', 1)

        log = '[{}: WARNING/{}] Job({}) is RETRY'.format(current_date, exec_type, job_num)

        logger.warning(log)

        #  dpa 取值对接mq，日志需传递到结果中
        exec_log = '[{}: INFO/{}] {} '.format(
            current_date,
            job_data.get('exec_option').get('runtime_type'),
            job_data.get('exec_option').get('args'),
            )
        logs = exec_log + '\n' + repr(exc) + '\n' + log

        if log_server == 1:
            es_handle = ElasticHandle()
            es_handle.update_signal(job_num=job_num, status='RETRY', log=log)

            exectool_result_ack = es_handle._get_response(job_num)

            if not exectool_result_ack and task_num:
                log = '[{}: ERROR/{}] Job({}) is FAILURE'.format(current_date, '_get_response', job_num)
                mq_socket_handle(task_num=task_num, job_num=job_num, node_num=node_num, custom_data=custom_data,
                                 status='FAILURE', log=logs, result=exc)

            if exectool_result_ack and task_num:
                mq_socket_handle(task_num=task_num, job_num=job_num, node_num=node_num, custom_data=custom_data,
                                 status='RETRY', log=logs, result=exc)
            logger.debug('Retry task ..')

        else:
            mq_socket_handle(task_num=task_num, job_num=job_num, node_num=node_num, custom_data=custom_data,
                             status='FAILURE', log=logs, result=exc)
            logger.error('Task exec failure')


@app.task(bind=True, base=MyTask, queue='exec-task')
def execute(self, *args, **kwargs):
    """
    :param self:
    :param kwargs:
    :return:
    """

    job_data = kwargs.get('job_data')
    exec_type = job_data.get('exec_type')
    exec_main = job_data.get('exec_main')
    job_num = job_data.get('job_num')
    task_num = job_data.get('task_num')
    node_num = job_data.get('node_num')
    custom_data = job_data.get('custom_data')
    exec_async = job_data.get('exec_async')
    log_server = job_data.get('log_server', 1)
    # files = job_data.get('files')

    result = None

    logger.debug(job_data)
    if exec_type == 'api':
        logger.debug("exec type is api")
        exec_option = job_data.get('exec_option')

        url = exec_option.get('url')
        header = exec_option.get('header')
        method = exec_option.get('method')
        timeout = exec_option.get('timeout') if exec_option.get('timeout') else 300
        max_retries = exec_option.get('max_retries') if exec_option.get('max_retries') else 1
        files = exec_option.get('files') if exec_option.get('files') else None

        # API请求的参数Get 及 POST方式都为JSON
        kwarg = exec_option.get('kwarg')

        http_handle = HttpHandle(job_num=job_num, exec_async=exec_async, log_server=log_server)

        success, code, result = http_handle.execute(url=url, method=method, header=header, args=kwarg, files=files,
                                                    timeout=timeout, max_retries=max_retries)

        if not success:
            logger.error(result)
            raise TaskError(result)

        return result

    if exec_type == 'command':
        logger.debug("exec type is command")

        success = False
        exec_option = job_data.get('exec_option')
        become = job_data.get('become')

        location = exec_option.get('location')

        if location == 'local':
            success, code, result = command(job_num=job_num,
                                            task_num=task_num,
                                            node_num=node_num,
                                            custom_data=custom_data,
                                            kwargs=exec_option,
                                            exec_async=exec_async,
                                            log_server=log_server,
                                            is_shell=True)

        if location == 'remote':
            component = exec_option.get('component')
            if component == 'salt':
                logger.debug("component type is salt")

                salt_handle = SaltHandle(kwargs=exec_option,
                                         job_num=job_num,
                                         node_num=node_num,
                                         custom_data=custom_data,
                                         func=exec_main,
                                         exec_async=exec_async,
                                         exec_type=exec_type,
                                         task_num=task_num,
                                         log_server=log_server)
                success, code, result = salt_handle.execute()

            if component == 'ansible':
                logger.debug("component type is ansible")
                # runtime_type = exec_option.get('runtime_type')
                # if runtime_type == 'build':
                #     disp_targets = dispatch_build_cluster(exec_option.get('targets'))[0]
                #     targets = [{
                #         'ip': disp_targets.get('ip'),
                #         'username': disp_targets.get('username'),
                #         'port': disp_targets.get('port'),
                #         'password': jkAes().encrypt(disp_targets.get('password'))
                #     }]

                #     exec_option['targets'] = targets

                an_handle = AnsibleHandle(kwargs=exec_option,
                                          become=become,
                                          job_num=job_num,
                                          node_num=node_num,
                                          custom_data=custom_data,
                                          func=exec_main,
                                          exec_type=exec_type,
                                          exec_async=exec_async,
                                          task_num=task_num,
                                          log_server=log_server)
                success, code, result = an_handle.execute()

            if component == 'smartagent':
                logger.debug("component type is jk smartagent")
                handlesmart = HandleSmart(kwargs=exec_option,
                                          job_num=job_num,
                                          node_num=node_num,
                                          custom_data=custom_data,
                                          cmd=exec_main,
                                          exec_async=exec_async,
                                          exec_type=exec_type,
                                          task_num=task_num,
                                          log_server=log_server)
                success, code, result = handlesmart.execute()

        if not success:
            if log_server == 1:
                es_handle = ElasticHandle()
                es_handle.update_signal(job_num=job_num, status='FAILURE', log=result)
            raise TaskError(result)

        return result

    if exec_type == 'message':
        logger.debug("exec type is message (push mq empty msg)")
        success = False
        exec_option = job_data.get('exec_option')

        component = exec_option.get('component')

        if component == 'rabbitmq':
            rabbitmq_handle = RabbitmqMsgHandle(kwargs=exec_option,
                                                job_num=job_num,
                                                node_num=node_num,
                                                custom_data=custom_data,
                                                func=exec_main,
                                                exec_type=exec_type,
                                                exec_async=exec_async,
                                                task_num=task_num,
                                                log_server=log_server)

            success, code, result = rabbitmq_handle.execute()

        if not success:
            raise TaskError(result)

        return result

    # rap rabbitmq通讯方式
    if exec_type == 'rpa':
        logger.debug("exec type is rpa")
        success = False
        exec_option = job_data.get('exec_option')

        component = exec_option.get('component')

        if component == 'rabbitmq':
            rabbitmq_handle = RpaMQHandle(kwargs=exec_option,
                                          job_num=job_num,
                                          node_num=node_num,
                                          custom_data=custom_data,
                                          func=exec_main,
                                          exec_type=exec_type,
                                          exec_async=exec_async,
                                          task_num=task_num,
                                          log_server=log_server)

            success, code, result = rabbitmq_handle.execute()

        if not success:
            raise TaskError(result)

        return result


def execute_sync(job_data):
    exec_type = job_data.get('exec_type')

    exec_main = job_data.get('exec_main')

    job_num = job_data.get('job_num')

    task_num = job_data.get('task_num')
    node_num = job_data.get('node_num')
    custom_data = job_data.get('custom_data')

    exec_async = job_data.get('exec_async')

    # log_server = job_data.get('log_server', 0)
    log_server = 0

    # files = job_data.get('files')
    code = 500
    result = None

    if exec_type == 'api':
        exec_option = job_data.get('exec_option')

        url = exec_option.get('url')
        header = exec_option.get('header')
        method = exec_option.get('method')
        timeout = exec_option.get('timeout') if exec_option.get('timeout') else 300
        max_retries = exec_option.get('max_retries') if exec_option.get('max_retries') else 1
        files = exec_option.get('files') if exec_option.get('files') else None

        kwarg = exec_option.get('kwarg')

        http_handle = HttpHandle(job_num=job_num, exec_async=exec_async, log_server=log_server)

        success, code, result = http_handle.execute(url=url, method=method, header=header, args=kwarg, files=files,
                                                    timeout=timeout, max_retries=max_retries)

        # if not success:
        #     return success, code, result

        return success, code, result

    if exec_type == 'command':
        success = False
        exec_option = job_data.get('exec_option')
        become = job_data.get('become')
        location = exec_option.get('location')

        if location == 'local':
            success, code, result = command(job_num=job_num,
                                            task_num=task_num,
                                            node_num=node_num,
                                            custom_data=custom_data,
                                            kwargs=exec_option,
                                            exec_async=exec_async,
                                            log_server=log_server,
                                            is_shell=True)

            return success, code, result

        if location == 'remote':
            component = exec_option.get('component')
            if component == 'salt':
                salt_handle = SaltHandle(kwargs=exec_option,
                                         job_num=job_num,
                                         node_num=node_num,
                                         custom_data=custom_data,
                                         func=exec_main,
                                         exec_async=exec_async,
                                         exec_type=exec_type,
                                         log_server=log_server,
                                         task_num=task_num)
                success, code, result = salt_handle.execute()
                return success, code, result

            if component == 'ansible':
                # runtime_type = exec_option.get('runtime_type')
                # if runtime_type == 'build':
                #     disp_targets = dispatch_build_cluster(exec_option.get('targets'))[0]
                #     targets = [{
                #         'ip': disp_targets.get('ip'),
                #         'username': disp_targets.get('username'),
                #         'port': disp_targets.get('port'),
                #         'password': jkAes().encrypt(disp_targets.get('password'))
                #     }]
                #     exec_option['targets'] = targets

                try:
                    an_handle = AnsibleHandle(kwargs=exec_option,
                                              become=become,
                                              job_num=job_num,
                                              node_num=node_num,
                                              custom_data=custom_data,
                                              func=exec_main,
                                              exec_type=exec_type,
                                              exec_async=exec_async,
                                              log_server=log_server,
                                              task_num=task_num)
                    success, code, result = an_handle.execute()
                    return success, code, result
                except Exception as e:
                    return repr(e)

                    # raise TaskError(repr(e))

            if component == 'smartagent':
                handlesmart = HandleSmart(kwargs=exec_option,
                                          job_num=job_num,
                                          node_num=node_num,
                                          custom_data=custom_data,
                                          cmd=exec_main,
                                          exec_async=exec_async,
                                          exec_type=exec_type,
                                          task_num=task_num,
                                          log_server=log_server)
                success, code, result = handlesmart.execute()
                return success, code, result

        if not success:
            return success, code, result

            # raise TaskError(result)

    if exec_type == 'message':
        success = False
        exec_option = job_data.get('exec_option')

        component = exec_option.get('component')

        if component == 'rabbitmq':
            rabbitmq_handle = RabbitmqMsgHandle(kwargs=exec_option,
                                                job_num=job_num,
                                                node_num=node_num,
                                                custom_data=custom_data,
                                                func=exec_main,
                                                exec_type=exec_type,
                                                exec_async=exec_async,
                                                log_server=log_server,
                                                task_num=task_num)

            success, code, result = rabbitmq_handle.execute()

        return success, code, result

    if exec_type == 'rpa':
        success = False
        result = {'msg': '不支持同步请求'}
        return success, 500, result


@app.task(bind=True, base=MyTask, queue='collect-task')
def collect_async(self, *args, **kwargs):
    """
    auth : auth
    job_num : job_num
    """
    auth_data = kwargs.get('job_data')
    log_server = auth_data.get('log_server')
    job_num = auth_data['job_num']
    exec_type = job_num.split('-')[0]

    if exec_type == 'snmp':
        success, result = SnmpDataCollect(
            job_num=auth_data['job_num'],
            brand=auth_data['brand'],
            model=auth_data['model'],
            community=jkAes().decrypt(auth_data['community']) if 'community' in auth_data else None,
            version=auth_data['version'],
            host=auth_data['host'],
            port=auth_data['port'],
            intention=auth_data['intention'],
            user=auth_data['user'] if 'user' in auth_data else None,
            secure_level=auth_data['secure_level'] if 'secure_level' in auth_data else None,
            auth_protocol=auth_data['auth_protocol'] if 'auth_protocol' in auth_data else None,
            auth_passphrase=auth_data['auth_passphrase'] if 'auth_passphrase' in auth_data else None,
            priv_protocol=auth_data['priv_protocol'] if 'priv_protocol' in auth_data else None,
            priv_passphrase=auth_data['priv_passphrase'] if 'priv_passphrase' in auth_data else None,
            log_server=log_server
        ).snmp_handler()
        if not success and log_server == 1:
            es_handle = ElasticHandle()
            es_handle.update_signal(job_num=job_num, status='FAILURE', log=result)
            raise TaskError(result)

        return result
    elif exec_type == 'ipmi':
        success, result = IpmiDataCollect(
            job_num=auth_data['job_num'],
            brand=auth_data['brand'],
            model=auth_data['model'],
            passwd=jkAes().decrypt(auth_data['passwd']),
            user=auth_data['user'],
            host=auth_data['host'],
            port=auth_data['port'],
            log_server=log_server
        ).ipmi_handler()
        if not success and log_server == 1:
            es_handle = ElasticHandle()
            es_handle.update_signal(job_num=job_num, status='FAILURE', log=result)
            raise TaskError(result)
        return result
