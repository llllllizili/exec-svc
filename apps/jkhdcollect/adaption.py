#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   adaption.py
@Time    :   2021/05/08
'''

def hd_adaption(classification, protocol):

    #服务器适配信息
    server_dict = {
        'snmp':{
            'Dell': ['default','R730',],
            'H3C': ['default','R590'],
            'HPE': ['default','DL580','DL380'],
            'Inspur': ['default','NF5140','NF5270'],
            'IBM': ['default','X3650'],
            'template': ['server','network']
        },
        'ipmi': {
            'hp': ['ProLiant']
        }
    }

    #交换机适配信息
    switch_dict = {
        'snmp': {
            'Cisco': ['default','N7000','3560G'],
            'H3C': ['default','(L)S5120','S5820'],
            'Huawei': ['default','CE5855','CE12808','NE20E','NE40E','S5710','S9706','USG9520'],
            'Brocade': ['default','300'],
            'other': ["default-net"]
        },
        'ipmi': {

        }
    }

    #存储阵列适配信息
    storage_dict = {
        'snmp': {
            'HPE': ['default','P2000']
        },
        'ipmi': {

        }
    }

    if classification == 'server':
        return server_dict[protocol]
    elif classification == 'switch':
        return switch_dict[protocol]
    elif classification == 'storage':
        return storage_dict[protocol]
    else:
        return False

def get_classification(model, protocol):

    #根据型号获取要导入模块类型（default/default/storage_default）
    server_model = list()
    switch_model = list()
    storage_model = list()
    for item in hd_adaption('server', protocol).values():
        server_model.extend(item)
    for item in hd_adaption('switch', protocol).values():
        switch_model.extend(item)
    for item in hd_adaption('storage', protocol).values():
        storage_model.extend(item)

    if model in server_model:
        return model
    elif model in switch_model:
        return model
    elif model in storage_model:
        return model


if __name__ == '__main__':
    print(get_classification('P2000', 'snmp'))