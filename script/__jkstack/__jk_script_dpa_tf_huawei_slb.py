#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import sys
import json
import getopt
import random
import string
import datetime

PY_VERSION = sys.version_info.major

if PY_VERSION == 2:
    import commands
if PY_VERSION == 3:
    import subprocess


def random_str(num):
    str_list = string.ascii_letters + string.digits
    random_str = [random.choice(str_list) for i in range(num)]
    res = ''.join(random_str)
    return res


# 写文件
TF_WORKSPACE = "/opt/terraform/"
TF_CACHE = TF_WORKSPACE + "dependent_cache/"
RANDOM_MODULE_NAME = "{}-{}-{}/".format('jk-huawei', datetime.datetime.now().strftime("%Y%m%d%H%M%S"), random_str(6))
TF_VAR_NAME = 'dpa.tfvars'

# 创建的目录
if not os.path.exists(TF_WORKSPACE):
    os.mkdir(TF_WORKSPACE)
if not os.path.exists(TF_CACHE):
    os.mkdir(TF_CACHE)

# 获取参数值
try:
    options, args = getopt.getopt(
        sys.argv[1:], "",
        [
            "module=",
            "accessKey=",
            "secretKey=",
            "name=",
            "region=",
            "vpcId=",
            "ipv4SubnetId=",
            "crossVpcBackend=",
            "availabilityZone=",
        ]
    )
except getopt.GetoptError as e:
    print('getopt error')
    print(e)
    sys.exit()


def var_check_write(key, value):
    try:
        check_type = json.loads(value)
    except Exception as e:
        check_type = value

    if isinstance(check_type, list):
        with open(TF_MODULE + TF_VAR_NAME, mode='a+') as file_obj:
            file_obj.write("{}={}\n".format(str(key), value))
    else:
        with open(TF_MODULE + TF_VAR_NAME, mode='a+') as file_obj:
            file_obj.write("{}=\"{}\"\n".format(str(key), value))


# 变量赋值
for option, value in options:
    # print("{} {}".format(option,value))
    if option in ("--module"):
        TF_BASE_MODULE = value + '/'
        # 目录复制
        os.system("cp -R {} {}".format(
            TF_WORKSPACE + TF_BASE_MODULE,
            TF_WORKSPACE + RANDOM_MODULE_NAME)
        )
        # 目录复制后路径
        TF_MODULE = TF_WORKSPACE + RANDOM_MODULE_NAME
    if option in ("--accessKey"):
        accessKey = value
    if option in ("--secretKey"):
        secretKey = value
    if option in ("--region"):
        region = value
        var_check_write('region', region)
    if option in ("--name"):
        name = value
        var_check_write('name', name)
    if option in ("--vpcId"):
        vpcId = value
        var_check_write('vpcId', vpcId)
    if option in ("--ipv4SubnetId"):
        ipv4SubnetId = value
        var_check_write('ipv4SubnetId', ipv4SubnetId)
    if option in ("--crossVpcBackend"):
        crossVpcBackend = value
        var_check_write('crossVpcBackend', crossVpcBackend)
    if option in ("--availabilityZone"):
        availabilityZone = value
        var_check_write('availabilityZone', availabilityZone)


def exec_tf_init():
    docker_tf_init = "docker run --rm -v {}:{} -v {}:{} -w {} -e TF_PLUGIN_CACHE_DIR={} -e HW_ACCESS_KEY={} -e HW_SECRET_KEY={} -e HW_REGION_NAME={} hashicorp/terraform:1.0.9 {} -var-file={}".format(
        TF_MODULE, TF_MODULE,
        TF_CACHE, TF_CACHE,
        TF_MODULE,
        TF_CACHE,
        accessKey,
        secretKey,
        region,
        'init',
        TF_MODULE + TF_VAR_NAME
    )
    if PY_VERSION == 2:
        (status, output) = commands.getstatusoutput(docker_tf_init)
    if PY_VERSION == 3:
        (status, output) = subprocess.getstatusoutput(docker_tf_init)

    print(output)


def exec_tf_create():
    docker_tf_apply = "docker run --rm -v {}:{} -v {}:{} -w {} -e TF_PLUGIN_CACHE_DIR={} -e HW_ACCESS_KEY={} -e HW_SECRET_KEY={} -e HW_REGION_NAME={} hashicorp/terraform:1.0.9 {} -var-file={}".format(
        TF_MODULE, TF_MODULE,
        TF_CACHE, TF_CACHE,
        TF_MODULE,
        TF_CACHE,
        accessKey,
        secretKey,
        region,
        # 'plan',
        'apply -auto-approve -json',
        TF_MODULE + TF_VAR_NAME
    )

    # print('---------------------')
    # print(docker_tf_apply)
    # print('-----------------------')

    if PY_VERSION == 2:
        (status, output) = commands.getstatusoutput(docker_tf_apply)
    if PY_VERSION == 3:
        (status, output) = subprocess.getstatusoutput(docker_tf_apply)

    print(output)


# print('*jkStack*')

# print(output.splitlines()[-1])


def get_output():
    out_cmd = "cat {}".format(TF_MODULE)
    if PY_VERSION == 2:
        (status, output) = commands.getstatusoutput(out_cmd)
    if PY_VERSION == 3:
        (status, output) = subprocess.getstatusoutput(out_cmd)
    outputs = json.loads(output)
    res = outputs.get("outputs")

    print('*jkStack*')
    print(json.dumps(res))


if __name__ == '__main__':
    exec_tf_init()
    exec_tf_create()
# get_output()


# python3 __jk_script_dpa_tf_huawei_slb.py \
# --module 'huaweicloud/slb' \
# --name 'dpa-elb-test' \
# --accessKey 'DNBD****AUHA' \
# --secretKey 'b2k*****qgEWFBAlW' \
# --region 'cn-east-3' \
# --vpcId 'f037d750-dff0-488b-a0a0-514491876069' \
# --crossVpcBackend 'true' \
# --ipv4SubnetId 'bfab797b-1bc6-48fd-a302-5dfc3ebdee09' \
# --availabilityZone '["cn-east-3a"]'
