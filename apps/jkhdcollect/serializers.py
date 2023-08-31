#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   serializers.py
@Time    :   2020/07/23 10:41:45
'''


import json
from rest_framework import serializers


# snmp 同步输入参数序列化
class snmpAuthSerializers(serializers.Serializer):
    """
    auth信息
    """
    auth_data = serializers.JSONField(label="auth_data", help_text='认证信息,JSON',required=True)

class FetchHDDeviceList(serializers.Serializer):
    """
    获取硬件兼容列表
    """
    brand = serializers.CharField(label='brand', help_text='品牌', required=True)
    way = serializers.CharField(label='way', help_text='同步方式', required=True)

