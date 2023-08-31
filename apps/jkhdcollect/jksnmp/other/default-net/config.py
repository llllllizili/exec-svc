#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   other/default/config.py
@Time    :   2020/08/17
'''

def oid_lable_num():  
    oid_dict = dict()
    # 公用
    # oid_dict['ipAdEntAddr']                 = '.1.3.6.1.2.1.4.20.1.1'
    oid_dict['ifDescr']                     = '.1.3.6.1.2.1.2.2.1.2'
    oid_dict['ifSpeed']                     = '.1.3.6.1.2.1.2.2.1.5'
    oid_dict['ifAdminStatus']               = '.1.3.6.1.2.1.2.2.1.7'
    oid_dict['ifPhysAddress']               = '.1.3.6.1.2.1.2.2.1.6'

    oid_dict['sysName']                     = '.1.3.6.1.2.1.1.5.0'
    oid_dict['sysDesc']                     = '.1.3.6.1.2.1.1.1.0'
    oid_dict['sysUptime']                   = '.1.3.6.1.2.1.1.3.0'
    
    oid_dict['ipNetToMac']                  = '.1.3.6.1.2.1.4.22.1.2'


    return oid_dict


def oid_lable_desc():
    desc_dict = dict()

    # desc_dict['ipAdEntAddr']                    = u'管理地址'
    desc_dict['ifDescr']                        = u'网口名'
    desc_dict['ifSpeed']                        = u'网口速率（bps）'
    desc_dict['ifAdminStatus']                  = u'网口状态'
    desc_dict['ifPhysAddress']                  = u'网口MAC'

    desc_dict['sysName']                        = u'系统名'
    desc_dict['sysDesc']                        = u'系统描述'
    desc_dict['sysUptime']                      = u'系统启动时间'

    desc_dict['ipNetToMac']                     = u'交换机ARP表'

    return desc_dict

def oid_lable_class():
    class_dict = dict()
    
    class_dict['basicInfo'] = ['sysName',
                               'sysDesc',
                               'sysUptime',
                            #    'ipNetToMac',
                               'ifSpeed',
                               'ifDescr',
                               'ifAdminStatus',
                               'ifPhysAddress'
                               ]

    return class_dict