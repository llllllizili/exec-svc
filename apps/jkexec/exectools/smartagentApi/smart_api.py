#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   smart_api.py
@Time    :   2021/01/15 11:50:47
'''
import json
import requests
import logging
from utils.jkaes import jkAes
from django.conf import settings


logger = logging.getLogger('console')

class SmartApi():
    def __init__(self, args):
        self.url = 'http://{}:{}'.format(
            settings.SMART_AGENT_SERVER['host'],
            str(settings.SMART_AGENT_SERVER['port'])
            )
        self.args = args
        if self.args == '':
            self.workdir = ''
        elif self.args.split('.')[-1] == 'sh':
            self.workdir = settings.SMART_AGENT_SCRIPT_PATH_LINUX
        elif self.args.split('.')[-1] == 'bat':
            self.workdir = settings.SMART_AGENT_SCRIPT_PATH_WINDOWS
        elif self.args.split('.')[-1] == 'ps1':
            self.workdir = settings.SMART_AGENT_SCRIPT_PATH_WINDOWS
        else:
            self.workdir = ''


    def hosts_list(self):
        hosts_url = '{}/host/list'.format(self.url)
        data = json.loads(requests.get(hosts_url).text)
        # logger.debug(data)
        return data

    def sys_info(self, hid):
        info_url = '{}/hm/static?id={}'.format(self.url, hid)
        data = json.loads(requests.get(info_url).text)
        logger.debug(data)
        return data

    def process_info(self, hid):
        process_url = '{}/hm/dynamic/process?id={}'.format(self.url, hid)
        data = json.loads(requests.get(process_url).text)
        logger.debug(data)
        return data

    def connection_info(self, hid):
        conn_url = '{}/hm/dynamic/connections?id={}'.format(self.url, hid)
        data = json.loads(requests.get(conn_url).text)
        logger.debug(data)
        return data

    def cmd_status(self, hid, pid):
        status_url = '{}/cmd/status?id={}&pid={}'.format(self.url, hid, pid)
        data = requests.get(status_url)
        # logger.debug(data)
        return data

    def cmd_run(self, hid, args, option_args, time_out, become):
        if become:
            cmd_url = '{}/cmd/run?workdir={}&id={}&cmd={}&args={}&timeout={}&auth={}&user={}&pass={}'.format(
                self.url, self.workdir, hid, args, option_args, time_out,
                become.get('method'),
                become.get('username'),
                jkAes().decrypt(become.get('password')))
        else:
            cmd_url = '{}/cmd/run?workdir={}&id={}&cmd={}&args={}&timeout={}'.format(
                self.url, self.workdir, hid, args, option_args, time_out)
        data = json.loads(requests.get(cmd_url).text)
        # logger.debug(data)
        return data

    def cmd_pty(self, agent_id, channel_id):
        pty_url = '{}/cmd/pty?id={}&pid={}'.format(self.url, agent_id, channel_id)
        data = requests.get(pty_url).text
        try:
            data = json.loads(data.replace('\n', '').replace('\r', ''))
        except:
            data = data.replace('\n', '').replace('\r', '')
        # logger.debug(data)
        return data

    def file_upload(self, payload, files):
        upload_url = '{}/file/upload'.format(self.url)
        data = requests.post(upload_url, data=payload, files=files)
        # logger.debug(data)
        return data

    def file_download(self, payload, files):
        download_url = '{}/file/download'.format(self.url)
        data = requests.post(download_url, data=payload, files=files)
        # logger.debug(data)
        return data