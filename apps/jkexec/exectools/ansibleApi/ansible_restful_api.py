#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   ansible_restful_api.py
@Time    :   2020/05/29 16:41:59
'''


import os
import platform
import requests
import logging
from .ans import RemoteApi
from utils.jklog import jklog
from utils.jkaes import jkAes
from django.conf import settings


logger = logging.getLogger('console')

class AnsibleHandle(object):

    def __init__(self, func, job_num, exec_type, exec_async,kwargs,become=None,task_num=None,node_num=None,custom_data=None,log_server=None):
        """

        :param kwargs:
        """
        self.func = func

        self.job_num = job_num

        self.exec_type = exec_type
        self.exec_async = exec_async

        self.task_num = task_num
        self.node_num = node_num
        self.custom_data = custom_data
        self.log_server = log_server

        self.targets = kwargs.get('targets', '')


        self.time_out = kwargs.get('timeout', 10)

        self.args = kwargs.get('args')

        self.kwarg = kwargs.get('kwarg')
        
        if kwargs.get('script_args',''):
            self.script_args = jkAes().decrypt(kwargs.get('script_args'))
        else:
            self.script_args = ''

        self.file_args = kwargs.get('file_args','/tmp/')

        self.become = kwargs.get('become')
        

        if not self.become:
            self.become=dict()

        if not isinstance(self.targets, list):
            raise TypeError('targets is Invalid data type')

        self.resource = []
        self.hosts = []

        for target in self.targets:
            self.resource.append({
                'hostname': target.get('ip'),
                'ansible_user': target.get('username'),
                'ansible_ssh_pass': jkAes().decrypt(target.get('password')),
                'ansible_port': target.get('port'),
                'ansible_become_pass': jkAes().decrypt(self.become.get('password'))
            })
            
            self.hosts.append(target.get('ip'))

    def __command(self, cmd):
        """

        :param cmd:
        :return:
        """
        if self.resource:
            try:
                _run = RemoteApi(
                    resource=self.resource,
                    become=self.become,
                    )

                _run_data = _run.run(
                    host_list=self.hosts,
                    module_name=self.func,
                    job_num=self.job_num,
                    module_args=cmd,
                    task_num=self.task_num,
                    node_num=self.node_num,
                    custom_data=self.custom_data,
                    log_server=self.log_server,
                    exec_async=self.exec_async
                )
                
                logger.debug('command is {}'.format(cmd))


                if _run_data != 0:
                    result = _run.get_result()
                    return True, 400, result

                logger.debug('{} exec success '.format(self.targets))
                
                result = _run.get_result()

                return True, 200, result

            except Exception as e:
                logger.error(repr(e))
                return False, 500, repr(e)

    def __download_file(self):

        try:
            # if not os.path.exists(settings.ANSIBLE_SCRIPT_PATH):
            #     os.makedirs(settings.ANSIBLE_SCRIPT_PATH)

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

    def __script(self):
        # 本地内置脚本or远程服务器脚本
        if '__jk_script_' in self.args:
            _script_filename = '{}/{}'.format(settings.ANSIBLE_PRIVATE_SCRIPT_PATH, self.args)
        else:
            _script_filename = self.__download_file()

        if not _script_filename:
            return False, 500, 'script file not exists'

        logger.debug('script path is {}'.format(_script_filename))


        module_args = _script_filename
        
        if self.script_args:

            if not self.__check_script():
                return False, 500, 'Illegal args Exists in the script'

            # module_args = '{} {}'.format(_script_filename, self.script_args)
            # dsp脚本参数含等号，参数丢失处理
            module_args = '{} {}'.format(_script_filename, self.script_args.replace('=','\='))

        if self.resource:
            try:
                _run = RemoteApi(resource=self.resource, become=self.become, timeout=self.time_out)

                _run_data = _run.run(
                    host_list=self.hosts,
                    module_name=self.func,
                    job_num=self.job_num,
                    module_args=module_args,
                    task_num=self.task_num,
                    node_num=self.node_num,
                    custom_data=self.custom_data,
                    log_server=self.log_server,
                    exec_async=self.exec_async
                )

                if _run_data != 0:
                    result = _run.get_result()
                    return True, 400, result
                    
                result = _run.get_result()

                return True, 200, result
                    
            except Exception as e:
                logger.error(repr(e))
                return False, 500, repr(e)

    def __file_distribute(self):

        filename = self.__download_file()

        module_args = 'src={} dest={}'.format(filename, self.file_args)

        if self.resource:
            try:
                _run = RemoteApi(resource=self.resource, become=self.become, timeout=self.time_out)

                _run_data = _run.run(
                    host_list=self.hosts,
                    module_name=self.func,
                    job_num=self.job_num,
                    module_args=module_args,
                    task_num=self.task_num,
                    node_num=self.node_num,
                    custom_data=self.custom_data,
                    log_server=self.log_server,
                    exec_async=self.exec_async
                )
                
                if _run_data != 0:
                    result = _run.get_result()
                    return True, 400, result
                    
                result = _run.get_result()

                return True, 200, result    
                 
            except Exception as e:
                logger.error(repr(e))
                return False, 500, repr(e)

    def execute(self):
        if self.func == 'cmd.run':
            return self.__command(cmd=self.args)
        if self.func == 'cmd.script':
            return self.__script()
        if self.func == 'file.distribute':
            return self.__file_distribute()


