#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   exec_api.py
@Time    :   2021/05/8 09:15:39
'''

import importlib
from utils.jklog import jklog
from utils.elasticApi.es import ElasticHandle
from apps.jkhdcollect.adaption import get_classification


class IpmiDataCollect(object):
    '''
        hd ipmi数据同步
    '''

    def __init__(self, host, user, passwd, port, **kwargs):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.brand = kwargs.get('brand', '')
        self.model = kwargs.get('model', '')
        self.job_num = kwargs.get('job_num', '')
        self.log_server = kwargs.get('log_server', 1)
        self.es_handle = ElasticHandle()

    def ipmi_handler(self):

        jklog('file', '{} - IpmiDataCollect'.format(__file__))
        jklog('debug', 'ipmi host is : {}'.format(self.host))

        try:
            if self.brand:
                brand_lower = self.brand.lower()
                module = get_classification(self.model, 'ipmi')
                ipmitool = importlib.import_module(
                    "jkhdcollect.jkipmi.{}.{}.ipmitool".format(brand_lower, module)
                )
                jklog("info", "import {} {} module".format(brand_lower, module))
            else:
                from apps.jkhdcollect.jkipmi import ipmitool
                jklog("info", "import default hd ipmi module")
        except ImportError:
            from apps.jkhdcollect.jkipmi import ipmitool
            jklog("error", "import default hd ipmi module")

        success, data = ipmitool.IpmiApi(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            port=self.port
        ).reply()

        if success:
            if not self.job_num:
                jklog('success', '同步HD信息获取(ipmi)-成功')
                return True, data
            elif self.log_server == 1:
                self.es_handle.send_result(job_num=self.job_num, result=data, log=str(data))
        else:
            jklog('error', 'HD信息获取(ipmi)-失败')
        return success, data

    def ipmi_verify(self):

        jklog('file', '{} - IpmiDataCollect'.format(__file__))
        jklog('debug', 'ipmi host is : {}'.format(self.host))

        from apps.jkhdcollect.jkipmi import ipmitool
        jklog("info", "import default hd ipmi module")

        success, data = ipmitool.IpmiApi(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            port=self.port,
        ).ipmi_verify()

        if success:
            return True, data

        jklog('error', 'HD验证(ipmi)-失败')
        return False, data