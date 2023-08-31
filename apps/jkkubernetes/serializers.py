#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   serializers.py
@Time    :   2020/11/12 15:37:35
'''

import json
from rest_framework import serializers

# snmp 同步输入参数序列化
class k8sAuthSerializers(serializers.Serializer):
    """
    auth信息
    """
    auth_data = serializers.JSONField(label="auth_data", help_text='认证信息,JSON',required=True)


