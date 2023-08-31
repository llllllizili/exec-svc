#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   cisco/default/snmpwalk.py
@Time    :   2020/08/24
'''

import json
import subprocess
from datetime import datetime
from utils.jklog import jklog
from .config import oid_lable_num, oid_lable_desc, oid_lable_class

class WalkApi(object):

    def __init__(self, community, version, host, port, intention, **kwargs):
        self.host = host 
        self.version = version
        self.community = community
        self.intention = intention
        self.snmp_port = port
        self.oid_dict = oid_lable_num()
        self.desc_dict = oid_lable_desc()
        self.class_dict = oid_lable_class()
        self.user = kwargs.get('user', '')  # snmpv3 用户
        self.level = kwargs.get('level', '')  # authPriv authNoPriv
        self.auth_protocol = kwargs.get('auth_protocol', '')  # md5 sha
        self.auth_pass = kwargs.get('auth_pass', '')
        self.priv_protocol = kwargs.get('priv_protocol', '')  # des aes
        self.priv_pass = kwargs.get('priv_pass', '')
        if self.version == '3c':
            self.version = 3
    # 执行方法缺少异常捕获，后续调用无法判断
    def walk_cmd(self, oid):
        (status, output) = subprocess.getstatusoutput(
            'snmpwalk -c ' + self.community + ' -v ' + self.version + ' ' + self.host + ':' + self.snmp_port + ' ' + oid)
        return output

    def walk_cmd_v3(self, oid):
        if self.level == 'authPriv':
            (status, output) = subprocess.getstatusoutput(
                'snmpwalk -v ' + self.version + ' -u ' + self.user + ' -l ' + self.level + ' -a ' + self.auth_protocol +
                ' -A ' + self.auth_pass + ' -x ' + self.priv_protocol + ' -X ' + self.priv_pass + ' ' +
                self.host + ':' + self.snmp_port + ' ' + oid)
            return output
        elif self.level == 'authNoPriv':
            (status, output) = subprocess.getstatusoutput(
                'snmpwalk -v ' + self.version + ' -u ' + self.user + ' -l ' + self.level + ' -a ' + self.auth_protocol +
                ' -A ' + self.auth_pass + ' ' + self.host + ':' + self.snmp_port + ' ' + oid)
            return output
        elif self.level == 'noAuthNoPriv':
            (status, output) = subprocess.getstatusoutput(
                'snmpwalk -v ' + self.version + ' -u ' + self.user + ' -l ' + self.level + ' ' +
                self.host + ':' + self.snmp_port + ' ' + oid)
            return output

    def get_basic_info(self, lable, output):
        basic_info_dict = dict()
        vlan_name_dict = dict()
        if_descr_dict = dict()
        if_speed_dict = dict()
        if_mac_dict = dict()
        if_state_dict = dict()
        if lable == 'sysName':
            basic_info_dict['sys_name'] = output.split(': ')[-1].strip('"')
        elif lable == 'sysDesc':
            basic_info_dict['ios_version'] = output.split(',')[2]
        elif lable == 'sysUptime':
            basic_info_dict['sys_uptime'] = output.split(')')[1].strip()
        elif lable == 'chassisModel':
            basic_info_dict['model'] = output.split('"')[1]
        elif lable == 'entPhysicalSerialNum':
            basic_info_dict['serial_num'] = ''
            for item in output.split('\n'):
                if 'string' in item.lower():
                    basic_info_dict['serial_num'] = output.split('"')[1]
        elif lable == 'vtpVlanName':
            for item in output.split('\n'):
                entry = item.split(' = ')
                vlan_port = entry[0].split('.')[-1]
                vlan_name = entry[1].split('"')[1]
                vlan_name_dict[vlan_port] = vlan_name
            basic_info_dict['vlan_name_dict'] = vlan_name_dict
        elif lable == 'ifAdminStatus':
            for item in output.split('\n'):
                entry = item.split(' = ')
                if_port = entry[0].split('.')[-1]
                if_state = entry[1].split(': ')[1]
                if_state_dict[if_port] = if_state
            basic_info_dict['if_state_dict'] = if_state_dict
        elif lable == 'ifSpeed':
            for item in output.split('\n'):
                entry = item.split(' = ')
                if_port = entry[0].split('.')[-1]
                if_speed = entry[1].split(': ')[1]
                if_speed_dict[if_port] = if_speed
            basic_info_dict['if_speed_dict'] = if_speed_dict
        elif lable == 'ifPhysAddress':
            for item in output.split('\n'):
                entry = item.split(' = ')
                if_port = entry[0].split('.')[-1]
                if 'string:' in item.lower():
                    hex_mac = entry[1].split(' ')[1:7]
                    if_mac = ':'.join(hex_mac)
                else:
                    if_mac = ''
                if_mac_dict[if_port] = if_mac
            basic_info_dict['if_mac_dict'] = if_mac_dict
        elif lable == 'ifDescr':
            for item in output.split('\n'):
                entry = item.split(' = ')
                if_port = entry[0].split('.')[-1]
                if_descr = entry[1].split(': ')[-1].strip('"')
                if_descr_dict[if_port] = if_descr
            basic_info_dict['if_descr_dict'] = if_descr_dict
        return basic_info_dict

    def get_loc(self):
        (status, output) = subprocess.getstatusoutput('snmpwalk -v %s -c %s %s:%s %s -Cc' 
            %(self.version, self.community, self.host, self.snmp_port, self.oid_dict['lldpLocChassisId']))
        loc_info = output.split('\n')
        if 'No Such' in loc_info[0] or 'Timeout' in loc_info[0]:
            chassisID = None
        else:
            chassisID = loc_info[0].split(':')[-1].strip()
        return chassisID

    def get_vlan_state(self):
        vlan_state_dict = dict()
        vlan_info = self.walk_cmd(self.oid_dict['vtpVlanState'])
        for item in vlan_info.split('\n'):
            entry = item.split(' = ')
            vlan_port = entry[0].split('.')[-1]
            vlan_state = entry[1].split(': ')[1]
            vlan_state_dict[vlan_port] = vlan_state
        return vlan_state_dict

    def get_ifname(self, port):
        port_ifname_dict = dict()
        (status, output) = subprocess.getstatusoutput('snmpwalk -c ' + self.community + '@' + port + ' -v ' 
            + self.version + ' ' + self.host + ':' + self.snmp_port + ' ' + self.oid_dict['ifDescr'])
        for item in output.split('\n'):
            entry = item.split(' = ')
            port = entry[0].split('.')[-1]
            ifname = entry[1].split(': ')[-1].strip('"')
            port_ifname_dict[port] = ifname
        return port_ifname_dict

    def port_ifname(self):
        vlan_state_dict = self.get_vlan_state()
        ifname_dict = dict()
        for port in vlan_state_dict.keys():
            port_ifname_dict = self.get_ifname(port)
            ifname_dict.update(port_ifname_dict)
        return ifname_dict

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
        vlan_state_dict = self.get_vlan_state()
        for (port, state) in vlan_state_dict.items():
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


    def hex2dec_ip(self, hex_list):
        dec_list = list()
        ip_addr = str()
        for item in hex_list:
            try:
                dec_num = str(int(item, 16))
            except ValueError as e:
                jklog('error', e)
            else:
                dec_list.append(dec_num)
        ip_addr = '.'.join(dec_list)
        return ip_addr

    def get_topinfo(self, info_list):
        top_info = dict()
        ifname_dict = self.port_ifname()
        ip2mac_dict = self.get_arp()
        for item in info_list:
            ip_mac = dict()
            entry = item.split('=')
            port = entry[0].split('.')[-2]
            hex_list = entry[1].split(' ')[2:6]
            dec_ip = self.hex2dec_ip(hex_list)
            ip_mac['remote_ip'] = dec_ip
            if dec_ip in ip2mac_dict.keys():
                ip_mac['remote_mac'] = ip2mac_dict[dec_ip]
            else:
                ip_mac['remote_mac'] = None
            ifname = ifname_dict[port]
            top_info[ifname] = ip_mac
        return ip2mac_dict, top_info

    def get_data(self):
        info_list = list()
        err_msg_list = list()
        data_dict = dict()
        cdp_dict = dict()
        arp_dict = dict()
        cdp_topinfo = dict()
        basic_info_dict = dict()
        data_dict['start_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_dict['target'] = self.host
        data_dict['result'] = dict()
        data_dict['status'] = 'SUCCESS'
        
        if self.intention == 'topinfo':
            cache_info = self.walk_cmd(self.oid_dict['cdpCacheAddress']) if self.version == '2c' else \
                self.walk_cmd_v3(self.oid_dict['cdpCacheAddress'])

            if 'Timeout' in cache_info or 'No Such' in cache_info:          
                data_dict['status'] = 'FAILURE'
                data_dict['err_msg'] = cache_info
                data_dict['result']['cdp_cache_address'] = None
            else:
                for item in cache_info.split('\n'):
                    if 'string:' in item.lower():
                        info_list.append(item)
                arp_dict, cdp_topinfo = self.get_topinfo(info_list)
                data_dict['result']['cdp_cache_address'] = cdp_topinfo
                data_dict['result']['arp_dict'] = arp_dict
            data_dict['result']['lldp_loc_chassisId'] = self.get_loc()
        elif self.intention == 'hdinfo':
            for lable in self.class_dict['basicInfo']:
                output = self.walk_cmd(self.oid_dict[lable]) if self.version == '2c' else \
                    self.walk_cmd_v3(self.oid_dict[lable])
                if 'Timeout' in output or 'No Such' in output:
                    err_msg_list.append("{} - {}".format(repr(lable),repr(output)))
                    jklog('error', "{} - {}".format(repr(lable),repr(output)))
                    # basic_info_dict[lable] = None
                else:
                    basic_info_dict.update(self.get_basic_info(lable, output))

            jklog('debug', basic_info_dict)
            
            if err_msg_list:
                # data_dict['status'] = 'FAILURE'
                data_dict['status'] = 'SUCCESS'
                data_dict['err_msg'] = err_msg_list

            basic_info_dict['if_dict'] = self.get_if(basic_info_dict)
            basic_info_dict['vlan_dict'] = self.get_vlan(basic_info_dict)
            basic_info_dict['if_count'] = len(basic_info_dict['if_dict'])
            basic_info_dict['vlan_count'] = len(basic_info_dict['vlan_dict'])
            basic_info_dict['manufacturer'] = 'cisco Systems, Inc.'
            del basic_info_dict['vlan_name_dict']
            del basic_info_dict['if_mac_dict']
            del basic_info_dict['if_speed_dict']
            del basic_info_dict['if_state_dict']
            del basic_info_dict['if_descr_dict']
            data_dict['result'] = basic_info_dict
        else:
            data_dict['status'] = 'FAILURE'
            data_dict['err_msg'] = 'The provided "' + self.intention + '" is not a valid intention.(topinfo/hdinfo)'
        data_dict['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        jklog('debug', data_dict)
        return True, data_dict

if __name__ == '__main__':
    snmpwalk = WalkApi('hexin1.1', '2c', '192.168.1.1', '161', 'topinfo')
    res = snmpwalk.get_data()
    #print(json.dumps(res,ensure_ascii=False))