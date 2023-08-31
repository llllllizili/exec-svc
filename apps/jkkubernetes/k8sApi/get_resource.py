#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   resource.py
@Time    :   2020/11/14 15:43:41
'''

import ast
import json

from jkkubernetes.k8sApi.connect import k8sConnect
from utils.jklog import jklog


class GetResourceHandle(object):
    """获取K8S资源
    ARGS:
        cluster_name: 集群名称
        conf_content: kube config信息
        kind: 资源类型
    """
    def __init__(self, cluster_name, conf_content, kind):
        self.cluster_name = cluster_name
        self.conf_content = conf_content
        self.kind = kind
        self.kconnect = None

    def client_type(self):
        kcore = ['pod', 'node', 'service', 'namespace']
        kapp = ['deployment', 'replicaset', 'daemonset']

        if self.kind in kcore:
            status, res = k8sConnect(cluster_name=self.cluster_name, conf_content=self.conf_content).kCore()

        if self.kind in kapp:
            status, res = k8sConnect(cluster_name=self.cluster_name, conf_content=self.conf_content).kApp()

        if status:
            self.kconnect = res
        else:
            pass

    def nodes(self):

        jklog('file', __file__)

        self.client_type()

        if self.kconnect == None:
            return False, "K8S connect failed"

        list_node = self.kconnect.list_node()

        jklog('debug', list_node)

        if list_node == None:
            return False, "node list is none"

        nodes_info = list()

        for n in list_node.items:
            role = ''
            if (('node-role.kubernetes.io/master' in n.metadata.labels)
                    or (n.spec.taints and n.spec.taints[0].key == 'node-role.kubernetes.io/master')):

                role = 'master'
            else:
                role = 'worker'

            n_info = {
                'architecture': n.status.node_info.architecture,
                'boot_id': n.status.node_info.boot_id,
                'container_runtime_version': n.status.node_info.container_runtime_version,
                'kernel_version': n.status.node_info.kernel_version,
                'kube_proxy_version': n.status.node_info.kube_proxy_version,
                'kubelet_version': n.status.node_info.kubelet_version,
                'machine_id': n.status.node_info.machine_id,
                'operating_system': n.status.node_info.operating_system,
                'os_image': n.status.node_info.os_image,
                'system_uuid': n.status.node_info.system_uuid,
                'labels': n.metadata.labels,
                'allocatable': n.status.allocatable,
                # 'capacity':n.status.capacity,
                'name': n.metadata.name,
                'address': n.status.addresses[0].address,
                'os_image': n.status.node_info.os_image,
                'create_time': n.metadata.creation_timestamp,
                # 'status': n.status.conditions,
                'role': role
            }

            nodes_info.append(n_info)
        return True, {'cluster': self.cluster_name, 'nodes_info': nodes_info}

    def pods(self):

        jklog('file', __file__)

        self.client_type()

        if self.kconnect == None:
            return False, "K8S connect failed"

        list_pod = self.kconnect.list_pod_for_all_namespaces()

        jklog('debug', list_pod)

        if list_pod == None:
            return False, "pod list is none"

        pods_info = list()

        for p in list_pod.items:
            p_info = {
                'name': p.metadata.name,
                'ip': p.status.pod_ip,
                'labels': p.metadata.labels,
                'node_name': p.spec.node_name,
                'namespace': p.metadata.namespace,
                'containers': p.spec.containers,
                'restart_count': p.status.container_statuses[0].restart_count
            }

            pods_info.append(p_info)
        return True, {'cluster': self.cluster_name, 'pods_info': ast.literal_eval(str(pods_info))}

        # print(list_pod)

    def services(self):
        jklog('file', __file__)
        self.client_type()

        if self.kconnect == None:
            return False, "K8S connect failed"

        list_service = self.kconnect.list_service_for_all_namespaces()

        jklog('debug', list_service)

        if list_service == None:
            return False, "service list is none"

        service_info = list()

        for s in list_service.items:
            s_info = {
                'name': s.metadata.name,
                'namespace': s.metadata.namespace,
                'labels': s.metadata.labels,
                'spec': ast.literal_eval(repr(s.spec)),
                'create_time': s.metadata.creation_timestamp,
            }

            service_info.append(s_info)

        return True, {'cluster': self.cluster_name, 'services_info': service_info}

    def namespace(self):
        jklog('file', __file__)
        self.client_type()

        if self.kconnect == None:
            return False, "K8S connect failed"

        list_namespace = self.kconnect.list_namespace()

        jklog('debug', list_namespace)

        if list_namespace == None:
            return False, "namespace list is none"

        namespace_info = list()

        for n in list_namespace.items:

            serv_name = self.kconnect.list_namespaced_service(n.metadata.name)
            self.kconnect.list_namespace_

            service_num = len(serv_name.items)

            ns_info = {
                'name': n.metadata.name,
                'status': n.status.phase,
                'create_time': n.metadata.creation_timestamp,
                'service_num': service_num,
                'labels': n.metadata.labels,
                'annotations': str(n.metadata.annotations)
            }
            namespace_info.append(ns_info)

        return True, {'cluster': self.cluster_name, 'namespaces_info': namespace_info}

    def deployment(self):
        jklog('file', __file__)
        self.client_type()

        if self.kconnect == None:
            return False, "K8S connect failed"

        list_deployment = self.kconnect.list_deployment_for_all_namespaces()

        jklog('debug', list_deployment)

        if list_deployment == None:
            return False, "deployment list is none"

        deployment_info = list()

        for dp in list_deployment.items:

            dp_info = {
                'name': dp.metadata.name,
                'namespace': dp.metadata.namespace,
                'create_time': dp.metadata.creation_timestamp,
                'strategy': dp.spec.strategy.type,
                'labels': dp.metadata.labels,
                'min_ready': dp.spec.min_ready_seconds,
                'selector': dp.spec.selector.match_labels
            }

            deployment_info.append(dp_info)

        return True, {'cluster': self.cluster_name, 'deployments_info': deployment_info}

    def replicaset(self):
        jklog('file', __file__)
        self.client_type()

        if self.kconnect == None:
            return False, "K8S connect failed"

        list_replicaset = self.kconnect.list_replica_set_for_all_namespaces()

        jklog('debug', list_replicaset)

        if list_replicaset == None:
            return False, "replicaset list is none"

        replicaset_info = list()

        for rs in list_replicaset.items:
            images = [c.image for c in rs.spec.template.spec.containers]
            rs_info = {
                'name': rs.metadata.name,
                'namespace': rs.metadata.namespace,
                'want_replicas': rs.spec.replicas,
                'ready_replicas': rs.status.ready_replicas,
                'create_time': rs.metadata.creation_timestamp,
                'images': images,
                'labels': rs.metadata.labels
            }
            replicaset_info.append(rs_info)

        return True, {'cluster': self.cluster_name, 'replicasets_info': replicaset_info}

    def daemonset(self):
        jklog('file', __file__)
        self.client_type()

        if self.kconnect == None:
            return False, "K8S connect failed"

        list_daemonset = self.kconnect.list_daemon_set_for_all_namespaces()

        jklog('debug', list_daemonset)

        if list_daemonset == None:
            return False, "replicaset list is none"

        daemonset_info = list()

        for ds in list_daemonset.items:
            ds_info = {
                'name': ds.metadata.name,
                'namespace': ds.metadata.namespace,
                'create_time': ds.metadata.creation_timestamp,
                'labels': ds.metadata.labels
            }
            daemonset_info.append(ds_info)

        return True, {'cluster': self.cluster_name, 'daemonsets_info': daemonset_info}
