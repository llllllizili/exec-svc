#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@Time    :   2020/05/31 17:39:54
'''

import os
import json
import time
import logging
from datetime import datetime
import requests
from django.conf import settings
from utils.jklog import jklog
from utils.websocketApi.base import socket_handler
from utils.elasticApi.es import ElasticHandle
from utils.jkaes import jkAes
from .smart_api import SmartApi
from .errorhandle import SmartError

logger = logging.getLogger('console')

class HandleSmart:
    def __init__(self, cmd, job_num, exec_type, exec_async, task_num, node_num, custom_data, kwargs, log_server):
        self.cmd = cmd  # 'cmd.run' cmd.script
        self.job_num = job_num
        self.task_num = task_num
        self.node_num = node_num
        self.custom_data = custom_data
        self.exec_type = exec_type
        self.exec_async = exec_async
        self.log_server = log_server
        self.targets = kwargs.get('targets', '')
        self.runtime_type = kwargs.get('runtime_type', 'shell')
        self.become = kwargs.get('becomes', '')
        self.args = kwargs.get('args', '')
        self.script_args = jkAes().decrypt(kwargs.get('script_args', ''))
        self.file_args = kwargs.get('file_args', '')
        self.hosts = dict()
        self.ip_list = list()
        self.es_handle = ElasticHandle()
        self.smartapi = SmartApi(self.args)

    def checkenv(self):
        if not isinstance(self.targets, list):
            logger.error('targets is Invalid data type')

            return False, 500, dict(status='Failure', result=TypeError('targets is Invalid data type'))

        host_list = self.smartapi.hosts_list()
        code = host_list['code']
        if code:
            logger.debug('/host/list: smartagent server abnormal response error')
            return False, 500, dict(status='Failure', result='/host/list: smartagent server abnormal responsecode: {}'
                                    .format(code))
        for host in host_list['payload']:
            self.hosts[host['ip']] = host['id']

    def exec_status(self, hid, pid):
        status = self.smartapi.cmd_status(hid, pid)
        try:
            result = json.loads(status.text)
            logger.debug('the status is {}'.format(result['payload']['running']))
            logger.debug(result)
            return True, result['payload']['running']
        except Exception as e:
            logger.error(repr(e))
            return False, repr(e)

    def __runcommand(self):
        exec_data = list()
        logs = str()
        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if self.checkenv():
            return self.checkenv()

        for target in self.targets:
            if target['ip'] not in self.hosts:
                logger.error('smartagent not installed on {}'.format(target['ip']))
                exec_data.append(SmartError(error='smartagent not installed on {}'.format(target['ip']),
                                            start_date=start_date, target=target['ip']).reply())
            elif target['ip'] in self.hosts:
                self.ip_list.append(target['ip'])
                if not self.ip_list:
                    logger.debug('os list is null')
                    return False, 500, SmartError(error='os list is null', start_date=start_date,
                                                  target=None).reply()
        if not self.args:
            logger.debug('command is null')
            return False, 500, SmartError(error='command is null', start_date=start_date,
                                          target=None).reply()

        args_list = self.args.strip().replace(',', '%2c%').split(' ')
        if self.runtime_type == 'powershell' and self.become:
            cmd_args = '-ExecutionPolicy,remotesigned,' + ','.join(args_list)
            self.args = 'powershell'
        else:
            self.args = args_list[0]
            del args_list[0]
            cmd_args = ','.join(args_list)

        for ip in self.ip_list:
            results = dict()
            response = self.smartapi.cmd_run(hid=self.hosts[ip], args=self.args, option_args=cmd_args, time_out=900,
                                             become=self.become)
            code = response['code']
            if code:
                err_msg = response['msg']
                err_result = SmartError(error='smartagent server execution failed on {}: {} {}'
                                              .format(ip, code, err_msg),
                                              start_date=start_date, target=ip).reply()
                exec_data.append(err_result)
                logger.debug('smartagent server execution failed on {}: {} {}'.format(ip, code, err_msg))
            else:
                channel_id = response['payload']['pid']

                while True:
                    success, running_status = self.exec_status(self.hosts[ip], response['payload']['pid'])
                    logger.debug('current running_status is {}'.format(running_status))
                    
                    if success:
                        if not running_status:
                            break
                        else:
                            logger.debug('the status of smartagent is Flase,wait smartagent')
                    time.sleep(2)
                    
                pty_result = self.smartapi.cmd_pty(agent_id=self.hosts[ip], channel_id=channel_id)

                results['start_date'] = start_date
                results['target'] = ip
                results['status'] = 'SUCCESS'
                results['result'] = pty_result
                results['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log = '[{}: {} INFO/{}] {}\n'.format(start_date, ip, self.exec_type, pty_result)
                logs += log

            exec_data.append(results)
        if self.exec_async != 0 and self.log_server == 1:
            for data in exec_data:
                self.es_handle.send_result(job_num=self.job_num, result=data, log=logs)

        if self.task_num and self.exec_async != 0:
            if 'jkws' in self.task_num:
                socket_handler(task_num=self.task_num,
                               job_num=self.job_num,
                               node_num=self.node_num,
                               custom_data=self.custom_data,
                               status='SUCCESS',
                               log=logs)

        logger.debug(exec_data)

        return True, 200, exec_data

    def __check_script(self):
        # special_chart = ';&|'

        # for i in special_chart:
        #     if i in self.script_args:
        #         return False
        return True

    def __runscript(self, **kwargs):
        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exec_data = list()
        logs = str()
        if self.checkenv():
            return self.checkenv()
        for target in self.targets:
            if target['ip'] not in self.hosts:
                logger.error('smartagent not installed on {}'.format(target['ip']))
                exec_data.append(SmartError(error='smartagent not installed on {}'.format(target['ip']),
                                            start_date=start_date, target=target['ip']).reply())
            elif target['ip'] in self.hosts:
                self.ip_list.append(target['ip'])
                if not self.ip_list:
                    logger.debug('os list is null')
                    return False, 500, SmartError(error='{}'.format('os list is null'), start_date=start_date,
                                                  target=None).reply()

        if not self.args:
            logger.debug('command is null')
            return False, 500, SmartError(error='command is null', start_date=start_date,
                                          target=None).reply()

        if self.script_args:
            if not self.__check_script():
                return False, 500, 'Illegal args Exists in the script arguments'
            script_args = ','.join(self.script_args.strip().replace(',', '%2c%').split(' '))
        else:
            script_args = ''

        if '__jk_script_' in self.args:
            _script_filename = self.args
        else:
            _script_filename = self.args.split('/')[-1]

        if '?' in _script_filename:
            _script_filename = _script_filename.split('?')[0]

        _script_type = _script_filename.split('.')[-1]

        if 'ps1' in _script_type:
            shell_cmd = 'powershell'
            shell_path = settings.SMART_AGENT_SCRIPT_PATH_WINDOWS
            if self.become:
                script_args = '-ExecutionPolicy,remotesigned,' + shell_path + _script_filename + ',' + script_args
            else:
                script_args = shell_path + _script_filename + ',' + script_args
        elif 'bat' in _script_type:
            shell_path = settings.SMART_AGENT_SCRIPT_PATH_WINDOWS
            shell_cmd = shell_path + _script_filename
        else:
            shell_path = settings.SMART_AGENT_SCRIPT_PATH_LINUX
            shell_cmd = shell_path + _script_filename

        logger.debug('script name is {}, _script_type  is {}'.format(_script_filename, _script_type))

        success, code, result = self.__file_distribute()
        if not success:
            return False, code, result

        for ip in self.ip_list:
            results = dict()
            response = self.smartapi.cmd_run(self.hosts[ip], shell_cmd, script_args, 900, self.become)
            logger.debug(response)

            if response['code']:
                err_msg = response['msg']
                err_result = SmartError(error='smartagent server execution failed on {}: {} {}'
                                        .format(ip, code, err_msg),
                                        start_date=start_date, target=ip).reply()
                exec_data.append(err_result)
                logger.debug('/cmd/run: smartagent server execution failed on {}: {}'.format(ip, err_msg))
            else:
                channel_id = response['payload']['pid']
                while True:
                    success, running_status = self.exec_status(self.hosts[ip], response['payload']['pid'])
                    logger.debug('current running_status is {}'.format(running_status))

                    if success:
                        if not running_status:
                            break
                        else:
                            logger.debug('the status of smartagent is Flase,wait smartagent')
                    time.sleep(2)
                
                pty_result = self.smartapi.cmd_pty(agent_id=self.hosts[ip], channel_id=channel_id)

                results['start_date'] = start_date
                results['target'] = ip
                results['status'] = 'SUCCESS'
                results['result'] = [pty_result]
                results['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                exec_data.append(results)
                log = '[{}: {} INFO/{}] {}\n'.format(start_date, ip, self.exec_type, pty_result)
                logs += log

            if 'ps1' in _script_type or 'bat' in _script_type:
                self.smartapi.cmd_run(self.hosts[ip], 'powershell', 'Remove-Item' + shell_path + _script_filename,
                                      900, become=self.become)

        if self.exec_async != 0 and self.log_server == 1:
            for data in exec_data:
                self.es_handle.send_result(job_num=self.job_num, result=data, log=logs)

        if self.task_num and self.exec_async != 0:
            if 'jkws' in self.task_num:
                socket_handler(task_num=self.task_num,
                               job_num=self.job_num,
                               node_num=self.node_num,
                               custom_data=self.custom_data,
                               status='SUCCESS',
                               log=logs)

        logger.debug('{} exec success '.format(self.targets))
        logger.debug('{}'.format(exec_data))

        return True, 200, exec_data

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

            logger.debug('{} - __download_file success'.format(filename))

            return filename

        except Exception as e:
            logger.error(repr(e))
            return repr(e)

    def __file_distribute(self):
        exec_data = list()
        logs = str()
        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.cmd == 'file.distribute':
            if self.checkenv():
                return self.checkenv()
            for target in self.targets:
                if target['ip'] not in self.hosts:
                    logger.error('smartagent not installed on {}'.format(target['ip']))
                    exec_data.append(SmartError(error='smartagent not installed on {}'.format(target['ip']),
                                                start_date=start_date, target=target['ip']).reply())
                elif target['ip'] in self.hosts:
                    self.ip_list.append(target['ip'])
                    if not self.ip_list:
                        logger.error('os list is null')
                        return False, 500, SmartError(error='{}'.format('os list is null'), start_date=start_date,
                                                  target=None).reply()

        if '__jk_script_' in self.args:
            _script_file = '{}/{}'.format(settings.ANSIBLE_PRIVATE_SCRIPT_PATH, self.args)
        else:
            _script_file = self.__download_file()
            if not os.path.exists(_script_file):
                return False, 500, SmartError(error='{}'.format('script file not exists'), start_date=start_date,
                                                  target=None).reply()

        _script_filename = _script_file.split('/')[-1]
        _script_type = _script_filename.split('.')[-1]

        if 'ps1' in _script_type or 'bat' in _script_type and self.file_args == '':
            shell_path = settings.SMART_AGENT_SCRIPT_PATH_WINDOWS
        elif 'sh' in _script_type or 'py' in _script_type and self.file_args == '':
            shell_path = settings.SMART_AGENT_SCRIPT_PATH_LINUX
        else:
            shell_path = self.file_args


        for ip in self.ip_list:
            with open(_script_file, 'rb') as f:
                files = {'file': f}
                results = dict()
                if self.become and 'sh' in _script_type:
                    payload = {
                        'id': self.hosts[ip],
                        'dir': shell_path,
                        'mod': '511',
                        'auth': self.become.get('method'),
                        'user': self.become.get('username'),
                        'pass': jkAes().decrypt(self.become.get('password'))
                    }
                else:
                    payload = {'id': self.hosts[ip], 'dir': shell_path, 'mod': '511'}

                response = self.smartapi.file_upload(payload, files)
                response = json.loads(response.text)
                code = response['code']
                if code:
                    msg = response['msg']
                    logger.error('/file/upload: smartagent server distribution failed on {}: {}'.format(ip, msg))
                    exec_data.append(SmartError(error='/file/upload: smartagent server distribution failed on {}: {}'
                                                .format(ip, msg), start_date=start_date, target=ip).reply())
                results['start_date'] = start_date
                results['target'] = ip
                results['status'] = 'SUCCESS'
                results['result'] = 'File {} uploaded to {}'.format(_script_filename, shell_path)
                results['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                exec_data.append(results)

                log = '[{}: {} INFO/{}] {}\n'.format(start_date, ip, self.exec_type, response)
                logs += log

        if self.exec_async != 0 and self.cmd == 'file.distribute' and self.log_server == 1:
            for data in exec_data:
                self.es_handle.send_result(job_num=self.job_num, result=data, log=logs)
        #if self.exec_async == 0:
        #    return True, 200, exec_data

        if self.task_num and self.exec_async != 0:
            if 'jkws' in self.task_num:
                socket_handler(task_num=self.task_num,
                               job_num=self.job_num,
                               node_num=self.node_num,
                               custom_data=self.custom_data,
                               status='SUCCESS',
                               log=logs)

        logger.debug('{} exec success '.format(self.ip_list))
        logger.debug('{}'.format(exec_data))

        return True, 200, exec_data

    def __get_sys_info(self):
        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.checkenv():
            return self.checkenv()
        exec_data = list()
        for target in self.targets:
            if target['ip'] not in self.hosts:
                logger.error('smartagent not installed on {}'.format(target['ip']))
                exec_data.append(SmartError(error='smartagent not installed on {}'.format(target['ip']),
                                            start_date=start_date, target=target['ip']).reply())
            elif target['ip'] in self.hosts:
                self.ip_list.append(target['ip'])
        for ip in self.ip_list:
            results = dict()
            sys_info = self.smartapi.sys_info(self.hosts[ip])
            # conn_info = self.smartapi.connection_info(self.hosts[ip])
            # process_info = self.smartapi.process_info(self.hosts[ip])
            sys_code = sys_info['code']

            #conn_code = conn_info['code']
            #process_code = process_info['code']

            if sys_code:
                msg = sys_info['msg']
                exec_data.append(SmartError(error='can not get system info on''{}: {}'.format(ip, msg),
                                           start_date=start_date, target=ip).reply())
            '''
            if conn_code:
                msg = conn_info['msg']
                exec_data.append(SmartError(error='can not get conn info on''{}: {}'.format(ip, msg),
                                            start_date=start_date, target=ip).reply())
            if process_code:
                msg = process_info['msg']
                exec_data.append(SmartError(error='can not get process info on''{}: {}'.format(ip, msg),
                                            start_date=start_date, target=ip).reply())
            '''
            if self.args == '':
                result = [{
                    "osfinger": sys_info['payload']['platform'],
                    "ip_interfaces": sys_info['payload']['intfs']
                }]
                results['date'] = start_date
                results['target'] = ip
                results['status'] = 'SUCCESS'
                results['result'] = result
            '''
            elif self.args == 'info':
                result = sys_info['payload']
                results['result'] = result
            elif self.args == 'conn':
                result = conn_info['payload']
                results['result'] = result
            elif self.args == 'process':
                result = process_info['payload']
                results['result'] = result
            else:
                return False, 400, 'illegal args'
            results['date'] = start_date
            results['target'] = ip
            results['status'] = 'SUCCESS'            
            '''
            exec_data.append(results)

        logger.debug(exec_data)
        return True, 200, exec_data


    def execute(self):
        if self.cmd == 'file.distribute':
            return self.__file_distribute()
        elif self.cmd == 'cmd.script':
            return self.__runscript()
        elif self.cmd == 'cmd.run':
            return self.__runcommand()
        elif self.cmd == 'cmd.getosinfo':
            return self.__get_sys_info()
        else:
            return False, 400, 'smartagent does not support this exec.main: {}'.format(self.cmd)