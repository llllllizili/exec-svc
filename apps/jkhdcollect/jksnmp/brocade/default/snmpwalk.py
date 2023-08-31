#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   brocade/default/snmpwalk.py
@Time    :   2020/12/03
'''

import json
import subprocess
from datetime import datetime
from .config import oid_lable_num,oid_lable_class

class WalkApi(object):

    def __init__(self, community, version, host, port, intention):
        self.host = host 
        self.version = version
        self.community = community
        self.intention = intention
        self.snmp_port = port
        self.oid_dict = oid_lable_num()
        self.class_dict = oid_lable_class()

    def walk_cmd(self, oid):
        (status, output) = subprocess.getstatusoutput(
            'snmpwalk -c ' + self.community + ' -v ' + self.version + ' ' + self.host + ':' + self.snmp_port + ' ' + oid + ' -Cc')
        return output

    def get_basic_info(self, lable, output):
        basic_info_dict = dict()
        vlan_state_dict = dict()
        vlan_name_dict = dict()
        if_id_list = list()
        if_speed_dict = dict()
        if_mac_dict = dict()
        if_descr_dict = dict()
        if_state_dict = dict()
        if lable == 'sysName':
            basic_info_dict['sys_name'] = output.split(': ')[-1].strip('"')
        elif lable == 'iosVersion':
            basic_info_dict['ios_version'] = output.split(': ')[-1].strip('"')
        elif lable == 'sysUptime':
            basic_info_dict['sys_uptime'] = output.split(')')[-1].strip()
        elif lable == 'entPhysicalSerialNum':                    
            basic_info_dict['serial_num'] = output.split('"')[1]
        elif lable == 'modelName':
            basic_info_dict['model_name'] = output.split('"')[1]
        elif lable == 'vlanName':
            for item in output.split('\n'):
                entry = item.split(' = ')
                vlan_id = entry[0].split('.')[-1]
                if entry[-1] == "":
                    vlan_name = "unset"
                elif "string" in entry[-1].lower():
                    vlan_name = entry[-1].split(': ')[-1].strip('"')
                else:
                    vlan_name = entry[-1].strip('"')
                vlan_name_dict[vlan_id] = vlan_name
            basic_info_dict['vlan_name_dict'] = vlan_name_dict
        elif lable == 'vlanState':
            for item in output.split('\n'):
                entry = item.split(' = ')
                vlan_id = entry[0].split('.')[-1]
                vlan_state = entry[-1].split(': ')[-1]
                vlan_state_dict[vlan_id] = vlan_state
            basic_info_dict['vlan_state_dict'] = vlan_state_dict                    
        elif lable == 'ifAdminStatus':
            for item in output.split('\n'):
                entry = item.split(' = ')
                if_id = entry[0].split('.')[-1]
                if_state = entry[-1].split(': ')[1]
                if_state_dict[if_id] = if_state
            basic_info_dict['if_state_dict'] = if_state_dict
        elif lable == 'ifSpeed':
            for item in output.split('\n'):
                entry = item.split(' = ')
                if_id = entry[0].split('.')[-1]
                if_speed = entry[-1].split(': ')[1]
                if_speed_dict[if_id] = if_speed
            basic_info_dict['if_speed_dict'] = if_speed_dict
        elif lable == 'ifPhysAddress':
            for item in output.split('\n'):
                entry = item.split(' = ')
                if_id = entry[0].split('.')[-1]
                if 'STRING:' in item:
                    hex_mac = entry[-1].split(' ')[1:7]
                    if_mac = ':'.join(hex_mac)
                else:
                    if_mac = None
                if_mac_dict[if_id] = if_mac
            basic_info_dict['if_mac_dict'] = if_mac_dict
        elif lable == 'ifDescr':
            for item in output.split('\n'):
                entry = item.split(' = ')
                if_id = entry[0].split('.')[-1]
                if_descr = entry[-1].split(': ')[-1].strip('"')
                if_descr_dict[if_id] = if_descr
            basic_info_dict['if_descr_dict'] = if_descr_dict
        return basic_info_dict

    def get_ifname(self):
        port_info = self.walk_cmd(self.oid_dict['ifDescr'])
        ifname_dict = dict()
        for item in port_info.split('\n'):
            if 'string' in item.lower():
                entry = item.split(' = ')
                port_num = entry[0].split('.')[-1].strip()
                ifname = entry[-1].split(':')[-1].strip('"')
                ifname_dict[port_num] = ifname
        return ifname_dict

    def get_loc(self):
        result = self.walk_cmd(self.oid_dict['lldpLocChassisId'])
        loc_info = result.split('\n')
        if 'No Such' in loc_info[0]:
            chassisID = None
        else:
            chassisID = loc_info[0].split(':')[-1].strip()
        return chassisID

    def get_if(self, basic_info_dict):
        if_dict = dict()
        for (port, ifname) in basic_info_dict['if_descr_dict'].items():
            port_dict = dict()
            port_dict['state'] = basic_info_dict['if_state_dict'][port]
            port_dict['speed'] = basic_info_dict['if_speed_dict'][port]
            port_dict['mac'] = basic_info_dict['if_mac_dict'][port]
            if_dict[ifname] = port_dict
        return if_dict

    def get_vlan(self, basic_info_dict):
        vlan_dict = dict()
        if 'vlan_state_dict' not in basic_info_dict.keys():
            return vlan_dict
        for (port, state) in basic_info_dict['vlan_state_dict'].items():
            port_dict = dict()
            vlan_name = basic_info_dict['vlan_name_dict'][port]
            port_dict['state'] = state
            if port in basic_info_dict['if_speed_dict']:
                port_dict['speed'] = basic_info_dict['if_speed_dict'][port]
            else:
                port_dict['speed'] = ''
            if port in basic_info_dict['if_mac_dict']:
                port_dict['mac'] = basic_info_dict['if_mac_dict'][port]
            else:
                port_dict['mac'] = ''        
            vlan_dict[vlan_name] = port_dict
        return vlan_dict

    def get_arp(self):
        arp_dict = dict()
        ip2mac_info = self.walk_cmd(self.oid_dict['ipNetToMac'])
        if 'Timeout' in ip2mac_info or 'No Such' in ip2mac_info:
            return arp_dict
        for item in ip2mac_info.split('\n'):
            entry = item.split(' = ')
            ip_num = entry[0].split('.')[-4:999]
            ip_net = '.'.join(ip_num)
            net_mac = entry[1].split(': ')[-1]
            arp_dict[ip_net] = net_mac
        return arp_dict

    def get_data(self):
        rem_dict = dict()
        data_dict = dict()
        err_msg_list = list()
        basic_info_dict = dict()
        data_dict['start_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_dict['target'] = self.host
        data_dict['result'] = dict()
        data_dict['status'] = 'SUCCESS'
        if self.intention == 'topinfo':
            rem_info = self.walk_cmd(self.oid_dict['lldpRemChassisId'])
            if 'Timeout' in rem_info or 'No Such' in rem_info:
                data_dict['status'] = 'FAILURE' 
                data_dict['err_msg'] = rem_info
            else:
                ifname_dict = self.get_ifname()
                for item in rem_info.split('\n'):
                    if 'hex' in item.lower():
                        entry = item.split(' = ')
                        port_num = entry[0].split('.')[-2].strip()
                        rem_chassisid = entry[-1].split(':')[-1].strip()
                        rem_dict[ifname_dict[port_num]] = rem_chassisid
                data_dict['result']['lldpRemChassisId'] = rem_dict
            data_dict['result']['arp_dict'] =  self.get_arp()
            data_dict['result']['lldpLocChassisId'] = self.get_loc()
        elif self.intention == 'hdinfo':
            for lable in self.class_dict['basicInfo']:
                output = self.walk_cmd(self.oid_dict[lable])
                if 'Timeout' in output:
                    data_dict['status'] = 'FAILURE'
                    data_dict['err_msg'] = output
                    break
                elif 'No Such Object' in output:
                    data_dict['status'] = 'FAILURE'
                    err_msg_list.append(output + ' Item:' + lable)
                    continue
                else:
                    basic_info_dict.update(self.get_basic_info(lable, output))
            if err_msg_list:
                data_dict['status'] = 'FAILURE'
                data_dict['err_msg'] = err_msg_list
            basic_info_dict['if_dict'] = self.get_if(basic_info_dict)
            basic_info_dict['vlan_dict'] = self.get_vlan(basic_info_dict)
            basic_info_dict['vlan_count'] = len(basic_info_dict['vlan_dict'])
            basic_info_dict['if_count'] = len(basic_info_dict['if_dict'])
            del basic_info_dict['if_mac_dict']
            del basic_info_dict['if_speed_dict']
            del basic_info_dict['if_state_dict']
            del basic_info_dict['if_descr_dict']
            if 'vlan_state_dict' in basic_info_dict.keys():
                del basic_info_dict['vlan_state_dict'] 
                del basic_info_dict['vlan_name_dict']
            data_dict['result'] = basic_info_dict
        else:
            data_dict['status'] = 'FAILURE'
            data_dict['err_msg'] = 'Please make sure your "intention" is right(topinfo/hdinfo)'
        data_dict['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return True, data_dict

if __name__ == "__main__":
    snmpwalk = WalkApi('xxx', '2c', '12.118.216.1', '161', 'topinfo')
    res = snmpwalk.get_data()
    print(json.dumps(res,ensure_ascii=False))