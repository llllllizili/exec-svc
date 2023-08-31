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
			"name_prefix=",
			"vpc_id=",
			"vswitch_ids=",
			"new_nat_gateway=",
			"endpoint_public_access_enabled=",
			"deletion_protection=",
			"load_balancer_spec=",
			"time_zone=",
			"service_cidr=",
			"service_discovery_types=",
			"logging_type=",
			"name1=",
			"name2=",
			"name3=",
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

	if option in ("--name_prefix"):
		name_prefix = value
		var_check_write('name_prefix', name_prefix)
	if option in ("--vpc_id"):
		vpc_id = value
		var_check_write('vpc_id', vpc_id)
	if option in ("--vswitch_ids"):
		vswitch_ids = value
		var_check_write('vswitch_ids', vswitch_ids)
	if option in ("--new_nat_gateway"):
		new_nat_gateway = value
		var_check_write('new_nat_gateway', new_nat_gateway)
	if option in ("--endpoint_public_access_enabled"):
		endpoint_public_access_enabled = value
		var_check_write('endpoint_public_access_enabled', endpoint_public_access_enabled)
	if option in ("--deletion_protection"):
		deletion_protection = value
		var_check_write('deletion_protection', deletion_protection)

	if option in ("--load_balancer_spec"):
		load_balancer_spec = value
		var_check_write('load_balancer_spec', load_balancer_spec)
	if option in ("--time_zone"):
		time_zone = value
		var_check_write('time_zone', time_zone)
	if option in ("--service_cidr"):
		service_cidr = value
		var_check_write('service_cidr', service_cidr)
	if option in ("--service_discovery_types"):
		service_discovery_types = value
		var_check_write('service_discovery_types', service_discovery_types)
	if option in ("--logging_type"):
		logging_type = value
		var_check_write('logging_type', logging_type)
	if option in ("--k_aa"):
		k_aa = value
		var_check_write('k_aa', k_aa)
	if option in ("--k_bb"):
		k_bb = value
		var_check_write('k_bb', k_bb)
	if option in ("--name1"):
		name1 = value
		var_check_write('name1', name1)
	if option in ("--name2"):
		name2 = value
		var_check_write('name2', name2)
	if option in ("--name3"):
		name3 = value
		var_check_write('name3', name3)


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

