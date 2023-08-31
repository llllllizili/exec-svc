#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   snmpwalk.py
@Time    :   2021/10/20 18:40
'''

# import re
import json
import logging
import subprocess
from datetime import datetime
from .oid_mapping import oidMapping, returnDataMapping


logger = logging.getLogger('console')


class WalkApi(object):
    def __init__(self, community, version, host, port, intention, **kwargs):
        self.host = host
        self.port = port
        self.snmp_port = port
        self.version = version
        self.community = community
        self.intention = intention
        self.user = kwargs.get('user', '')  # snmpv3 用户
        self.level = kwargs.get('level', '')  # authPriv authNoPriv
        self.auth_protocol = kwargs.get('auth_protocol', '')  # md5 sha
        self.auth_pass = kwargs.get('auth_pass', '')
        self.priv_protocol = kwargs.get('priv_protocol', '')  # des aes
        self.priv_pass = kwargs.get('priv_pass', '')

        self._return_data = returnDataMapping
        
        if self.version == '3c':
            self.version = 3

    def walk_cmd_v2(self, oid):
        (status, output) = subprocess.getstatusoutput('snmpwalk' + ' -c ' + self.community + ' -v ' + self.version + ' ' + self.host + ':' + self.port + ' ' + oid)

        # print("{}   {}".format(status,oid))

        if status > 0:  # failed
            return False, output
        else:  # success
            return True, output

    def walk_cmd_v3(self, oid):
        if self.level == 'authPriv':
            (status, output) = subprocess.getstatusoutput('snmpwalk -v ' + self.version + ' -u ' + self.user + ' -l ' + self.level + ' -a ' + self.auth_protocol +
                                                          ' -A ' + self.auth_pass + ' -x ' + self.priv_protocol + ' -X ' + self.priv_pass + ' ' + self.host + ':' +
                                                          self.snmp_port + ' ' + oid)
        elif self.level == 'authNoPriv':
            (status, output) = subprocess.getstatusoutput('snmpwalk -v ' + self.version + ' -u ' + self.user + ' -l ' + self.level + ' -a ' + self.auth_protocol +
                                                          ' -A ' + self.auth_pass + ' ' + self.host + ':' + self.snmp_port + ' ' + oid)
        elif self.level == 'noAuthNoPriv':
            (status, output) = subprocess.getstatusoutput('snmpwalk -v ' + self.version + ' -u ' + self.user + ' -l ' + self.level + ' ' + self.host + ':' +
                                                          self.snmp_port + ' ' + oid)
        else:
            return False, 'invalid auth level'

        if status > 0:  # failed
            return False, output
        else:  # success
            return True, output

    def split_snmpwalk_data(self, data):
        # print(data)
        oid_value_list = list()
        for info in data.split("\n"):
            if '=' in info:
                line_data = info.split(' = ')
                oid_value = line_data[1].split(': ')[-1].strip('"')
                if 'ipAdEntIfIndex' in data:
                    oid_value = dict()
                    if_address = line_data[0].split('.')[-4:]
                    oid_value = '.'.join(if_address)
                oid_value_list.append(oid_value)
            else:
                oid_value_list.append(data)
        # print(oid_value_list)
        return oid_value_list

    def return_oid_data(self):
        self._return_data['start_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._return_data['target'] = self.host

        _result = dict()

        key_list = (list(oidMapping.keys()))

        for key in key_list:
            _result[key] = dict()
            _oid_dict = oidMapping.get(key)
            _property_dict_key_list = (list(_oid_dict.keys()))
            for _property in _property_dict_key_list:
                if _oid_dict.get(_property).get('oid'):
                    if self.version == '2c':
                        status, walk_data = self.walk_cmd_v2(_oid_dict.get(_property).get('oid'))
                    else:
                        status, walk_data = self.walk_cmd_v3(_oid_dict.get(_property).get('oid'))
                else:
                    status, walk_data = False, _property + ': oid is null'

                if status:
                    self._return_data['status'] = 'SUCCESS'
                    _data = self.split_snmpwalk_data(walk_data)
                    for num, w_data in enumerate(_data):
                        if _result[key].get(num):
                            _result[key][num][_property] = w_data
                        else:
                            _result[key][num] = dict()
                            _result[key][num][_property] = w_data
                else:
                    # 错误不更改状态，OID全部对比较难
                    # self._return_data['status'] = 'FAILURE'
                    logger.error(walk_data)

                    #return False, walk_data

        return True, _result

    def get_data(self):
        status, oid_data = self.return_oid_data()

        result = {'ip': {}, 'cpu': {}, 'fan': {}, 'power': {}, 'disk': {}, 'memory': {}}
        # 基础信息 数据兼容
        result.update(oid_data['base'][0])
        # CPU 数据兼容
        result['cpu'].update(oid_data['cpu'])
        # memory 数据兼容
        result['memory'].update(oid_data['memory'])
        # fan 数据兼容
        fan_data = oid_data.get('fan')
        if fan_data:
            for fan in fan_data:
                result['fan'][fan_data[fan]['name']] = fan_data[fan]
        # disk 数据兼容
        disk_data = oid_data.get('disk')
        if disk_data:
            for disk in disk_data:
                if disk_data.get(disk).get('name'):
                    result['disk'][disk_data[disk]['name']] = disk_data[disk]
        # power 数据兼容
        power_data = oid_data.get('power')
        if power_data:
            for power in power_data:
                if power_data.get(power).get('name'):
                    result['power'][power_data[power]['name']] = power_data[power]
        # ip 数据兼容
        ip_data = oid_data.get('ip')
        if ip_data:
            for ip in ip_data:
                if ip_data.get(ip).get('name'):
                    result['ip'][ip_data[ip]['name']] = ip_data[ip]

        self._return_data['result'] = result
        self._return_data['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return True, self._return_data

    def __del__(self):
        pass


if __name__ == '__main__':
    snmpwalk = WalkApi('Server', '2c', '192.168.5.20', '161', 'hdinfo')
    # snmpwalk = WalkApi('123@qweASD', '3', '192.168.5.27', '161', 'hdinfo',user='cmdp',auth_protocol='sha',priv_protocol='aes')
    res = snmpwalk.get_data()
    print(json.dumps(res, ensure_ascii=False))
