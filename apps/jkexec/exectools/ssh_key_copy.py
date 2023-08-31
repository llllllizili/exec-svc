#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   ssh_key_copy.py
@Time    :   2020/06/06 23:52:18
'''

import os
import shlex
from subprocess import check_output, STDOUT, CalledProcessError
from django.conf import settings
from utils.jklog import jklog


def command(cmd, is_shell=False):
    """

    :param cmd:
    :param is_shell:
    :return:
    """
    if not is_shell:
        cmd = shlex.split(cmd)

    try:
        process = check_output(cmd, shell=is_shell, stderr=STDOUT)
        return True, process
    except CalledProcessError as e:
        return False, repr(e)
    except Exception as e:
        return False, repr(e)


def add_sshKey(data):
    """

    :param data
    """

    _script_file = '{}/__jk_script_addKey.sh'.format(settings.ANSIBLE_PRIVATE_SCRIPT_PATH)

    if not os.path.exists(_script_file):
        return False, 'add key script file not exists'

    cmd = 'expect {} {username} {ip} {password} {port}'.format(_script_file,
                                                               username=data.get('username'),
                                                               ip=data.get('ip'),
                                                               password=data.get('password'),
                                                               port=data.get('port'))

    success, result = command(cmd=cmd, is_shell=True)

    if not success:
        jklog('error',result)

        return False, result

    jklog('debug',result)

    return True, result


def delete_key(data):
    '''
    仅用于删除本机信息,client信息需要使用脚本删除/卸载
    '''

    control_type = data.get('control_type')
    username = data.get('username'),
    ip = data.get('ip'),
    password = data.get('password'),
    port = data.get('port')

    if control_type == 'agentless':

        local_konow_host_delete = "ssh-keygen -f ~/.ssh/known_hosts -R " + ip

        success, result = command(cmd=local_konow_host_delete, is_shell=True)

        if not success:
            jklog('debug', result)
            return False, result

    if control_type == 'agent':

        accept_key_delete = "salt-key -yd " + ip

        success, result = command(cmd=accept_key_delete, is_shell=True)

        if not success:
            jklog('debug', result)
            return False, result
