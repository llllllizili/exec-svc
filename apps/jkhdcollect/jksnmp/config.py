#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   config.py
@Time    :   2020/04/28 15:53:14
'''
# dell
def oid_lable_num():  
    oid_dict = dict()
    # 公用
    oid_dict['ipAdEntAddr']                 = '.1.3.6.1.2.1.4.20.1.1'                       # 管理地址
    oid_dict['ifPhysAddress']               = '.1.3.6.1.2.1.2.2.1.6'                        # mac地址
    oid_dict['sysDesc']                     = '.1.3.6.1.2.1.1.1.0'

    return oid_dict


def oid_lable_desc():
    oid_desc_dict = dict()
    oid_desc_dict['ipAdEntAddr']                    = u'管理地址'
    oid_desc_dict['ifPhysAddress']                  = u'网口MAC'
    oid_desc_dict['sysDesc']                        = u'系统描述'

    return oid_desc_dict


def oid_lable_class():
    oid_class_dict = dict()
    oid_class_dict['ipAdEntAddr']                    = u'ip'
    oid_class_dict['ifPhysAddress']                  = u'ip'
    oid_class_dict['sysDesc']                        = u'sys'

    return oid_class_dict