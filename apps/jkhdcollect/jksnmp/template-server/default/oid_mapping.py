#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   oidmapping.py
@Time    :   2021/10/20 18:40
'''
# dell
from .config import *

oidMapping = {
    'base':{
        'manufacturer':{'describe': "制造厂商",'oid': racManufacturer},
        'sys_uptime':{'describe': "系统启动时间",'oid': sysUptime},
        'firmware_version':{'describe': "固件版本(FW)",'oid': racFirmwareVersion},
        'service_number':{'describe': "服务码(SN)",'oid': systemExpressServiceCode},
        'sys_name':{'describe': "系统名",'oid': sysName},
        'hostname':{'describe': "系统主机名",'oid': systemFQDN},
        'sys_desc':{'describe': "系统描述信息",'oid': sysDesc},
        'model_name':{'describe': "产品型号",'oid': systemModelName},
    },
    'cpu':{
        'state':{'describe': "CPU状态",'oid': processorDeviceStatus},
        'manu':{'describe': "CPU厂商",'oid': processorDeviceManufacturerName},
        'core':{'describe': "CPU插槽数",'oid': processorDeviceCoreCount},
        'name':{'describe': "CPU型号",'oid': processorDeviceBrandName}
    },
    'memory':{
        'state':{'describe': "内存状态",'oid': memoryDeviceStatus},
        'type':{'describe': "内存类型",'oid': memoryDeviceType},
        'size':{'describe': "内存大小",'oid': memoryDeviceSize},
        'manu':{'describe': "内存厂商",'oid': memoryDeviceManufacturerName},
        'speed':{'describe': "内存速率",'oid': memoryDeviceSpeed}
    },
    'fan':{
        'name':{'describe': "风扇名称",'oid': coolingDeviceLocationName},
        'state':{'describe': "风扇状态",'oid': coolingDeviceStatus},
        'speed':{'describe': "风扇转/分 ",'oid': coolingDeviceReading},
    },
    'disk':{
        'name':{'describe': "磁盘名称",'oid': physicalDiskDisplayName},
        'state':{'describe': "磁盘状态",'oid': physicalDiskState},
        'type':{'describe': "磁盘类型",'oid': physicalDiskMediaType},
        'size':{'describe': "磁盘大小",'oid': physicalDiskCapacityInMB},
    },
    'power':{
        'name':{'describe': "电源名称",'oid': powerSupplyLocationName},
        'state':{'describe': "电源状态",'oid': powerSupplyStatus},
        'type':{'describe': "电源类型",'oid': powerSupplyType},
    },
    'ip':{
        'name':{'describe': "接口名",'oid': ifDescr},
        'mac':{'describe': "接口MAC",'oid': ifPhyAddress},
        'state':{'describe': "接口状态",'oid': ifAdminStatus},
        'ip':{'describe': "电源类型",'oid': ipAdEntIfIndex},
    },
}

returnDataMapping = {
    "start_date": None,
    "target": None,
    "status": None,
    "result": None,
    "result": None,
    "end_date": None,
}