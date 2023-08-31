#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   config.py
@Time    :   2021/10/20 18:40:14
'''

# 只需要看备注，更改oid即可，找不到的为空 如 systemOSName=None 或 systemOSName=''

# ip
ipAdEntIfIndex = '.1.3.6.1.2.1.4.20.1.2'
ifIndex = '.1.3.6.1.2.1.2.2.1.1'                        # 管理地址
ifAdminStatus = '.1.3.6.1.2.1.2.2.1.7'                  # 接口状态
ifPhyAddress = '.1.3.6.1.2.1.2.2.1.6'                   # 接口MAC
ifDescr = '.1.3.6.1.2.1.2.2.1.2'                        # 接口名  必填项 !!!! 

sysName = '.1.3.6.1.2.1.1.5.0'                          # 系统名
sysDesc = ''                          # 系统描述信息
sysUptime = '.1.3.6.1.2.1.1.3.0'                        # 系统启动时间

# 私有
systemModelName = '.1.3.6.1.4.1.674.10892.5.1.3.12'                 # 型号  (string)
sysUUID = None                # 型号  (string)
systemFQDN = '.1.3.6.1.4.1.674.10892.5.1.3.1'                       # 系统主机名 (string)
systemOSName = '.1.3.6.1.4.1.674.10892.5.1.3.6'                     # 操作系统 (string)
racFirmwareVersion = '.1.3.6.1.4.1.674.10892.5.1.1.8'               # 固件版本 FW version(string)
racManufacturer = '.1.3.6.1.4.1.674.10892.5.1.1.4.0'                # 制造商 (string)
systemExpressServiceCode = '.1.3.6.1.4.1.674.10892.5.1.3.3'         # 服务码
    # power    
powerSupplyLocationName = '.1.3.6.1.4.1.674.10892.5.4.600.12.1.15'  # 电源名称   必填项 !!!! 
powerSupplyType = '.1.3.6.1.4.1.674.10892.5.4.600.12.1.7'           # 电源类型
powerSupplyStatus = '.1.3.6.1.4.1.674.10892.5.4.600.12.1.5'         # 电源状态     
    # cpu
processorDeviceBrandName = '.1.3.6.1.4.1.674.10892.5.4.1100.30.1.23'  # CPU 型号   必填项 !!!!
processorDeviceStatus = '.1.3.6.1.4.1.674.10892.5.4.1100.30.1.5'    # 状态 
processorDeviceManufacturerName = '.1.3.6.1.4.1.674.10892.5.4.1100.30.1.8'      # CPU厂商
processorDeviceCoreCount = '.1.3.6.1.4.1.674.10892.5.4.1100.30.1.17'            # CPU插槽数
processorDeviceVersionName = '.1.3.6.1.4.1.674.10892.5.4.1100.30.1.16'          # 处理器版本
    # 内存 memory
memoryDeviceStatus = '.1.3.6.1.4.1.674.10892.5.4.1100.50.1.5'       # 内存状态
memoryDeviceSpeed = '.1.3.6.1.4.1.674.10892.5.4.1100.50.1.15'       # 内存速率
memoryDeviceType = '.1.3.6.1.4.1.674.10892.5.4.1100.50.1.7'         # 内存类型
memoryDeviceManufacturerName = '.1.3.6.1.4.1.674.10892.5.4.1100.50.1.21'    # 内存厂商
memoryDeviceSize = '.1.3.6.1.4.1.674.10892.5.4.1100.50.1.14'                # 内存大小
    #风扇 fan 
coolingDeviceLocationName = '.1.3.6.1.4.1.674.10892.5.4.700.12.1.8'     # 风扇名称   必填项 !!!!
coolingDeviceStatus = '.1.3.6.1.4.1.674.10892.5.4.700.12.1.5'           # 风扇状态
coolingDeviceReading = '.1.3.6.1.4.1.674.10892.5.4.700.12.1.6'          # 风扇转/分      
#     # 磁盘 disk
physicalDiskDisplayName = '1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.55'       # 磁盘名称     必填项 !!!!
physicalDiskCapacityInMB = '1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.11'      # 磁盘大小
physicalDiskState = '1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.4'              # 磁盘状态     
physicalDiskMediaType = '1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.35'         # 磁盘类型
