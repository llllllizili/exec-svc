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
			"access_key=",
			"secret_key=",
			"region=",
			"instance_charge_type=",
			"data_node_amount=",
			"data_node_spec=",
			"data_node_disk_size=",
			"data_node_disk_type=",
			"client_node_amount=",
			"client_node_spec=",
			"master_node_spec=",
			"protocol=",
			"vswitch_id=",
			"password=",
			"e_version=",
			"description=",
			"zone_count=",
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
		# 模块缓存统一放模块目录

	if option in ("--access_key"):
		accessKey = value
		var_check_write('access_key', accessKey)
	if option in ("--secret_key"):
		secretKey = value
		var_check_write('secret_key', secretKey)
	if option in ("--region"):
		region = value
		var_check_write('region', region)
	if option in ("--instance_charge_type"):
		instance_charge_type = value
		var_check_write('instance_charge_type', instance_charge_type)
	if option in ("--data_node_amount"):
		data_node_amount = value
		var_check_write('data_node_amount', data_node_amount)
	if option in ("--data_node_spec"):
		data_node_spec = value
		var_check_write('data_node_spec', data_node_spec)
	if option in ("--data_node_disk_size"):
		data_node_disk_size = value
		var_check_write('data_node_disk_size', data_node_disk_size)
	if option in ("--data_node_disk_type"):
		data_node_disk_type = value
		var_check_write('data_node_disk_type', data_node_disk_type)

	if option in ("--master_node_spec"):
		master_node_spec = value
		var_check_write('master_node_spec', master_node_spec)


	if option in ("--protocol"):
		protocol = value
		var_check_write('protocol', protocol)

	if option in ("--vswitch_id"):
		vswitch_id = value
		var_check_write('vswitch_id', vswitch_id)

	if option in ("--password"):
		password = value
		var_check_write('password', password)

	if option in ("--e_version"):
		e_version = value
		var_check_write('e_version', e_version)

	if option in ("--description"):
		description = value
		var_check_write('description', description)

	if option in ("--zone_count"):
		zone_count = value
		var_check_write('zone_count', zone_count)


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

