#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   dell/default/snmpwalk.py
@Time    :   2020/08/28
'''

# import re
import json
import subprocess
from datetime import datetime
from .config import oid_lable_num,oid_lable_desc,oid_lable_class

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
        (status, output) = subprocess.getstatusoutput(
            'snmpwalk'+' -c '+self.community+' -v '+self.version+' '+self.host+':'+self.port+' '+oid)
       
        return output

        # if status > 0:  # failed
        #     return {'status': 0, 'msg': output}
        # else:   # success
        #     return {'status': 1, 'msg': output}

    def walk_cmd_v3(self, oid):
        if self.level == 'authPriv':
            (status, output) = subprocess.getstatusoutput(
                'snmpwalk -v ' + self.version + ' -u ' + self.user + ' -l ' + self.level + ' -a ' + self.auth_protocol +
                ' -A ' + self.auth_pass + ' -x ' + self.priv_protocol + ' -X ' + self.priv_pass + ' ' +
                self.host + ':' + self.port + ' ' + oid)
            return output
        elif self.level == 'authNoPriv':
            (status, output) = subprocess.getstatusoutput(
                'snmpwalk -v ' + self.version + ' -u ' + self.user + ' -l ' + self.level + ' -a ' + self.auth_protocol +
                ' -A ' + self.auth_pass + ' ' + self.host + ':' + self.port + ' ' + oid)
            return output
        elif self.level == 'noAuthNoPriv':
            (status, output) = subprocess.getstatusoutput(
                'snmpwalk -v ' + self.version + ' -u ' + self.user + ' -l ' + self.level + ' ' +
                self.host + ':' + self.port + ' ' + oid)
            return output

    def get_data(self):
        
        data_dict = dict()
        result_dict = dict()
        tmp_dict = dict()
        ifAddress_dict = dict()
        ifName_dict = dict()
        err_msg_list = list()

        data_dict['start_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_dict['target'] = self.host
        data_dict['status'] = 'SUCCESS'
        data_dict['result'] = dict()

        for lable in oid_lable_num():

            data_out = self.walk_cmd(self._lable2num(lable)) if self.version == '2c' else \
                    self.walk_cmd_v3(self._lable2num(lable))  # result

            if 'Timeout' in data_out:
                data_dict['status'] = 'FAILURE' 
                result_dict[self.host] = data_out
                break
            if 'No Such Object' in data_out:
                err_msg_list.append(lable)
                continue

            line_list = list()
            class_key = self._lable2class(lable) if self._lable2class(lable) else ''
            
            for num,entry in enumerate(data_out.split("\n")):
                line_data = entry.split(' = ')
                oid_value = line_data[1].split(': ')[-1].strip('"')
                line_list.append(oid_value)
                if lable == 'ipAdEntIfIndex':
                    if_address = line_data[0].split('.')[-4:]
                    if_index = line_data[1].split(': ')[-1]
                    ifAddress_dict[if_index] = '.'.join(if_address)

            tmp_dict[lable] = line_list
            if class_key in ['ip', 'power', 'cpu', 'memory', 'fan', 'disk']:
                if lable == 'ifDescr':
                    result_dict['ip'] = dict()
                    for num, if_name in enumerate(line_list):
                        ip_dict = dict()
                        if_index = tmp_dict['ifIndex'][num]
                        ip_dict['ip'] = ifAddress_dict[if_index] if if_index in ifAddress_dict else ''
                        ip_dict['state'] = tmp_dict['ifAdminStatus'][num]
                        ip_dict['mac'] = tmp_dict['ifPhyAddress'][num]
                        result_dict['ip'][if_name] = ip_dict
                elif lable == 'powerSupplyLocationName':
                    result_dict['power'] = dict()
                    for num, power_name in enumerate(line_list):
                        power_dict = dict()
                        power_dict['state'] = tmp_dict['powerSupplyStatus'][num]
                        power_dict['type'] = tmp_dict['powerSupplyType'][num]
                        result_dict['power'][power_name] = power_dict
                elif lable == 'processorDeviceBrandName':
                    result_dict['cpu'] = dict()
                    for num, cpu_name in enumerate(line_list):
                        cpu_dict = dict()
                        cpu_dict['state'] = tmp_dict['processorDeviceStatus'][num]
                        cpu_dict['manu'] = tmp_dict['processorDeviceManufacturerName'][num]
                        # cpu_dict['slot'] = tmp_dict['processorDeviceCoreCount'][num]
                        cpu_dict['name'] = cpu_name
                        result_dict['cpu'][num] = cpu_dict                    
                elif lable == 'memoryDeviceSize':
                    result_dict['memory'] = dict()
                    for num, mem_size in enumerate(line_list):
                        mem_dict = dict()
                        mem_dict['speed'] = tmp_dict['memoryDeviceSpeed'][num]
                        mem_dict['type'] = tmp_dict['memoryDeviceType'][num]
                        mem_dict['manu'] = tmp_dict['memoryDeviceManufacturerName'][num]
                        mem_dict['state'] = tmp_dict['memoryDeviceStatus'][num]
                        mem_dict['size'] = mem_size
                        result_dict['memory'][num] = mem_dict
                elif lable == 'coolingDeviceLocationName':
                    result_dict['fan'] = dict()
                    for num, fan_name in enumerate(line_list):
                        fan_dict = dict()
                        fan_dict['speed'] = tmp_dict['coolingDeviceReading'][num]
                        fan_dict['state'] = tmp_dict['coolingDeviceStatus'][num]
                        result_dict['fan'][fan_name] = fan_dict
                elif lable == 'physicalDiskDisplayName':
                    result_dict['disk'] = dict()
                    for num, disk_name in enumerate(line_list):
                        disk_dict = dict()
                        disk_dict['size'] = str(int(tmp_dict['physicalDiskCapacityInMB'][num])*1024)
                        disk_dict['state'] = tmp_dict['physicalDiskState'][num]
                        disk_dict['type'] = tmp_dict['physicalDiskMediaType'][0]
                        result_dict['disk'][disk_name] = disk_dict
                else:
                    pass
            elif class_key == 'sys_uptime':
                result_dict['sys_uptime'] = line_list[0].split(') ')[1]
            else:
                result_dict[class_key] = tmp_dict[lable][0]
        data_dict['result'] = result_dict
        if err_msg_list:
            data_dict['status'] = 'FAILURE'
            data_dict['err_msg'] = err_msg_list
        data_dict['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return True,data_dict


if __name__ == '__main__':
    snmpwalk = WalkApi('xxx', '2c', '192.168.x.x', '161', 'hdinfo')
    res = snmpwalk.get_data()
    print(json.dumps(res,ensure_ascii=False))