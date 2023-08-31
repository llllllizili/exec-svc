'''
@File    :   config.py
@Time    :   2021/03/19 17:24:14
'''

import subprocess
import chardet
from utils.jklog import jklog
from .config import base_info
from .config import hardware_info

class IpmiApi:
    def __init__(self, host, user, passwd, port):
        self.base_info = base_info(host=host, user=user, passwd=passwd, port=port)
        self.hardware_info = hardware_info(host=host, user=user, passwd=passwd, port=port)

    def ipmirun(self, cmd):
        ret = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        if ret.returncode == 0:
            return ret.stdout
        else:
            jklog('error', ret.stderr)
            return ret.stderr

    def reply(self):
        exec_data = list()
        base = dict()
        product_name = self.ipmirun(self.base_info['product_name']).decode('utf-8')
        fw = self.ipmirun(self.base_info['fw']).decode('utf-8')
        encoded = chardet.detect(self.ipmirun(self.base_info['sn']))['encoding']
        sn = self.ipmirun(self.base_info['sn']).decode(encoded)
        uuid = self.ipmirun(self.base_info['uuid']).decode('utf-8')
        mfg = self.ipmirun(self.base_info['mfg']).decode('utf-8')
        time = self.ipmirun(self.base_info['time']).decode('utf-8')
        os_name = self.ipmirun(self.base_info['os_name']).decode('utf-8')
        mac = self.ipmirun(self.base_info['mac']).decode('utf-8')
        addr = self.ipmirun(self.base_info['addr']).decode('utf-8')

        # 风扇信息
        fans = self.ipmirun(self.hardware_info['fans']).decode('utf-8')
        fans_list = list()
        for fan in fans.strip().split('\n'):
            fan_info = dict()
            fan_info['name'] = fan.split('|')[0]
            fan_info['speed'] = fan.split('|')[1]
            fan_info['status'] = fan.split('|')[2]
            fans_list.append(fan_info)
        base['fans'] = fans_list

        # 电源信息
        powers = self.ipmirun(self.hardware_info['power']).decode('utf-8')
        powers_list = list()
        for power in powers.strip().split('\n'):
            power_info = dict()
            power_info['name'] = power.split('|')[0]
            power_info['voltage'] = power.split('|')[1]
            power_info['status'] = power.split('|')[2]
            powers_list.append(power_info)
        base['powers'] = powers_list

        # 内存信息
        mems = self.ipmirun(self.hardware_info['mem']).decode('utf-8')
        mems_list = list()
        for mem in mems.strip().split('\n'):
            mem_info = dict()
            mem_info['name'] = mem.split('|')[0]
            mem_info['temperature'] = mem.split('|')[1]
            mem_info['status'] = mem.split('|')[2]
            mems_list.append(mem_info)
        base['mem'] = mems_list

        # cpu信息
        cpus = self.ipmirun(self.hardware_info['cpu']).decode('utf-8')
        cpus_list = list()
        for cpu in cpus.strip().split('\n'):
            cpu_info = dict()
            cpu_info['name'] = cpu.split('|')[0]
            cpu_info['temperature'] = cpu.split('|')[1]
            cpu_info['status'] = cpu.split('|')[2]
            cpus_list.append(cpu_info)
        base['cpus'] = cpus_list

        # 磁盘信息
        disks = self.ipmirun(self.hardware_info['disk']).decode('utf-8')
        disks_list = list()
        for disk in disks.strip().split('\n'):
            disk_info = dict()
            disk_info['name'] = disk.split('|')[0]
            disk_info['temperature'] = disk.split('|')[1]
            disk_info['status'] = disk.split('|')[2]
            disks_list.append(disk_info)
        base['disks'] = disks_list


        base['product_name'] = product_name
        base['fw'] = fw
        base['sn'] = sn
        base['uuid'] = uuid
        base['mfg'] = mfg
        base['time'] = time
        base['os_name'] = os_name
        base['addr'] = addr
        base['mac'] = mac

        exec_data.append(base)
        jklog('info', exec_data)

        return True, exec_data


if __name__ == '__main__':
    ipmiapi = IpmiApi(host='192.168.5.24', user='root', passwd='123qweASD', port='623').reply()
    print(ipmiapi)