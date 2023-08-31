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
RANDOM_MODULE_NAME = "{}-{}-{}/".format('jk-huawei',datetime.datetime.now().strftime("%Y%m%d%H%M%S"), random_str(6))
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
			"availabilityZone=",
			"instanceType=",
			"numberOfInstances=",
			"instanceName=",
			"dbType=",
			"dbVersion=",
			"dbPassword=",
			"volumeType=",
			"volumeSize=",
			"vpcID=",
			"subnetID=",
			"securityGroupID=",
			"instanceChargeType=",
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
	if option == "--accessKey":
		accessKey = value
	if option == "--secretKey":
		secretKey = value
	if option == "--region":
		region = value
		var_check_write('region', region)
	if option == "--availabilityZone":
		availabilityZone = value
		var_check_write('availabilityZone', availabilityZone)
	if option == "--instanceType":
		instanceType = value
		var_check_write('instanceType', instanceType)
	if option == "--numberOfInstances":
		numberOfInstances = value
		var_check_write('numberOfInstances', numberOfInstances)
	if option == "--instanceName":
		instanceName = value
		var_check_write('instanceName', instanceName)
	if option == "--dbType":
		dbType = value
		var_check_write('dbType', dbType)
	if option == "--dbVersion":
		dbVersion = value
		var_check_write('dbVersion', dbVersion)
	if option == "--dbPassword":
		dbPassword = value
		var_check_write('dbPassword', dbPassword)
	if option == "--volumeType":
		volumeType = value
		var_check_write('volumeType', volumeType)
	if option == "--volumeSize":
		volumeSize = value
		var_check_write('volumeSize', volumeSize)
	if option == "--vpcID":
		vpcID = value
		var_check_write('vpcID', vpcID)
	if option == "--subnetID":
		subnetID = value
		var_check_write('subnetID', subnetID)
	if option == "--securityGroupID":
		securityGroupID = value
		var_check_write('securityGroupID', securityGroupID)
	if option == "--instanceChargeType":
		instanceChargeType = value
		var_check_write('instanceChargeType', instanceChargeType)

def exec_tf_init():
	docker_tf_init = "docker run --rm -v {}:{} -v {}:{} -w {} -e TF_PLUGIN_CACHE_DIR={} -e HW_ACCESS_KEY={} -e HW_SECRET_KEY={} -e HW_REGION_NAME={} hashicorp/terraform:1.0.9 {} -var-file={}".format(
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
	docker_tf_apply = "docker run --rm -v {}:{} -v {}:{} -w {} -e TF_PLUGIN_CACHE_DIR={} -e HW_ACCESS_KEY={} -e HW_SECRET_KEY={} -e HW_REGION_NAME={} hashicorp/terraform:1.0.9 {} -var-file={}".format(
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


if __name__ == '__main__':
	exec_tf_init()
	exec_tf_create()

# python __jk_script_dpa_tf_huawei_rds.py \
# --module 'huaweicloud/rds' \
# --accessKey 'DNBDRK****QFXAUHA' \
# --secretKey 'b2kqAkLw*****2chIvpTRZh17qgEWFBAlW' \
# --region 'cn-east-3' \
# --availabilityZone '["cn-east-3a"]' \
# --instanceType 'rds.mysql.n1.large.2' \
# --numberOfInstances '1' \
# --instanceName 'dpa-rds-test' \
# --dbType 'MySQL' \
# --dbVersion '5.7' \
# --dbPassword '123qweASD' \
# --volumeType 'CLOUDSSD' \
# --volumeSize '100' \
# --vpcID 'f037d750-dff0-488b-a0a0-514491876069' \
# --subnetID '1daed776-39e9-4ff7-afad-b9540a18104b' \
# --securityGroupID 'e2361088-3b96-4ef0-868a-8f390d06faff' \
# --instanceChargeType 'postPaid'