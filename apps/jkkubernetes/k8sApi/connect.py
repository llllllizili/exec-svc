#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   connect.py
@Time    :   2020/11/14 13:01:05
'''

import os
from kubernetes import client, config
from utils.jklog import jklog


class k8sConnect(object):
    """K8S连接
    ARGS:
        cluster_name : 集群名
        conf_content : kubeadmin 配置信息
    """

    def __init__(self, cluster_name, conf_content):
        self.cluster_name = cluster_name
        self.conf_content = conf_content

    def config(self):
        jklog('file', __file__)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        kube_config = '{}/{}/{}.yml'.format(current_dir, 'kubeconfig',
                                            self.cluster_name)
    
        cf = os.path.exists(kube_config)

        if cf:
            return kube_config
        else:
            with open(kube_config, 'w') as file_object:
                file_object.write(self.conf_content)
            return kube_config

    # 核心资源客户端
    def kCore(self):

        try:
            cf = self.config()

            config.load_kube_config(config_file=cf)

            return True, client.CoreV1Api()

        except Exception as e:

            jklog('error', repr(e))

            return False, repr(e)

    #app客户端连接
    def kApp(self):

        try:
            cf = self.config()

            config.load_kube_config(config_file=cf)

            return True, client.AppsV1Api()

        except Exception as e:

            jklog('error', repr(e))

            return False, repr(e)