#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   restful_api.py
@Time    :   2020/05/29 16:42:33
'''

import json
import requests
import logging
from urllib.parse import urlencode
from urllib3 import disable_warnings
from urllib3 import encode_multipart_formdata
from utils.jklog import jklog
from uuid import uuid4

from utils.elasticApi.es import ElasticHandle

from datetime import datetime

from django.conf import settings

logger = logging.getLogger('console')


class HttpHandle(object):
    """

    """
    def __init__(self, job_num, exec_async, log_server):

        self.job_num = job_num
        self.exec_async = exec_async
        self.log_server = log_server
        self.es_handle = ElasticHandle()

    @staticmethod
    def generate_get_url(url, args):
        """转换Get方式的url

        :param url:
        :param args:
        :return:
        """
        url_arg = urlencode(args, doseq=True)

        if '?' in url:
            format_url = url + '&' + url_arg
        else:
            format_url = url + '?' + url_arg

        return format_url

    def send_res(self, start_date, url, data, log):

        results = dict()
        results['start_date'] = start_date
        results['target'] = url
        results['status'] = 'SUCCESS'
        results['result'] = data
        results['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')

        self.es_handle.send_result(job_num=self.job_num, result=results, log=log)
    
    def post(self,**kwargs):
            pass

    def execute(self, url, method, timeout=120, max_retries=1, header=None, args=None, files=None, verify=False):
        """接口调用执行逻辑

        :param url:
        :param method:
        :param header:
        :param args:
        :param verify:
        :return: bool http_status_code result
        """

        logger.debug('files is :  {} '.format(files))
        logger.debug('args is :  {} '.format(args))

        # 此处兼容dpa 数据以及xml.(DPA 定义数据结构为string，实际使用为map(object))
        if type(args) is str:
            if args.startswith('<'):
                args = args.replace('"', '\'')
            # 处理 万科兼容
            elif 'binary' in header:
                args = args
            elif 'text/plain' in header:
                args = args
            else:
                if "xml" not in header:
                    if '\\' in args:
                        args = json.loads(json.dumps(args))
                    else:
                        args = json.loads(args.replace('\'', '"'))
            logger.debug(args)
        if method.lower() == 'get':
            if args:
                url = self.generate_get_url(url=url, args=args)

        if isinstance(header, str):
            header = json.loads(header)


        retry = 0

        while retry < max_retries:
            success, code, result = self.retry_exec(retry=retry,
                                                    url=url,
                                                    method=method,
                                                    timeout=timeout,
                                                    max_retries=max_retries,
                                                    header=header,
                                                    args=args,
                                                    files=files,
                                                    verify=verify)
            if success:
                break
            retry += 1
        return success, code, result

    def generate_file_args(self,files):
        # 数据结构 {"file1":["1",2],"file2":[3,4]}
        logger.debug("generate_file_args")

        dir_path = '/tmp'

        # return 定义
        file_args = list()

        # 下载文件,并生成文件参数
        for key in files.keys():
            file_list = files[key]

            for file_url in file_list:
                                
                filename =file_url.split('/')[-1]

                if '?' in filename:
                    filename = filename.split('?')[0]
                
                file_path = '{}/{}'.format(dir_path, filename)

                with requests.get(url=file_url, stream=True) as r:
                    r.raise_for_status()
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)

                file_args.append((key,open(file_path,"rb")))


        logger.debug('file_args:  {} '.format(file_args))

        return file_args

    def generate_binary_filename(self,file_url):
        dir_path = '/tmp'
        if "?" in file_url:
            filename =file_url.split('/')[-1].split('?')[0]
        else:
            filename =file_url.split('/')[-1]

        file_path = '{}/{}'.format(dir_path, filename)

        with requests.get(url=file_url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

        return file_path

    def retry_exec(self, retry, url, method, timeout, max_retries, header, args, files, verify):
        _request = None

        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')
        response_data = dict()
        response_data['start_date'] = start_date
        response_data['header'] = None
        response_data['body'] = None
        response_data['target'] = None
        response_data['status'] = None
        response_data['end_date'] = None

        
        disable_warnings()

        content_type = header.get('Content-Type', None)

        # 万科兼容
        company = header.get('company', None)
        vanke_cookie=dict()

        if company:
            header.pop('company')
            
            if header.get("Cookie"):
                cookies = header.get("Cookie")
                for i  in cookies.split(";"):
                    if "rtFa" in i:
                        rtFa = i.split("=")
                        vanke_cookie["rtFa"]=rtFa[1]+"="
                    if "FedAuth" in i:
                        FedAuth = i.split("=")
                        vanke_cookie["FedAuth"]=FedAuth[1]
                    if "SIMI" in i:
                        SIMI = i.split("=")
                        vanke_cookie["SIMI"]=SIMI[1]+"="

        logger.debug('Content-Type is: {}'.format(content_type))
        
        try:
            if method.lower() == 'get':
                if header:
                    _request = requests.get(url=url, headers=header, timeout=timeout, verify=verify)
                else:
                    _request = requests.get(url=url, timeout=timeout, verify=verify)

            if method.lower() == 'delete':
                _request = requests.delete(url=url, json=args, headers=header, timeout=timeout, verify=verify)

            if method.lower() == 'patch':
                _request = requests.patch(url=url, json=args, headers=header, timeout=timeout, verify=verify)

            if method.lower() == 'put':
                _request = requests.put(url=url, json=args, headers=header, timeout=timeout, verify=verify)

            if method.lower() == 'post':
                if header:
                    if 'binary' in content_type:
                        filename = self.generate_binary_filename(args)
                        if vanke_cookie:
                            with open(filename, 'rb') as f:
                                _request = requests.post(url, data=f, timeout=timeout,  headers=header, cookies=vanke_cookie, verify=verify)
                        else:
                            with open(filename, 'rb') as f:
                                _request = requests.post(url, data=f, timeout=timeout, verify=verify)
                                
                    if 'application/json' in content_type:
                        _request = requests.post(url=url, json=args, timeout=timeout, headers=header, verify=verify)

                    elif 'application/x-www-form-urlencoded' in content_type:
                        if files:
                            file_args = self.generate_file_args(files)
                            _request = requests.post(url=url, data=args, files=file_args, headers=header, timeout=timeout, verify=verify)
                        else:
                            _request = requests.post(url=url, data=args, timeout=timeout, verify=verify)

                    elif 'multipart/form-data' in content_type:
                        
                        file_args = self.generate_file_args(files)

                        _request = requests.post(url=url, data=args, files=file_args,timeout=timeout, verify=verify)

                    elif 'text/xml' in content_type:
                        if vanke_cookie:
                            _request = requests.post(url=url, data=args, timeout=timeout, cookies=vanke_cookie, verify=verify)
                        else:
                            _request = requests.post(url=url, data=args, timeout=timeout, headers=header, verify=verify)

                    elif 'text/plain' in content_type:
                        _request = requests.post(url=url, data=args, timeout=timeout, headers=header, verify=verify)
                        
                    elif content_type is None:
                        _request = requests.post(url=url, data=args, headers=header, timeout=timeout, verify=verify)
                    else:
                        pass
                else:
                    if files:
                        file_args = self.generate_file_args(files)
                        _request = requests.post(url=url, data=args, headers=header, files=file_args, timeout=timeout, verify=verify)
                    else:
                        _request = requests.post(url=url, data=args, headers=header, timeout=timeout, verify=verify)

        except Exception as e:
            if retry == max_retries - 1:
                log = '[{}: ERROR/{}] \n{}\n'.format(start_date, url, repr(e))
                if self.exec_async == 1 and self.log_server == 1:
                    self.send_res(start_date, url, repr(e), log)
            logger.error(repr(e))
            return False, 500, 'Request {} API Exception: {}'.format(url, repr(e))

        logger.debug(_request.content)
        logger.debug(_request.status_code)

        # 万科 兼容 cookie 返回403
        if _request.content:
            request_status_code = _request.status_code
        if company and company=="vanke" and request_status_code == 403:
            request_status_code = 200


        if _request and request_status_code in [200, 201, 202, 204, 302]:

            request_content =  _request.content
            if isinstance(_request.content, bytes):
                request_content = str(_request.content, encoding='utf-8')

            if _request.content:
                if 'xml' in _request.headers.get('Content-Type'):
                    request_content = request_content
                elif company and company=="vanke":
                    request_content = str(request_content,encoding='utf-8')
                else:
                    if isinstance(_request.content, bytes):
                        request_content = json.loads(request_content)
                    else:
                        request_content = json.loads(_request.content.decode('utf-8').replace('\'', '"'))
            
            try:
                response_data['header'] = json.loads(json.dumps(dict(_request.headers))),
                response_data['body'] = request_content
                response_data['target'] = url
                response_data['status'] = 'SUCCESS'
                response_data['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')

                log = '[{}: INFO/{}] \n{}\n'.format(start_date, url, response_data)

                if self.exec_async == 1 and self.log_server == 1:
                    self.send_res(start_date, url, response_data, log)
                    
                return True, _request.status_code, response_data

            except json.JSONDecodeError as e:

                response_data['header'] = json.loads(json.dumps(dict(_request.headers))),
                response_data['body'] = _request.content.decode('utf-8'),
                response_data['target'] = url
                response_data['status'] = 'FAILURE'
                response_data['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')



                log = '[{}: INFO/{}] \n{}\n'.format(start_date, url, response_data)

                if self.exec_async == 1 and self.log_server == 1:
                    self.send_res(start_date, url, response_data, log)

                return True, _request.status_code, response_data

            except Exception as e:
                if retry == max_retries - 1:
                    log = '[{}: ERROR/{}] \n{} \n'.format(start_date, url, repr(e))

                if self.exec_async == 1 and self.log_server == 1:
                    self.send_res(start_date, url, _request.content.decode('utf-8'), log)

                logger.error(log)
                return False, 500, '{} API Response Exception: {}'.format(url, repr(e))

        else:

            error_data = dict()
            error_data['start_date'] = start_date
            error_data['error'] = None
            error_data['body'] = None
            error_data['target'] = None
            error_data['status'] = None
            error_data['end_date'] = None

            try:
                error_url = 'Request {} API Result Error({})'.format(url, _request.status_code)

                if company and company=="vanke":
                    error_response=str(_request.content, encoding='utf-8')

                else:
                    error_response = json.loads(_request.content.decode('utf-8').replace('\'', '"'))

                error_data['error'] = error_url
                error_data['body'] = error_response
                error_data['target'] = url
                error_data['status'] = 'SUCCESS'
                error_data['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')

            except json.JSONDecodeError:
                error_url = 'Request {} API Result Error({})'.format(url, _request.status_code)
                error_response = _request.content.decode('utf-8')

                error_data['error'] = error_url
                error_data['body'] = error_response
                error_data['target'] = url
                error_data['status'] = 'FAILURE'
                error_data['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')

            if retry == max_retries - 1:
                log = '[{}: ERROR/{}] {}\n'.format(start_date, url, error_data)
                logger.error(log)
                if self.exec_async == 1 and self.log_server == 1:
                    self.send_res(start_date, url, error_data, log)
            

            if company and company=="vanke":
                error_data['header'] = json.loads(json.dumps(dict(_request.headers))),
                return True, _request.status_code, error_data

            return False, _request.status_code, error_data
            
