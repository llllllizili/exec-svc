#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   snmpwalk.py
@Time    :   2020/04/28 15:53:56
'''

# import re
import json
import subprocess
from datetime import datetime
from .config import oid_lable_num, oid_lable_desc, oid_lable_class
from utils.jklog import jklog


class WalkApi(object):
    def __init__(self, community, version, host, port, intention, **kwargs):
        self.host = host
        self.port = port
        self.version = version
        self.community = community
        self.intention = intention
        self.user = kwargs.get('user', '')  # snmpv3 用户
        self.level = kwargs.get('level', '')  # authPriv authNoPriv
        self.auth_protocol = kwargs.get('auth_protocol', '')  # md5 sha
        self.auth_pass = kwargs.get('auth_pass', '')
        self.priv_protocol = kwargs.get('priv_protocol', '')  # des aes
        self.priv_pass = kwargs.get('priv_pass', '')

        if self.version == '3c':
            self.version = 3
            
    def _lable2num(self, oid_lable):
        if oid_lable in oid_lable_num():
            return oid_lable_num()[oid_lable]
        else:
            return oid_lable

    def _lable2desc(self, oid_lable):
        if oid_lable in oid_lable_desc():
            return oid_lable_desc()[oid_lable]
        else:
            return oid_lable

    def _lable2class(self, oid_lable):
        if oid_lable in oid_lable_class():
            # oid_lable_class()[oid_lable] = list()

            return oid_lable_class()[oid_lable]
        else:
            return ''

    def walk_cmd(self, oid):
        (status, output) = subprocess.getstatusoutput('snmpwalk' + ' -c ' + self.community + ' -v ' + self.version + ' ' + self.host + ' ' + oid)

        if status > 0:
            return False, status, output
        else:
            return True, status, output

    def walk_cmd_v3(self, oid):
        if self.level == 'authPriv':
            walk_cmd = "snmpwalk -v {} -u {} -l {} -a {} -A {} -x {} -X {} {}:{} {}".format(
                self.version, self.user, self.level, self.auth_protocol, 
                self.auth_pass, self.priv_protocol, self.priv_pass,
                self.host,self.port, oid
                )
            # print(walk_cmd)
            (status, output) = subprocess.getstatusoutput(walk_cmd)
            print(output)
            if status > 0:
                return False, status, output
            else:
                return True, status, output
        elif self.level == 'authNoPriv':
            walk_cmd = "snmpwalk -v {} -u {} -l {} -a {} -A {} {}:{} {}".format(
                self.version, self.user, self.level,self.auth_protocol, self.auth_pass,self.host,self.port, oid
                )
            # print(walk_cmd)

            (status, output) = subprocess.getstatusoutput(walk_cmd)
            if status > 0:
                return False, status, output
            else:
                return True, status, output
        elif self.level == 'noAuthNoPriv':
            walk_cmd = "snmpwalk -v {} -u {} -l {} {}:{} {}".format(
                self.version, self.user, self.level,self.host,self.port, oid
                )
            # print(walk_cmd)

            (status, output) = subprocess.getstatusoutput(walk_cmd)
            if status > 0:
                return False, status, output
            else:
                return True, status, output

    def get_data(self):

        status_code = {1: 'other', 2: 'unknown', 3: 'ok', 4: 'nonCritical', 5: 'critical', 6: 'nonRecoverable'}

        data_dict = dict()
        result_dict = dict()
        # result_dict['status_code'] = status_code

        data_dict['start_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_dict['target'] = self.host
        data_dict['status'] = 'SUCCESS'
        data_dict['result'] = list()

        for lable in oid_lable_num():
            success, status, data_out = self.walk_cmd(self._lable2num(lable)) if self.version == '2c' \
                else self.walk_cmd_v3(self._lable2num(lable))  # result
            if not success:
                data_dict['status'] = 'FAILURE'
                result_dict[self.host] = data_out
                break
            if 'Timeout' in data_out:
                data_dict['status'] = 'FAILURE'
                result_dict[self.host] = data_out
                break
            if 'No Such Object' in data_out:
                data_dict['status'] = 'FAILURE'
                result_dict[lable] = data_out
                break

            class_key = self._lable2class(lable) if self._lable2class(lable) else ''

            line_dict = dict()

            # print('------------')
            # print(data_out)

            for num, line_data in enumerate(data_out.split("\n")):
                oid_value = line_data.split('=')[1].split(': ')[-1].replace('"', '')
                line_dict[num] = oid_value
                line_dict['describe'] = self._lable2desc(lable)

            if class_key in result_dict:
                result_dict[class_key].append(line_dict)
            else:
                result_dict[class_key] = [line_dict]

        data_dict['result'].append(result_dict)

        data_dict['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return True, data_dict

    def com_verify(self):

        result_dict = dict()
        data_dict = dict()
        data_dict['start_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_dict['target'] = self.host
        data_dict['status'] = 'SUCCESS'

        success, status, data_out = self.walk_cmd(self._lable2num('sysDesc')) if self.version == '2c' \
            else self.walk_cmd_v3(self._lable2num('sysDesc'))  # result

        if not success or 'Timeout' in data_out:
            data_dict['status'] = 'FAILURE'
            data_dict['err_msg'] = data_out
        else:
            sys_desc = data_out.split(' = ')[-1]
            result_dict['sys_desc'] = sys_desc
        data_dict['result'] = result_dict
        data_dict['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return True, data_dict


if __name__ == '__main__':
    snmpwalk = WalkApi('xxx', '2c', '192.168.x.x', intention='hdinfo', port=623)
    res = snmpwalk.get_data()
    print(json.dumps(res, encoding='gbk', ensure_ascii=False))
