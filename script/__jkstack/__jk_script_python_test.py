#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@File    :   __jk_script_python_test.py
@Time    :   2020/06/12 09:53:36
'''

import sys
import platform 

print("helo world - python")
hw="hello world -var"
print(hw)

print(sys.argv[0])
print(sys.argv[1])
print(sys.argv[2])
print(sys.argv[3])
print('---------------\n')
print(platform.system())
print(platform.platform())
print(platform.version())
print(platform.architecture())
