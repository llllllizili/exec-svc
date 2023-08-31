#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   ruijie/default/snmpwalk.py
@Time    :   2020/08/17
'''

import json
import subprocess
from datetime import datetime
from .config import oid_lable_num,oid_lable_desc

class WalkApi(object):

    def __init__(self, community, version, host, port):
        self.host = host 
        self.version = version
        self.community = community
        self.snmp_port = port
        self.oid_dict = oid_lable_num()
        self.desc_dict = oid_lable_desc()
        if self.version == '3c':
            self.version = 3
    def walk_cmd(self, oid):
        (status, output) = subprocess.getstatusoutput(
            'snmpwalk -c ' + self.community + ' -v ' + self.version + ' ' + self.host + ' ' + oid + ' -Cc')
        return output

    def get_ifname(self):
        port_info = self.walk_cmd(self.oid_dict['ifDescr'])
        ifname_dict = dict()
        for item in port_info.split('\n'):
            if 'string' in item.lower():
                entry = item.split('=')
                port_num = entry[0].split('.')[-1].strip()
                ifname = entry[-1].split(':')[-1].strip('"')
                ifname_dict[port_num] = ifname
        return ifname_dict

    def get_loc(self):
        result = self.walk_cmd(self.oid_dict['lldpLocChassisId'])
        loc_info = result.split('\n')
        if 'No Such' in loc_info[0]:
            chassisID = 'None'
        else:
            chassisID = loc_info[0].split(':')[-1].strip()
        return chassisID

    def get_data(self):
        rem_dict = dict()
        lldp_rem_dict = dict()
        lldp_loc_dict = dict()
        data_dict = dict()
        data_dict['start_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_dict['target'] = self.host
        data_dict['result'] = list()
        data_dict['status'] = 'SUCCESS' 
        rem_info = self.walk_cmd(self.oid_dict['lldpRemChassisId'])
        if 'Timeout' in rem_info or 'No Such' in rem_info:
            data_dict['status'] = 'FAILURE' 
            lldp_rem_dict['lldpRemChassisId'] = rem_info
        else:
            ifname_dict = self.get_ifname()
            for item in rem_info.split('\n'):
                if 'hex' in item.lower():
                    entry = item.split('=')
                    port_num = entry[0].split('.')[-2].strip()
                    rem_chassisid = entry[-1].split(':')[-1].strip()
                    rem_dict[ifname_dict[port_num]]=rem_chassisid
            if rem_dict:
                lldp_rem_dict['lldpRemChassisId'] = rem_dict
            else:
                lldp_rem_dict['lldpRemChassisId'] = 'None'
        lldp_rem_dict['describ'] = self.desc_dict['lldpRemChassisId']
        lldp_loc_dict['lldpLocChassisId'] = self.get_loc()
        lldp_loc_dict['describ'] = self.desc_dict['lldpLocChassisId']
        data_dict['result'].append(lldp_rem_dict)
        data_dict['result'].append(lldp_loc_dict)
        data_dict['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return True, [data_dict]

if __name__ == "__main__":
    snmpwalk = WalkApi('public', '2c', '172.20.20.210', '121')
    res = snmpwalk.get_data()
    print(json.dumps(res,ensure_ascii=False))