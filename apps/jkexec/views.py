#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   views.py
@Time    :   2020/05/29 16:05:15
'''

import json
import  logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from datetime import datetime
# from django.http import QueryDict
from django.http import JsonResponse
from celery import chain
from coreapi import Field
from jksreExecEngine.jktask import execute, execute_sync
from jkexec.exectools.ssh_key_copy import add_sshKey
from .serializers import ExecJobSerializer, RegisterSerializer
from utils.jklog import jklog
from utils.jkcode import jkreturn
from utils.elasticApi.es import ElasticHandle
from utils.job_num import generate_exec_num

logger = logging.getLogger('console')


class TaskTrigger(mixins.CreateModelMixin, viewsets.GenericViewSet):

    serializer_class = ExecJobSerializer

    # permission_classes = (IsAuthenticated,)

    def create(self, request):
        """exec_data
        [
            {
                "exec_main": "cmd.script",
                "exec_type": "command",
                "operator": "zili",
                "task_num": "line-1548",
                "node_num": "01",
                "log_server": 0,
                "exec_async": 1,
                "exec_option": {
                    "location": "remote",
                    "runtime_type": "shell",
                    "component": "ansible",
                    "targets": [
                        {
                            "ip": "192.168.3.82",
                            "password": "2KozIlHoIybYMskAkScS3Q==",
                            "port": 22,
                            "username": "root"
                        },
                        {
                            "ip": "192.168.3.83",
                            "username": "root",
                            "port": "22",
                            "password": "u2KWCkq02vScvLEEZ6lvdA=="
                        }
                    ],
                    "args": "__jk_script_os_info.sh",
                    "script_args": ""
                }
            }
        ]
        """
        get_serializer = self.get_serializer(data=request.data)
        get_serializer.is_valid(raise_exception=True)
        param_data = get_serializer.validated_data

        logger.debug(param_data.get('exec_data'))

        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Generate Task chain
        chains = []
        result = []
        job_list = param_data.get('exec_data')
        logs = None

        for job in job_list:
            # Generate Custom Job Number
            job_num = generate_exec_num(job.get('exec_type'))
            if not job_num:
                return Response({'data': {'job_num': 'Failed to generate job_num'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            job['job_num'] = job_num

            exec_async = job.get('exec_async')
            is_extend_args = job.get('extend_args')
            log_server = job.get('log_server', 1)


            if exec_async == 0:
                logger.debug('sync task start ...')
                success, code, res = execute_sync(job_data=job)
                result.append(res)
            else:
                log = '[{}: INFO/{}] Job({}) is PENDING'.format(current_date, job.get('exec_type'), job_num)

                logger.debug(log)

                result.append(job_num)

                if log_server == 1:
                    es_handle = ElasticHandle()
                    if not es_handle.es_health():
                        return Response({'data': 'ES ConnectionError'}, status=status.HTTP_200_OK)
                    es_handle.generate_signal(job_num=job_num, log=log)
                else:
                    #  dpa 取值对接mq，日志需传递到结果中
                    job['logs'] = log + '\n'
                    # 可添加MQ消息推送-任务状态为PENDING

                # Generate Celery Chain Task Logic
                if is_extend_args == 1:
                    chains.append(execute.s(job_data=job))
                else:
                    chains.append(execute.si(job_data=job))
                logger.debug('async task')
        if chains:
            chain(*chains)()
            return Response({'data': result}, status=status.HTTP_200_OK)
        return Response({'data': result}, status=status.HTTP_200_OK)


class RegisterResource(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ssh key register

    """
    serializer_class = RegisterSerializer

    # permission_classes = (IsAuthenticated,)

    def create(self, request):
        get_serializer = self.get_serializer(data=request.data)
        get_serializer.is_valid(raise_exception=True)
        param_data = get_serializer.validated_data

        success, result = add_sshKey(data=param_data)

        if not success:
            # return Response({'code':200,'msg':'','data': result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return JsonResponse(jkreturn(1001, repr(result)))

        result = result.decode('utf-8')

        if 'Permission denied' in result:
            result = 'Permission denied (publickey,gssapi-keyex,gssapi-with-mic,password)'
            return JsonResponse(jkreturn(1001, repr(result)))

        if 'Connection refused' in result or 'Bad port' in result:
            result = 'connect to host {} port {}: Connection refused'.format(param_data.get('ip'), param_data.get('port'))
            return JsonResponse(jkreturn(1001, repr(result)))

        # return Response({'code':200,'msg':'','data': 'success'}, status=status.HTTP_200_OK)
        return JsonResponse(jkreturn(1000, repr(result)))
