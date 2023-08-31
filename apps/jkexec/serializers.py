#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   serializers.py
@Time    :   2020/05/29 16:57:42
'''

import json
from rest_framework import serializers


class ExecJobSerializer(serializers.Serializer):
    """

    """
    exec_data = serializers.JSONField(label="exec_data", help_text='exec_data(json格式)',required=True)

    @staticmethod
    def validate_exec_data(data):

        if isinstance(data, str):
            try:
                data = eval(data)
            except NameError as e:
                raise serializers.ValidationError(
                    detail='Execute Job Request Data Incorrect format, Error: {}'.format(repr(e)),
                    code='invalid_parameter')
            except SyntaxError as e:
                raise serializers.ValidationError(
                    detail='Execute Job Request Data SyntaxError: {}'.format(repr(e)), code='syntax_error_parameter'
                )
            except Exception as e:
                raise serializers.ValidationError(
                    detail='Execute Job Request Data Exception: {}'.format(repr(e)), code='exception_parameter'
                )

        if type(data) is not list:
            raise serializers.ValidationError(detail='Execute Job Request Data Incorrect format, Must List',
                                              code='no_list_parameter')
        if not data:
            raise serializers.ValidationError(
                detail='No Execution data is Defined', code='no_job_data'
            )

        for o in data:
            if type(o) is not dict:
                raise serializers.ValidationError(
                    detail='Execute Job Request Object Must be Json data, Must Json', code='no_json_parameter'
                )

            if not o.get('exec_main'):
                raise serializers.ValidationError(
                    detail='Execute Job Request Object Attribute exec_main is Missing', code='attr_missing'
                )

            if not o.get('exec_type'):
                raise serializers.ValidationError(
                    detail='Execute Job Request Object Attribute exec_type is Missing', code='attr_missing'
                )

            if not o.get('exec_retry'):
                o['exec_retry'] = 0

            if not o.get('exec_async'):
                o['exec_async'] = 0

            if not o.get('operator') and o.get('operator') != '':
                raise serializers.ValidationError(
                    detail='Execute Job Request Object Attribute operator is Missing',
                    code='operator_missing'
                )

            if not o.get('exec_option'):
                raise serializers.ValidationError(
                    detail='Execute Job Request Object Attribute exec_option is Missing', code='exec_option_missing'
                )
            else:
                if type(o.get('exec_option')) is not dict:
                    raise serializers.ValidationError(
                        detail='Execute Job Request Object Attribute exec_option Incorrect format, Must Json',
                        code='no_json_exec_option'
                    )

                if o.get('exec_type') == 'api':
                    if not o.get('exec_option').get('method'):
                        raise serializers.ValidationError(
                            detail='Execute API Job Attribute method is Missing', code='api_method_missing'
                        )

                if o.get('exec_type') == 'command' or o.get('exec_type') == 'script':
                    # if not o.get('exec_option').get('runtime_type'):
                    #     raise serializers.ValidationError(
                    #         detail='Execute Command or Script Runtime Type was not specified',
                    #         code='runtime_type_missing'
                    #     )
                    if not o.get('exec_option').get('location'):
                        raise serializers.ValidationError(
                            detail='Execute Command or Script Execute Location was not specified',
                            code='location_missing'
                        )

        return data

class RegisterSerializer(serializers.Serializer):
    """

    """
    ip = serializers.CharField(label="ip", help_text='ip',required=True)
    username = serializers.CharField(label="username", help_text='username',required=True)
    password = serializers.CharField(label="password", help_text='password',required=True)
    port = serializers.IntegerField(label="port", help_text='port',required=True)
