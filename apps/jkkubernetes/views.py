#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   views.py
@Time    :   2020/11/12 15:36:32
'''

import os
import json
from . import serializers
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
from utils.jklog import jklog
from utils.elasticApi.es import ElasticHandle
from utils.job_num import generate_exec_num
from utils.jkaes import jkAes
from jkkubernetes.k8sApi.get_resource import GetResourceHandle
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.http import JsonResponse


class jkK8s(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """同步k8s资源
    ARGS:
        auth_data: 认证信息JSON串
        {
            "task_num": "xxxxxxxxxx",
            "task_type": "resource"  
            "exec_type": "get", // get  create delete 
            "exec_async": 0,
            "targets": [
                {
                    "cluster": "jk",
                    "kind": "pod",
                    "kubeconfig":"---------"
                },
                {
                    "cluster": "zili",
                    "kind": "node",
                    "kubeconfig":"---------"
                }
            ]
        }
    """

    serializer_class = serializers.k8sAuthSerializers

    # permission_classes = (IsAuthenticated,)

    def create(self, request):

        jklog('file', __file__)

        get_serializer = self.get_serializer(data=request.data)
        get_serializer.is_valid(raise_exception=True)
        param_data = get_serializer.validated_data

        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        current_dir = os.path.dirname(os.path.abspath(__file__))

        data = None
        auth_data = param_data.get('auth_data')
        task_type = param_data.get('task_type')

        jklog('debug', auth_data)

        if not auth_data['targets']:
            return Response({'data': 'Param target required!'}, status=status.HTTP_400_BAD_REQUEST)

        # 异步入口
        if 'exec_async' not in auth_data or auth_data.get('exec_async') == 1:
            return Response({'data': '异步开发中..'}, status=status.HTTP_200_OK)

        # 同步处理
        else:
            # 获取资源
            data_list = list()
            if ('resource' == auth_data.get('task_type') and 'get' == auth_data.get('exec_type')):
                for target in auth_data['targets']:
                    if 'node' == target['kind']:
                        success, data = GetResourceHandle(cluster_name=target['cluster'],
                                                          conf_content=target['kubeconfig'],
                                                          kind=target['kind']).nodes()
                    if 'pod' == target['kind']:
                        success, data = GetResourceHandle(cluster_name=target['cluster'],
                                                          conf_content=target['kubeconfig'],
                                                          kind=target['kind']).pods()
                    if 'service' == target['kind']:
                        success, data = GetResourceHandle(cluster_name=target['cluster'],
                                                          conf_content=target['kubeconfig'],
                                                          kind=target['kind']).services()
                    if 'namespace' == target['kind']:
                        success, data = GetResourceHandle(cluster_name=target['cluster'],
                                                          conf_content=target['kubeconfig'],
                                                          kind=target['kind']).namespace()
                    if 'deployment' == target['kind']:
                        success, data = GetResourceHandle(cluster_name=target['cluster'],
                                                          conf_content=target['kubeconfig'],
                                                          kind=target['kind']).deployment()
                    if 'replicaset' == target['kind']:
                        success, data = GetResourceHandle(cluster_name=target['cluster'],
                                                          conf_content=target['kubeconfig'],
                                                          kind=target['kind']).replicaset()
                    if 'daemonset' == target['kind']:
                        success, data = GetResourceHandle(cluster_name=target['cluster'],
                                                          conf_content=target['kubeconfig'],
                                                          kind=target['kind']).daemonset()
                    else:
                        jklog('error', 'kind类型不支持')
                        return Response({'data': data_list}, status=status.HTTP_200_OK)


                    data_list.append(data)

                return Response({'data': data_list}, status=status.HTTP_200_OK)
                # return Response({'data': eval(str(data_list))}, status=status.HTTP_200_OK)

            else:
                return Response({'data': 'Unsupported parameter task_type or exec_type'}, status=status.HTTP_200_OK)
