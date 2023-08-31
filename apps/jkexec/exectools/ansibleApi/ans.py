#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   ans.py
@Time    :   2020/06/01 13:51:18
'''


import json
import logging
from datetime import datetime
from collections import namedtuple
from utils.jklog import jklog
from utils.elasticApi.es import ElasticHandle
from utils.websocketApi.base import socket_handler
from utils.jkaes import jkAes
from django.conf import settings
from ansible.playbook.play import Play
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.plugins.callback import CallbackBase
from ansible.inventory.manager import InventoryManager
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible import constants as C
C.HOST_KEY_CHECKING = False


logger = logging.getLogger('console')

class MyInventory(InventoryManager):

    def __init__(self, resource, loader, sources=None):
        super(MyInventory, self).__init__(loader=loader, sources=sources)
        self.resource = resource
        self.inventory = InventoryManager(loader=loader, sources=sources)
        self.gen_inventory()
        
    def __add_group(self, hosts, group_name, group_vars=None):
        """
        :param hosts:
        :param group_name:
        :param group_vars:
        :return:
        """
        self.inventory.add_group(group=group_name)

        if group_vars:
            _group = self.inventory.groups().get(group_name, None)

            if _group is None:
                return 'my group is None',

            for key, value in group_vars.items():
                _group.set_variable(key=key, value=value)

        for host in hosts:
            if 'hostname' not in host:
                continue

            hostname = host.get('hostname')
            self.inventory.add_host(host=hostname, group=group_name)

            _host = self.inventory.get_host(hostname)

            for key, value in host.items():
                if key not in ['hostname']:
                    _host.set_variable(key=key, value=value)

    def gen_inventory(self):

        if self.resource is None:
            pass

        if isinstance(self.resource, list):
            self.__add_group(self.resource, settings.ANSIBLE_DEFAULT_GROUP)

        if isinstance(self.resource, dict):
            for g_name, host_vars in self.resource.items():
                self.__add_group(hosts=host_vars.get('hosts'), group_name=g_name, group_vars=host_vars.get('vars'))


class CustomCallback(CallbackBase):

    def __init__(self, job_num, log_server, exec_type, exec_async, raw_args, start_date, task_num=None,node_num=None,custom_data=None):
        super(CustomCallback, self).__init__()
        self.job_num = job_num
        self.task_num = task_num
        self.node_num = node_num
        self.custom_data = custom_data
        self.log_server = log_server
        self.exec_type = exec_type
        self.exec_async = exec_async
        self.raw_args = raw_args
        self.start_date = start_date
        self.es_handle = ElasticHandle()

        # 同步结果展示&MQ结果推送
        self.sync_result = list()

    def v2_runner_on_ok(self, result):

        _result = result._result

        data = []

        if _result.get('stdout_lines'):
            for item in _result.get('stdout_lines'):
                try:
                    json_result = json.loads(item)
                    data.append(json_result)
                except ValueError:
                    if isinstance(item, str):
                        data.append(item)
                except Exception as e:
                    data.append(repr(e))
        if _result.get('path'):
            file_distribute=dict(
                path=_result.get('path'),
                size=_result.get('size'),
                owner=_result.get('owner'),
            )
            
            data.append(file_distribute)


        host = result._host.get_name()

        cmd = ''
        if self.exec_type == 'shell':
            cmd = '[{}: {} INFO/{}] {}\n'.format(self.start_date, host, self.exec_type, _result.get('cmd').rstrip('\n'))

        elif self.exec_type == 'script':
            cmd = '[{}: {} INFO/{}] {}\n'.format(self.start_date, host, self.exec_type, self.raw_args.split('/')[-1])

        logs = '{}{}\n'.format(cmd, _result.get('stdout'))

        res = dict(
            target=host,
            start_date=self.start_date,
            status='SUCCESS',
            end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        if data:
            res['result'] = data


        logger.debug('task num {} - v2_runner_on_ok'.format(self.task_num))
        logger.debug(_result)

        self.sync_result.append(res)
        
        if self.task_num and self.exec_async != 0:
            if self.log_server == 1:
                self.es_handle.send_result(job_num=self.job_num, result=res, log=logs)

    def v2_runner_on_failed(self, result, ignore_errors=False):

        _result = result._result
        host = result._host.get_name()

        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cmd = ''
        error_msg = ''

        if self.exec_type == 'shell':

            msg = _result.get('cmd')
            if msg:
                cmd = '[{}: {} ERROR/{}] {}\n'.format(start_date, host, self.exec_type, msg.rstrip('\n'))
            error_msg = _result.get('stderr')
            if not error_msg:
                error_msg = _result.get('module_stdout')

        elif self.exec_type == 'script':
            
            cmd = '[{}: {} ERROR/{}] {}\n'.format(start_date, host, self.exec_type, self.raw_args.split('/')[-1])
            error_msg = _result.get('stdout')

        logs = '{}{}\n'.format(cmd, error_msg)

        res = dict(
            target=host,
            start_date=self.start_date,
            status='FAILURE',
            end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            result=_result
        )
        logger.error('task num {} - v2_runner_on_failed'.format(self.task_num))
        logger.error(_result)

        self.sync_result.append(res)

        if self.task_num and self.exec_async != 0:
            if self.log_server == 1:
                self.es_handle.send_result(job_num=self.job_num, result=res, log=logs)

    def v2_runner_on_unreachable(self, result):

        _result = result._result

        host = result._host.get_name()

        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        logs = '[{}: {} ERROR/{}] {}\n'.format(current_date, host, self.exec_type, _result.get('msg').rstrip('\r\n'))

        res = dict(
            target=host,
            start_date=self.start_date,
            status='FAILURE',
            end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            result=[_result]
        )

        logger.error('task num {} - v2_runner_on_unreachable'.format(self.task_num))
        logger.error(_result)



        self.sync_result.append(res)

        if self.task_num and self.exec_async != 0:
            if self.log_server == 1:        
                self.es_handle.send_result(job_num=self.job_num, result=res, log=logs)


class RemoteApi(object):
    """

    """
    def __init__(self, resource=None, source=settings.ANSIBLE_HOSTS_FILE, *args, **kwargs):
        """

        :param resource:
        :param source:
        :param args:
        :param kwargs:
        """
        self.resource = resource
        self.source = source
        self.inventory = None
        self.variable_manager = None
        self.loader = None
        self.options = None
        self.password = None
        self.callback = None

        self.timeout = kwargs.get('timeout', 10)
        self.forks = kwargs.get('forks', '') if kwargs.get('forks', '') else 100
        self.connection = kwargs.get('connection', '') if kwargs.get('connection', '') else 'smart'



        self.become = kwargs.get('become', '') if kwargs.get('become', '') else dict()
        self.become_state = True if self.become else False

        self.become_method = self.become.get('method')
        self.become_user = self.become.get('username')
        self.become_pass = jkAes().decrypt(self.become.get('password')) if self.become else self.become.get('password')

        self.__initializeData()
        

    def __initializeData(self):
        """

        :return:
        """
        Options = namedtuple(
            'Options', [
                'connection',
                'module_path',
                'forks',
                'timeout',
                'remote_user',
                'ask_pass',
                'private_key_file',
                'ssh_common_args',
                'ssh_extra_args',
                'sftp_extra_args',
                'scp_extra_args',
                'become',
                'become_method',
                'become_user',
                'become_pass',
                'ask_value_pass',
                'verbosity',
                'check',
                'listhosts',
                'listtasks',
                'listtags',
                'diff',
                'syntax'
            ]
        )

        self.options = Options(
            connection='smart',
            module_path=settings.ANSIBLE_EXTEND_MODULES,
            forks=self.forks,
            timeout=self.timeout,
            remote_user=settings.ANSIBLE_REMOTE_USER,
            ask_pass=False,
            private_key_file=None,
            ssh_common_args=None,
            ssh_extra_args=None,
            sftp_extra_args=None,
            scp_extra_args=None,
            become=self.become_state,
            become_method=self.become_method,
            become_user=self.become_user,
            become_pass=self.become_pass,
            ask_value_pass=False,   # 是否询问su|sudo密码
            verbosity=None,
            check=False,
            listhosts=False,
            listtasks=False,
            listtags=False,
            diff=False,
            syntax=False
        )

        self.loader = DataLoader()

        self.password = dict(vault_pass='secret')

        self.inventory = MyInventory(resource=self.resource, loader=self.loader, sources=self.source).inventory

        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)

    def run(self, host_list, module_name, job_num, node_num,custom_data,exec_async, module_args=None, task_num=None, log_server=None):
        """

        :param task_num:
        :param host_list:
        :param module_name:
        :param job_num:
        :param module_args:
        :return:
        """

        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if module_name == 'cmd.run':
            module_name = 'shell'
            # module_name = 'raw'
            # module_name = 'command'
        if module_name == 'cmd.script':
            module_name = 'script'
        if module_name == 'file.distribute':
            module_name = 'copy'

        play_source = dict(
            name=settings.ANSIBLE_PLAY,
            hosts=host_list,
            gather_facts='no',
            tasks=[
                dict(
                    action=dict(
                        module=module_name,
                        args=module_args
                    )
                )
            ]
        )

        play = Play().load(data=play_source, variable_manager=self.variable_manager, loader=self.loader)

        tmq = None

        self.callback = CustomCallback(
            job_num=job_num,
            node_num=node_num,
            custom_data=custom_data,
            exec_type=module_name,
            exec_async=exec_async,
            raw_args=module_args,
            task_num=task_num,
            log_server=log_server,
            start_date=start_date
        )
        try:
            tmq = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.password,
                stdout_callback=self.callback,
            )
            ret = tmq.run(play=play)
            return ret
        finally:
            if tmq is not None:
                tmq.cleanup()
            if self.loader:
                self.loader.cleanup_all_tmp_files()
            self.inventory.clear_pattern_cache()


    def get_result(self):

        return self.callback.sync_result