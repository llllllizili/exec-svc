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
	str_list=string.ascii_letters+string.digits
	random_str = [random.choice(str_list) for i in range(num)]
	res = ''.join(random_str)
	return res

# 写文件
TF_WORKSPACE="/opt/terraform/"
TF_CACHE=TF_WORKSPACE+"dependent_cache/"
RANDOM_MODULE_NAME = "{}-{}-{}/".format('jk-ali',datetime.datetime.now().strftime("%Y%m%d%H%M%S"), random_str(6))
TF_VAR_NAME='dpa.tfvars'

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
			"region=",
			"imageIds=",
			"instanceType=",
			"systemDiskCategory=",
			"systemDiskSize=",
			"numberOfInstances=",
			"instanceName=",
			"instancePassword=",
			"securityGroups=",
			"vswitchId=",
			"instanceChargeType="
		]
	)
except getopt.GetoptError as e:
	print('getopt error')
	print(e)
	sys.exit()

def var_check_write(key,value):

	try:
		check_type = json.loads(value)
	except Exception as e:
		check_type = value

	if isinstance(check_type,list):
		with open(TF_MODULE + TF_VAR_NAME, mode='a+') as file_obj:
			file_obj.write("{}={}\n".format(str(key), value))
	else:
		with open(TF_MODULE + TF_VAR_NAME, mode='a+') as file_obj:
			file_obj.write("{}=\"{}\"\n".format(str(key), value))

# 变量赋值
for option, value in options:	
	# print("{} {}".format(option,value))
	if option in ("--module"):

		TF_BASE_MODULE = value+'/'
		# 目录复制
		os.system("cp -R {} {}".format(
			TF_WORKSPACE+TF_BASE_MODULE,
			TF_WORKSPACE+RANDOM_MODULE_NAME)
			)
		# 目录复制后路径
		TF_MODULE = TF_WORKSPACE+RANDOM_MODULE_NAME
	if option in ("--accessKey"):
		accessKey = value
		var_check_write('accessKey', accessKey)
	if option in ("--secretKey"):
		secretKey = value
		var_check_write('secretKey', secretKey)
	if option in ("--region"):
		region = value
		var_check_write('region', region)
	if option in ("--imageIds"):
		imageIds = value
		var_check_write('imageIds', imageIds)
	if option in ("--instanceType"):
		instanceType = value
		var_check_write('instanceType', instanceType)
	if option in ("--systemDiskCategory"):
		systemDiskCategory = value
		var_check_write('systemDiskCategory', systemDiskCategory)
	if option in ("--systemDiskSize"):
		systemDiskSize = value
		var_check_write('systemDiskSize', systemDiskSize)
	if option in ("--numberOfInstances"):
		numberOfInstances = value
		var_check_write('numberOfInstances', numberOfInstances)
	if option in ("--instanceName"):
		instanceName = value
		var_check_write('instanceName', instanceName)
	if option in ("--instancePassword"):
		instancePassword = value
		var_check_write('instancePassword', instancePassword)
	if option in ("--securityGroups"):
		securityGroups = value
		var_check_write('securityGroups', securityGroups)
	if option in ("--vswitchId"):
		vswitchId = value
		var_check_write('vswitchId', vswitchId)
	if option in ("--instanceChargeType"):
		instanceChargeType = value
		var_check_write('instanceChargeType', instanceChargeType)

def exec_tf_init():
	docker_tf_init = "docker run --rm -v {}:{} -v {}:{} -w {} -e TF_PLUGIN_CACHE_DIR={} -e ALICLOUD_ACCESS_KEY={} -e ALICLOUD_SECRET_KEY={} -e ALICLOUD_REGION={} hashicorp/terraform:1.0.9 {} -var-file={}".format(
		TF_MODULE,TF_MODULE,
		TF_CACHE,TF_CACHE,
		TF_MODULE,
		TF_CACHE,
		accessKey,
		secretKey,
		region,
		'init',
		TF_MODULE+TF_VAR_NAME
	)
	if PY_VERSION == 2:
		(status, output) = commands.getstatusoutput(docker_tf_init)
	if PY_VERSION == 3:
		(status, output) = subprocess.getstatusoutput(docker_tf_init)

	print(output)


def exec_tf_create():

	docker_tf_apply = "docker run --rm -v {}:{} -v {}:{} -w {} -e TF_PLUGIN_CACHE_DIR={} -e ALICLOUD_ACCESS_KEY={} -e ALICLOUD_SECRET_KEY={} -e ALICLOUD_REGION={} hashicorp/terraform:1.0.9 {} -var-file={}".format(
		TF_MODULE,TF_MODULE,
		TF_CACHE,TF_CACHE,
		TF_MODULE,
		TF_CACHE,
		accessKey,
		secretKey,
		region,
		# 'plan',
		'apply -auto-approve -json',
		TF_MODULE+TF_VAR_NAME
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
	out_cmd="cat {}".format(TF_MODULE)
	if PY_VERSION == 2:
		(status, output) = commands.getstatusoutput(out_cmd)
	if PY_VERSION == 3:
		(status, output) = subprocess.getstatusoutput(out_cmd)

	outputs=json.loads(output)
	res = outputs.get("outputs")

	print(json.dumps(res))

if __name__ == '__main__':
	exec_tf_init()
	exec_tf_create()
	# get_output()

#  python3 __jk_script_dpa_tf_aliyun_ecs.py \
# --module 'aliyun/ecs' \
# --accessKey 'LTAI5t5gn******' \
# --secretKey '3sdtxM*****DMAMxrO' \
# --region 'cn-hangzhou' \
# --imageIds '["centos_7_7_64_20G_alibase_20191008.vhd"]' \
# --instanceType 'ecs.xn4.small' \
# --systemDiskCategory 'cloud_efficiency' \
# --systemDiskSize '50' \
# --numberOfInstances '1' \
# --instanceName 'dpa-test' \
# --instancePassword '123qweASD' \
# --securityGroups '["sg-bp1fhu45pdvomvhg0isp"]' \
# --vswitchId 'vsw-bp1gx9q8egwdw6b7ltus6' \
# --instanceChargeType 'PostPaid'