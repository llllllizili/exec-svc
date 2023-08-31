#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   ruijie/default/config.py
@Time    :   2020/08/17
'''

def oid_lable_num():  
    oid_dict = dict()
    # 公用
    oid_dict['ipAdEntAddr']                 = '.1.3.6.1.2.1.4.20.1.1'                       # 管理地址
    oid_dict['ifDescr']                     = '.1.3.6.1.2.1.2.2.1.2'                        # 接口名
    oid_dict['ifAdminStatus']               = '.1.3.6.1.2.1.2.2.1.7'                        # 接口状态
    oid_dict['ifPhysAddress']               = '.1.3.6.1.2.1.2.2.1.6'                        # 接口MAC

    oid_dict['SysName']                     = '.1.3.6.1.2.1.1.5.0'                          # 系统名
    oid_dict['SysDesc']                     = '.1.3.6.1.2.1.1.1.0'                          # 系统描述信息
    oid_dict['SysUptime']                   = '.1.3.6.1.2.1.1.3.0'                          # 系统启动时间

    #私有
    oid_dict['lldpRemChassisId']            = '1.0.8802.1.1.2.1.4.1.1.5'
    oid_dict['lldpLocChassisId']            = '1.0.8802.1.1.2.1.3.2'

    return oid_dict


def oid_lable_desc():
    desc_dict = dict()

    desc_dict['ipAdEntAddr']                    = u'管理地址'
    desc_dict['ifDescr']                        = u'网口名'
    desc_dict['ifAdminStatus']                  = u'网口状态'
    desc_dict['ifPhysAddress']                  = u'网口MAC'

    desc_dict['SysName']                        = u'系统名'
    desc_dict['SysDesc']                        = u'系统描述'
    desc_dict['SysUptime']                      = u'系统启动时间' 

    desc_dict['lldpLocChassisId']               = u'此设备机架ID'
    desc_dict['lldpRemChassisId']               = u'远程设备机架ID'

    return desc_dict