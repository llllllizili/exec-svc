#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   exec_api.py
@Time    :   2020/05/19 09:15:39
'''

import importlib
from utils.jklog import jklog
from utils.elasticApi.es import ElasticHandle
from jkhdcollect.adaption import get_classification


class SnmpDataCollect(object):
    '''
        hd snmp数据同步
    '''

    def __init__(self, community, version, host, intention, port='161', **kwargs):
        self.community = community if community else ''
        self.version = version
        self.host = host
        self.port = port
        self.intention = intention
        self.brand = kwargs.get('brand', '') if kwargs.get('brand', '') else None
        self.model = kwargs.get('model', '') if kwargs.get('model', '') else None
        self.job_num = kwargs.get('job_num', '') if kwargs.get('job_num', '') else None
        self.log_server = kwargs.get('log_server', 1)

        # 兼容v3
        self.user = kwargs.get('user', '')   # snmpv3 用户
        self.level = kwargs.get('secure_level', '')   # authPriv authNoPriv
        self.auth_protocol = kwargs.get('auth_protocol', '')    # md5 sha
        self.auth_pass = kwargs.get('auth_passphrase', '')
        self.priv_protocol = kwargs.get('priv_protocol', '')    # des aes
        self.priv_pass = kwargs.get('priv_passphrase', '')

        self.es_handle = ElasticHandle()

    def snmp_handler(self):
        jklog('file', '{} - SnmpDataCollect'.format(__file__))
        jklog('debug', 'snmp host is : {}'.format(self.host))

        try:
            if self.brand:
                brand_lower = self.brand.lower()
                module = get_classification(self.model, 'snmp')
                snmpwalk = importlib.import_module(
                    "jkhdcollect.jksnmp.{}.{}.snmpwalk".format(brand_lower, module)
                )
                jklog("info", "import {} {} module".format(brand_lower, module))
            else:
                from .jksnmp import snmpwalk
                jklog("info", "import default hd snmp module")
        except ImportError:
            from apps.jkhdcollect.jksnmp import snmpwalk
            jklog("error", "import default hd snmp module")
        if self.version == '2c':
            success, data = snmpwalk.WalkApi(
                community=self.community,
                version=self.version,
                host=self.host,
                port=self.port,
                intention=self.intention,
            ).get_data()
            if success:
                if self.log_server == 1 and self.job_num:  # 异步
                    self.es_handle.send_result(job_num=self.job_num, result=data, log=str(data))
                jklog('success', '同步HD信息获取(SNMP)-成功')
            else:
                jklog('error', 'HD信息获取(SNMP)-失败')

            return success, data
        if self.version == '3':
            success, data = snmpwalk.WalkApi(
                community=self.community,
                version=self.version,
                user=self.user,
                level=self.level,
                host=self.host,
                port=self.port,
                intention=self.intention,
                auth_protocol=self.auth_protocol,
                auth_pass=self.auth_pass,
                priv_protocol=self.priv_protocol,
                priv_pass=self.priv_pass
            ).get_data()

            if success:
                if self.log_server == 1 and self.job_num:    #异步
                    self.es_handle.send_result(job_num=self.job_num, result=data, log=str(data))
                jklog('success', '同步HD信息获取(SNMP)-成功')
            else:
                jklog('error', 'HD信息获取(SNMP)-失败')

            return success, data

    def snmp_verify(self):

        jklog('file', '{} - SnmpDataCollect'.format(__file__))
        jklog('debug', 'snmp host is : {}'.format(self.host))

        from apps.jkhdcollect.jksnmp import snmpwalk
        jklog("info", "import default hd snmp module")

        success, data = snmpwalk.WalkApi(
            community=self.community,
            version=self.version,
            host=self.host,
            port=self.port,
            intention='verify',
            user=self.user,
            level=self.level,
            auth_protocol=self.auth_protocol,
            auth_pass=self.auth_pass,
            priv_protocol=self.priv_protocol,
            priv_pass=self.priv_pass
        ).com_verify()

        if success:
            return True, data

        jklog('error', 'HD验证(SNMP)-失败')
        return False, repr(data)