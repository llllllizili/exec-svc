#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   config.py
@Time    :   2020/08/28
'''
# dell

def oid_lable_num():  
    oid_dict = dict()
    # 公用
    oid_dict['ipAdEntIfIndex']              = '.1.3.6.1.2.1.4.20.1.2'
    oid_dict['ifIndex']                     = '.1.3.6.1.2.1.2.2.1.1'                        # 管理地址
    oid_dict['ifAdminStatus']               = '.1.3.6.1.2.1.2.2.1.7'                        # 接口状态
    oid_dict['ifPhyAddress']                = '.1.3.6.1.2.1.2.2.1.6'                        # 接口MAC
    oid_dict['ifDescr']                     = '.1.3.6.1.2.1.2.2.1.2'                        # 接口名

    oid_dict['sysName']                     = '.1.3.6.1.2.1.1.5.0'                          # 系统名
    oid_dict['sysDesc']                     = '.1.3.6.1.2.1.1.1.0'                          # 系统描述信息
    oid_dict['sysUptime']                   = '.1.3.6.1.2.1.1.3.0'                          # 系统启动时间

    # 私有
    oid_dict['systemModelName']             = '.1.3.6.1.4.1.19046.11.1.1.5.2.1.5.0'              # 型号  (string)
    # power     
    oid_dict['powerSupplyType']             = '.1.3.6.1.4.1.19046.11.1.1.11.2.1.4'        # 电源类型
    oid_dict['powerSupplyStatus']           = '.1.3.6.1.4.1.19046.11.1.1.11.2.1.6'        # 电源状态     
    oid_dict['powerSupplyLocationName']     = '.1.3.6.1.4.1.19046.11.1.1.11.2.1.2'       # 电源名称       		

    oid_dict['systemFQDN']                  = '.1.3.6.1.4.1.19046.11.1.1.5.2.1.5.0'               # 系统主机名 (string)
    oid_dict['systemOSName']                = 'sysDescr.0'               # 操作系统 (string)
    oid_dict['racFirmwareVersion']          = '.1.3.6.1.4.1.19046.11.1.1.5.1.1.3.4'               # 固件版本 FW version(string)
    oid_dict['racManufacturer']             = '.1.3.6.1.4.1.19046.11.1.1.5.1.1.2.4'             # 制造商 (string)
    oid_dict['systemExpressServiceCode']    = '.1.3.6.1.4.1.19046.11.1.1.5.2.1.3'               # 服务码

    # cpu
    oid_dict['processorDeviceStatus']           = '.1.3.6.1.4.1.19046.11.1.1.5.20.1.11'    # 状态 
    oid_dict['processorDeviceManufacturerName'] = '.1.3.6.1.4.1.19046.11.1.1.5.20.1.6'    # CPU厂商
    oid_dict['processorDeviceCoreCount']        = '.1.3.6.1.4.1.19046.11.1.1.5.20.1.7'   # CPU插槽数
    oid_dict['processorDeviceVersionName']      = '.1.3.6.1.4.1.19046.11.1.1.5.20.1.3'   # 处理器版本
    oid_dict['processorDeviceBrandName']        = '.1.3.6.1.4.1.19046.11.1.1.5.20.1.12'   # CPU 型号
    # 内存
    oid_dict['memoryDeviceStatus']          = '.1.3.6.1.4.1.19046.11.1.1.5.21.1.8'       # 内存状态
    oid_dict['memoryDeviceSpeed']           = '.1.3.6.1.4.1.19046.11.1.1.5.21.1.9'      # 内存速率
    oid_dict['memoryDeviceType']            = '.1.3.6.1.4.1.19046.11.1.1.5.21.1.6'       # 内存类型
    oid_dict['memoryDeviceManufacturerName']= '.1.3.6.1.4.1.19046.11.1.1.5.21.1.3'      # 内存厂商
    oid_dict['memoryDeviceSize']            = '.1.3.6.1.4.1.19046.11.1.1.5.21.1.7'      # 内存大小
    #风扇
    oid_dict['coolingDeviceStatus']         = '.1.3.6.1.4.1.19046.11.1.1.3.2.1.10'        # 风扇状态
    oid_dict['coolingDeviceReading']        = '.1.3.6.1.4.1.19046.11.1.1.3.2.1.3'        # 风扇转/分      
    oid_dict['coolingDeviceLocationName']   = '.1.3.6.1.4.1.19046.11.1.1.3.2.1.2'        # 风扇名称
    # 磁盘
    oid_dict['physicalDiskCapacityInMB']    = '.1.3.6.1.4.1.19046.11.1.1.13.1.3.1.12'    # 磁盘大小
    oid_dict['physicalDiskState']           = '.1.3.6.1.4.1.19046.11.1.1.12.2.1.3'     # 磁盘状态     
    oid_dict['physicalDiskMediaType']       = '.1.3.6.1.4.1.19046.11.1.1.13.1.3.1.8'    # 磁盘类型
    oid_dict['physicalDiskDisplayName']     = '.1.3.6.1.4.1.19046.11.1.1.12.2.1.2'    # 磁盘名称    


    # oid_dict['eventLogRecord']                = '1.3.6.1.4.1.674.10892.5.4.300.40.1.5'         # 日志

    return oid_dict


def oid_lable_desc():
    oid_desc_dict = dict()
    oid_desc_dict['ipAdEntIfIndex']                 = u'管理地址'

    oid_desc_dict['sysName']                        = u'系统名'
    oid_desc_dict['sysDesc']                        = u'系统描述'
    oid_desc_dict['sysUptime']                      = u'系统启动时间' 

    oid_desc_dict['ifDescr']                        = u'网口名'
    oid_desc_dict['ifAdminStatus']                  = u'网口状态'
    oid_desc_dict['ifPhyAddress']                   = u'网口MAC'

    oid_desc_dict['powerSupplyStatus']              = u'电源名称'
    oid_desc_dict['powerSupplyLocationName']        = u'电源状态'
    oid_desc_dict['powerSupplyType']                = u'电源类型'

    oid_desc_dict['systemModelName']                = u'产品型号'
    oid_desc_dict['systemFQDN']                     = u'系统主机名'
    oid_desc_dict['systemOSName']                   = u'操作系统'
    oid_desc_dict['systemExpressServiceCode']       = u'服务码'
    oid_desc_dict['racFirmwareVersion']             = u'固件版本'
    oid_desc_dict['racManufacturer']                = u'制造商'

    oid_desc_dict['processorDeviceBrandName']       = u'CPU型号'
    oid_desc_dict['processorDeviceStatus']          = u'CPU状态'
    oid_desc_dict['processorDeviceManufacturerName']= u'CPU厂商'
    oid_desc_dict['processorDeviceCoreCount']       = u'CPU插槽数'
    oid_desc_dict['processorDeviceVersionName']     = u'处理器版本'

    oid_desc_dict['memoryDeviceManufacturerName']   = u'内存厂商'
    oid_desc_dict['memoryDeviceSize']               = u'内存大小'
    oid_desc_dict['memoryDeviceStatus']             = u'内存状态'
    oid_desc_dict['memoryDeviceSpeed']              = u'内存速率'
    oid_desc_dict['memoryDeviceType']               = u'内存类型'

    oid_desc_dict['coolingDeviceStatus']            = u'风扇状态'     
    oid_desc_dict['coolingDeviceLocationName']      = u'风扇名称'
    oid_desc_dict['coolingDeviceReading']           = u'风扇转/分'

    oid_desc_dict['physicalDiskDisplayName']        = u'磁盘名字'
    oid_desc_dict['physicalDiskState']              = u'磁盘状态'
    oid_desc_dict['physicalDiskMediaType']          = u'磁盘类型'
    oid_desc_dict['physicalDiskCapacityInMB']       = u'磁盘容量'

    return oid_desc_dict

def oid_lable_class():
    oid_class_dict = dict()
    oid_class_dict['ifIndex']                        = 'ip'
    oid_class_dict['ipAdEntIfIndex']                 = 'ip'
    oid_class_dict['ifAdminStatus']                  = 'ip'
    oid_class_dict['ifPhyAddress']                   = 'ip'
    oid_class_dict['ifDescr']                        = 'ip'

    oid_class_dict['sysName']                        = 'sys_name'
    oid_class_dict['sysDesc']                        = 'sys_desc'
    oid_class_dict['sysUptime']                      = 'sys_uptime'

    oid_class_dict['systemModelName']                = 'brand'
    oid_class_dict['systemFQDN']                     = 'hostname'
    oid_class_dict['systemOSName']                   = 'os_name'
    oid_class_dict['systemExpressServiceCode']       = 'service_number'
    oid_class_dict['racFirmwareVersion']             = 'firmware_version'
    oid_class_dict['racManufacturer']                = 'manufacturer'

    oid_class_dict['powerSupplyStatus']              = 'power'    
    oid_class_dict['powerSupplyLocationName']        = 'power'    
    oid_class_dict['powerSupplyType']                = 'power'  		

    oid_class_dict['processorDeviceBrandName']       = 'cpu'
    oid_class_dict['processorDeviceStatus']          = 'cpu'
    oid_class_dict['processorDeviceManufacturerName']= 'cpu'
    oid_class_dict['processorDeviceCoreCount']       = 'cpu'
    oid_class_dict['processorDeviceVersionName']     = 'cpu'
    
    oid_class_dict['memoryDeviceManufacturerName']   = 'memory'
    oid_class_dict['memoryDeviceSize']               = 'memory'
    oid_class_dict['memoryDeviceStatus']             = 'memory'
    oid_class_dict['memoryDeviceSpeed']              = 'memory'
    oid_class_dict['memoryDeviceType']               = 'memory'

    oid_class_dict['coolingDeviceStatus']            = 'fan'     
    oid_class_dict['coolingDeviceLocationName']      = 'fan'
    oid_class_dict['coolingDeviceReading']           = 'fan'

    oid_class_dict['physicalDiskDisplayName']        = 'disk'
    oid_class_dict['physicalDiskState']              = 'disk'
    oid_class_dict['physicalDiskCapacityInMB']       = 'disk'
    oid_class_dict['physicalDiskMediaType']          = 'disk'

    return oid_class_dict
