#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   views.py
@Time    :   2020/07/23 10:38:07
'''

from . import serializers
from rest_framework import status
from rest_framework.response import Response
from utils.jklog import jklog
from utils.elasticApi.es import ElasticHandle
from utils.job_num import generate_exec_num
from utils.jkaes import jkAes

from rest_framework import viewsets, mixins

# snmp
from jkhdcollect.adaption import hd_adaption  # 硬件适配信息
from .jksnmp.collect_api import SnmpDataCollect
from .jkipmi.ipmicollect import IpmiDataCollect  # 同步使用
from jksreExecEngine.jktask import collect_async  # 异步使用


class jkCollectSync(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """同步硬件数据
    ARGS:
        auth: 认证信息JSON串
        {
            "task_num": "cmdp_xxxxxxx",
            "exec_type": "snmp",
            "exec_async": 0,
            "targets": [
                {
                    "brand": "dell",
                    "model": "r730",
                    "community": "xxx",
                    "version": "2c",
                    "host": "192.168.5.20",
                    "port": "161"
                },
                {
                    "brand": "dell",
                    "model": "r730",
                    "community": "xxx",
                    "version": "2c",
                    "host": "192.168.5.20",
                    "port": "161"
                }
            ]
        }
    """

    serializer_class = serializers.snmpAuthSerializers

    # permission_classes = (IsAuthenticated,)

    def create(self, request):

        get_serializer = self.get_serializer(data=request.data)
        get_serializer.is_valid(raise_exception=True)
        post_data = get_serializer.validated_data
        jkaes = jkAes()
        result = list()

        jklog('file', __file__)
        jklog('debug', post_data.get('auth_data'))

        auth_data = post_data.get('auth_data')
        log_server = auth_data.get('log_server', 1)
        task_num = auth_data['task_num']
        if not auth_data:
            return Response({'data': 'Param auth_data required!'}, status=status.HTTP_400_BAD_REQUEST)

        if auth_data['exec_type'] == 'snmp':
            # async
            if 'exec_async' not in auth_data or auth_data['exec_async'] == 1:
                for auth in auth_data['targets']:
                    auth['log_server'] = log_server
                    auth['task_num'] = task_num
                    job_num = generate_exec_num(auth_data['exec_type'])
                    if not job_num:
                        return Response({'data': {'job_num': 'Failed to generate job_num'}},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    auth['job_num'] = job_num
                    result.append(job_num)
                    jklog('debug', 'job num is : {}'.format(job_num))

                    if log_server == 1:
                        es_handle = ElasticHandle()
                        if not es_handle.es_health():
                            return Response({'data': 'ES ConnectionError'}, status=status.HTTP_200_OK)
                        es_handle.generate_signal(job_num=job_num, log=None)

                    collect_async.delay(job_data=auth)
            else:
                # sync
                for auth in auth_data['targets']:
                    jklog('debug', auth)
                    if auth['intention'] == 'verify':
                        success, data = SnmpDataCollect(
                            community=jkaes.decrypt(auth['community']) if 'community' in auth else None,
                            version=auth['version'],
                            host=auth['host'],
                            port=auth['port'],
                            user=auth['user'] if 'user' in auth else None,
                            intention=auth['intention'],
                            secure_level=auth['secure_level'] if 'secure_level' in auth else None,
                            auth_protocol=auth['auth_protocol'] if 'auth_protocol' in auth else None,
                            auth_passphrase=auth['auth_passphrase'] if 'auth_passphrase' in auth else None,
                            priv_protocol=auth['priv_protocol'] if 'priv_protocol' in auth else None,
                            priv_passphrase=auth['priv_passphrase'] if 'priv_passphrase' in auth else None
                        ).snmp_verify()
                    else:
                        success, data = SnmpDataCollect(
                            community=jkaes.decrypt(auth['community']) if 'community' in auth else None,
                            version=auth['version'],
                            host=auth['host'],
                            port=auth['port'],
                            user=auth['user'] if 'user' in auth else None,
                            secure_level=auth['secure_level'] if 'secure_level' in auth else None,
                            auth_protocol=auth['auth_protocol'] if 'auth_protocol' in auth else None,
                            auth_passphrase=auth['auth_passphrase'] if 'auth_passphrase' in auth else None,
                            priv_protocol=auth['priv_protocol'] if 'priv_protocol' in auth else None,
                            priv_passphrase=auth['priv_passphrase'] if 'priv_passphrase' in auth else None,
                            intention=auth['intention'],
                            brand=auth['brand'] if 'brand' in auth else '',
                            model=auth['model'] if 'model' in auth else '',
                        ).snmp_handler()

                    result.append(data)
            return Response({'data': result}, status=status.HTTP_200_OK)

        if auth_data['exec_type'] == 'ipmi':
            # async
            if 'exec_async' not in auth_data or auth_data['exec_async'] == 1:
                for auth in auth_data['targets']:
                    auth['log_server'] = log_server
                    auth['task_num'] = task_num
                    job_num = generate_exec_num(auth_data['exec_type'])
                    if not job_num:
                        return Response({'data': {'job_num': 'Failed to generate job_num'}},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    auth['job_num'] = job_num
                    result.append(job_num)
                    jklog('debug', 'job num is : {}'.format(job_num))

                    if log_server == 1:
                        es_handle = ElasticHandle()
                        if not es_handle.es_health():
                            return Response({'data': 'ES ConnectionError'}, status=status.HTTP_200_OK)
                        es_handle.generate_signal(job_num=job_num, log=None)

                    collect_async.delay(job_data=auth)
            else:
                # sync
                for auth in auth_data['targets']:
                    jklog('debug', auth)
                    if auth['intention'] == 'verify':
                        success, data = IpmiDataCollect(
                            passwd=jkaes.decrypt(auth['passwd']),
                            user=auth['user'],
                            host=auth['host'],
                            port=auth['port'],
                        ).ipmi_verify()
                    else:
                        success, data = IpmiDataCollect(
                            passwd=jkaes.decrypt(auth['passwd']),
                            user=auth['user'],
                            host=auth['host'],
                            port=auth['port'],
                            brand=auth['brand'] if 'brand' in auth else '',
                            model=auth['model'] if 'model' in auth else '',
                        ).ipmi_handler()

                    result.append(data)

            return Response({'data': result}, status=status.HTTP_200_OK)

        return Response({'data': 'Param exec_type error!'}, status=status.HTTP_400_BAD_REQUEST)


class jkCollectAdaption(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """获取硬件适配列表
    ARGS:
        "auth_data": 认证信息JSON串
        {
            "task_num": "cmdp_xxxxxxx",
            "classification": "server",
            "manufacturer": "dell"
        }
    """

    serializer_class = serializers.snmpAuthSerializers

    def create(self, request):

        result = list()
        jkaes = jkAes()
        post_data = request.data
        auth_data = post_data['auth_data']

        jklog('file', __file__)

        if not auth_data:
            return Response({'data': 'Param "auth_data" required!'}, status=status.HTTP_400_BAD_REQUEST)

        if auth_data['protocol'] == 'snmp':
            try:
                adaption_dict = hd_adaption(auth_data['classification'], 'snmp')
                manu = auth_data['manufacturer']
            except KeyError:
                return Response({'data': 'Invalid hardware classification or manufacturer!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if manu in adaption_dict.keys():
                result = adaption_dict[manu]
                return Response({'data': result}, status=status.HTTP_200_OK)
            else:
                result = list(adaption_dict.keys())
                return Response({'data': result}, status=status.HTTP_200_OK)
        elif auth_data['protocol'] == 'ipmi':
            try:
                adaption_dict = hd_adaption(auth_data['classification'], 'ipmi')
                manu = auth_data['manufacturer']
            except KeyError:
                return Response({'data': 'Invalid hardware classification or manufacturer!'},
                                status=status.HTTP_400_BAD_REQUEST)

            if manu in adaption_dict.keys():
                result = adaption_dict[manu]
                return Response({'data': result}, status=status.HTTP_200_OK)
            else:
                result = list(adaption_dict.keys())
                return Response({'data': result}, status=status.HTTP_200_OK)