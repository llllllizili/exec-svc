#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   salt.py
@Time    :   2020/05/31 17:39:54
'''

import os
import json
import requests
import salt.config
import salt.client
import salt.wheel
import logging
from django.conf import settings
from datetime import datetime
from utils.jklog import jklog
from utils.websocketApi.base import socket_handler
from utils.elasticApi.es import ElasticHandle
from utils.jkaes import jkAes

logger = logging.getLogger('console')


def check_json_format(data):
    if isinstance(data, str):
        try:
            res = json.loads(data.replace('\r\n', ''), encoding='utf-8')
            return True, res
        except ValueError:
            logger.error(data)
            return False, data
    else:
        return False, data


class jkServerError(Exception):
    pass


class SaltHandle():
    def __init__(self, func, job_num, exec_type, exec_async, task_num, node_num, custom_data, kwargs, log_server):
        '''
        :param hostid:
        :param type  cmd, script,scp_file,fetch_file:
        :param kwargs:
        '''

        self.func = func  # 'cmd.run' cmd.script
        self.job_num = job_num
        self.task_num = task_num
        self.node_num = node_num
        self.custom_data = custom_data
        self.exec_type = exec_type
        self.exec_async = exec_async
        self.log_server = log_server
        self.targets = kwargs.get('targets', '')
        self.time_out = kwargs.get('timeout', 60)
        self.runtime_type = kwargs.get('runtime_type', 'bat')
        self.args = kwargs.get('args')
        # self.script_args = jkAes().decrypt(kwargs.get('script_args'))
        if kwargs.get('script_args', ''):
            self.script_args = jkAes().decrypt(kwargs.get('script_args'))
        else:
            self.script_args = ''
        self.file_args = kwargs.get('file_args', '/tmp/')

        self.ip_list = list()
        self.ip_no_agent_list = list()
        self.es_handle = ElasticHandle()

        if not isinstance(self.targets, list):
            logger.error('targets is Invalid data type')
            raise TypeError('targets is Invalid data type')

        opts = salt.config.master_config(settings.SALT_MASTER_CONFIG)
        wheel = salt.wheel.WheelClient(opts)
        minions = wheel.cmd('key.list', ['accepted'])

        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for target in self.targets:
            if target['ip'] not in minions['minions']:
                logger.warning('{} not install agent'.format(target['ip']))
                self.ip_no_agent_list.append(target['ip'])
            else:
                self.ip_list.append(target['ip'])

    def __command(self, **kwargs):
        data = list()
        logs = str()
        if not self.args:
            logger.error('command is null')
            raise jkServerError('{}'.format('command is null'))
        if not self.ip_list:
            logger.error('os list is null')
            raise jkServerError('{}'.format('os list is null'))

        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        local = salt.client.LocalClient()
        cmd_result = local.cmd(','.join(self.ip_list), self.func, [self.args], tgt_type='list', timeout=self.time_out)


        for key in cmd_result:
            # if not [cmd_result[key]] or isinstance([cmd_result[key]], str) or [cmd_result[key]['retcode']] != 0:
            if not [cmd_result[key]] or isinstance([cmd_result[key]], str) != 0:
                res_dict = dict(target=key,
                                start_date=start_date,
                                status='FAILURE',
                                result=[cmd_result[key]],
                                end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                log = '[{}: {} ERROR/{}] {}\n'.format(start_date, key, self.exec_type, cmd_result[key])
            else:
                results = dict()
                results['start_date'] = start_date
                results['target'] = key
                results['status'] = 'SUCCESS'
                results['result'] = [cmd_result[key]]
                results['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                log = '[{}: {} INFO/{}] {}\n'.format(start_date, key, self.exec_type, cmd_result[key])

            logs += log
            data.append(results)
            if self.exec_async != 0:
                if self.log_server == 1:
                    self.es_handle.send_result(job_num=self.job_num, result=results, log=logs)

        for key in self.ip_no_agent_list:
            results = dict()
            results['start_date'] = start_date
            results['target'] = key
            results['status'] = 'FAILURE'
            results['result'] = '%s not install agent' % key
            results['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            log = '[{}: {} ERROR/{}] {}\n'.format(start_date, key, self.exec_type, '%s not install agent' % key)
            logs += log
            data.append(results)
            if self.exec_async != 0:
                if self.log_server == 1:
                    self.es_handle.send_result(job_num=self.job_num, result=results, log=logs)

        # if self.exec_async == 0:
        #     return True, 200, data

        # if data:
        #     self.es_handle.send_result(job_num=self.job_num, result=data, log=logs)

        logger.debug('{} exec success '.format(self.targets))
        logger.debug('{}'.format(data))

        return True, 200, data

    def __download_file(self):

        try:

            filename = '{}/{}'.format(settings.ANSIBLE_SCRIPT_PATH, self.args.split('/')[-1])
            if '?' in filename:
                filename = filename.split('?')[0]

            with requests.get(url=self.args, stream=True) as r:
                r.raise_for_status()
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)

            if not os.path.exists(filename):
                return None

            logger.debug('{} - __download_file success'.format(filename))

            return filename

        except Exception as e:
            logger.error(repr(e))
            return None

    def __check_script(self):
        # special_chart = ';&|'

        # for i in special_chart:
        #     if i in self.script_args:
        #         return False

        return True

    def __script(self, **kwargs):
        if not self.args:
            logger.error('script name is null')
            raise jkServerError('{}'.format('script name is null'))
        if not self.ip_list:
            logger.error('os list is null')
            raise jkServerError('{}'.format('os list is null'))

        if self.script_args:
            if not self.__check_script():
                return False, 500, 'Illegal args Exists in the script'

        if '__jk_script_' in self.args:
            _script_filename = self.args
        else:
            _script_filename = self.__download_file().split('/')[-1]

        if not _script_filename:
            return False, 500, 'script file not exists'

        _script_type = _script_filename.split('.')[-1]

        if 'bat' in _script_type:
            shell = 'bat'
        elif 'ps1' in _script_type:
            shell = 'powershell'
        elif 'sh' in _script_type:
            shell = '/bin/bash'
        else:
            shell = ''

        if shell:
            local_cmd = ['salt://' + _script_filename, self.script_args, 'shell=' + shell]
        if not shell:
            local_cmd = ['salt://' + _script_filename, self.script_args]

        logger.debug('script name is {}, type is {}'.format(_script_filename, shell))

        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        local = salt.client.LocalClient()
        script_result = local.cmd(','.join(self.ip_list), self.func, local_cmd, tgt_type='list', timeout=self.time_out)

        data_list = list()
        logs = str()
        # jklog('debug', ">>>______________________-salt -_-script  result")
        # jklog('debug',type(script_result))
        # jklog('debug', script_result)
        for target, res in script_result.items():

            # if not res:  # {'xxx.xxx.xxx.xxx': False}
            #     return False, 500, '{} - salt exec failure (timeout)'.format(res)

            if not res or isinstance(res, str) or res['retcode'] != 0:
                res_dict = dict(target=target,
                                start_date=start_date,
                                status='FAILURE',
                                result=[res],
                                end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                log = '[{}: {} ERROR/{}] {}\n'.format(start_date, target, self.exec_type, res)
            else:
                json_check, result = check_json_format(res['stdout'])
                res_dict = dict(target=target,
                                start_date=start_date,
                                status='SUCCESS',
                                result=[result],
                                end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                log = '[{}: {} INFO/{}\n] {}\n'.format(start_date, target, self.exec_type, result)

            logs += log
            data_list.append(res_dict)
            if self.exec_async != 0:
                if self.log_server == 1:
                    self.es_handle.send_result(job_num=self.job_num, result=res_dict, log=logs)

        for key in self.ip_no_agent_list:
            results = dict()
            results['start_date'] = start_date
            results['target'] = key
            results['status'] = 'FAILURE'
            results['result'] = '%s not install agent' % key
            results['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            log = '[{}: {} ERROR/{}] {}\n'.format(start_date, key, self.exec_type, '%s not install agent' % key)
            logs += log
            data_list.append(results)
            if self.exec_async != 0:
                if self.log_server == 1:
                    self.es_handle.send_result(job_num=self.job_num, result=results, log=logs)

        # if self.exec_async == 0:
        #     return True, 200, data_list

        # if data_list:
        #     self.es_handle.send_result(job_num=self.job_num, result=data_list, log=logs)

        logger.debug(data_list)

        return True, 200, data_list 

    def __local_module_run(self, **kwargs):

        local = salt.client.LocalClient()

        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        local_module_result = local.cmd(','.join(self.ip_list), self.func, self.args, tgt_type='list', timeout=self.time_out)

        # jklog('debug', local_module_result)

        data_list = list()
        logs = str()
        for target, res in local_module_result.items():
            if not res or isinstance(res, str):
                res_dict = dict(target=target,
                                start_date=start_date,
                                status='FAILURE',
                                result=[res],
                                end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                log = '[{}: {} ERROR/{}] {}\n'.format(start_date, target, self.exec_type, res)
            else:
                json_check, result = check_json_format(res)
                res_dict = dict(target=target,
                                start_date=start_date,
                                status='SUCCESS',
                                result=[result],
                                end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

                log = '[{}: {} INFO/{}] {}\n'.format(start_date, target, self.exec_type, result)

            logs += log
            data_list.append(res_dict)
            if self.exec_async != 0:
                if self.log_server == 1:
                    self.es_handle.send_result(job_num=self.job_num, result=res_dict, log=logs)

        for key in self.ip_no_agent_list:
            results = dict()
            results['start_date'] = start_date
            results['target'] = key
            results['status'] = 'FAILURE'
            results['result'] = '%s not install agent' % key
            results['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            log = '[{}: {} ERROR/{}] {}\n'.format(start_date, key, self.exec_type, '%s not install agent' % key)
            logs += log
            data_list.append(results)

            if self.exec_async != 0:
                if self.log_server == 1:
                    self.es_handle.send_result(job_num=self.job_num, result=results, log=logs)

        # if self.exec_async == 0:
        #     return True, 200, data_list

        # if data_list:
        #     self.es_handle.send_result(job_num=self.job_num, result=data_list, log=logs)

        return True, 200, data_list

    def __file_distribute(self):

        filename = self.__download_file()

        source_file = filename.split('/')[-1]

        local = salt.client.LocalClient()

        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        module_args = ['salt://' + source_file, self.file_args, 'makedirs=True']
        

        _result = local.cmd(','.join(self.ip_list),'cp.get_file',module_args, tgt_type='list')
        
        data_list = list()
        logs = str()

        for target, res in _result.items():

            # if not res or isinstance(res, str) or res['retcode'] != 0:
            # if not res:
            #     res_dict = dict(target=target,
            #                     start_date=start_date,
            #                     status='FAILURE',
            #                     result=[res],
            #                     end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            #     log = '[{}: {} ERROR/{}] {}\n'.format(start_date, target, self.exec_type, res)
            # else:
            json_check, result = check_json_format(res)
            res_dict = dict(target=target,
                            start_date=start_date,
                            status='SUCCESS',
                            result=[result],
                            end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            log = '[{}: {} INFO/{}] {}\n'.format(start_date, target, self.exec_type, result)

            logs += log

            data_list.append(res_dict)

            if self.exec_async != 0:
                if self.log_server == 1:
                    self.es_handle.send_result(job_num=self.job_num, result=res_dict, log=logs)

        for key in self.ip_no_agent_list:
            results = dict()
            results['start_date'] = start_date
            results['target'] = key
            results['status'] = 'FAILURE'
            results['result'] = '%s not install agent' % key
            results['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            log = '[{}: {} ERROR/{}] {}\n'.format(start_date, key, self.exec_type, '%s not install agent' % key)
            logs += log
            data_list.append(results)

            if self.exec_async != 0:
                if self.log_server == 1:
                    self.es_handle.send_result(job_num=self.job_num, result=results, log=logs)

        # if self.exec_async == 0:
        #     return True, 200, data_list

        # if data_list:
        #     self.es_handle.send_result(job_num=self.job_num, result=data_list, log=logs)

        return True, 200, data_list

    def execute(self):
        if self.func == 'cmd.run':
            return self.__command(cmd=self.args)
        elif self.func == 'cmd.script':
            return self.__script()
        elif self.func == 'file.distribute':
            return self.__file_distribute()
        else:
            return self.__local_module_run()
