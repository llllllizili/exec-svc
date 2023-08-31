#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   jklog.py
@Time    :   2020/05/29 11:10:23
'''

import logging
import colorlog

log_collect = logging.getLogger("jkexec")
log_collect.setLevel(logging.INFO)

log_colors_config = {
    'DEBUG': 'white',
    'INFO': 'green',
    'FILE': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

console_handler = logging.StreamHandler()

console_formatter = colorlog.ColoredFormatter(
    fmt='%(log_color)s[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
    datefmt='%Y-%m-%d  %H:%M:%S',
    log_colors=log_colors_config
)

console_handler.setFormatter(console_formatter)


log_collect.addHandler(console_handler)

console_handler.close()


set_level = ['info','error','debug','file', 'warn']
# set_level = ['info','error','file']

def jklog(level, log):
    """
    level: info,warn,error,debug
    log  : log content
    """
    
    if level in set_level:
        if level== 'file':
            log_collect.info(log)
        if level== 'info':
            log_collect.info(log)
        if level== 'warn':
            log_collect.warning(log) 
        if level == 'error':
            log_collect.error(log) 
        if level == 'debug':
            log_collect.debug(log) 
    else:
        pass


if __name__ == '__main__':
    log_collect.debug('debug')
    log_collect.info('info')
    log_collect.warning('warning')
    log_collect.error('error')
    log_collect.critical('critical')
