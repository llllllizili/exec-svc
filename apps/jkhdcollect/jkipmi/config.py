'''
@File    :   config.py
@Time    :   2021/03/19 17:24:14
'''


def base_info(host, user, passwd, port='623'):
    base_dict = dict()
    base_dict['mc'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                                ' -p ' + port + ' mc info'
    base_dict['product_name'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd +\
                                ' -p ' + port + ' mc getsysinfo system_name'
    base_dict['fw'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd +\
                      ' -p ' + port + ' mc info | grep -i Firmware | awk {\'print $4\'}'
    base_dict['sn'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd +\
                      ' -p ' + port + ' fru list | grep -a "Product Serial" | head -n1 | awk \'{print $4}\''
    base_dict['uuid'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                              ' -p ' + port + ' mc guid | head -n1 | awk \'{print $4}\''
    base_dict['mfg'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                                    ' -p ' + port + ' mc info | grep "Manufacturer Name" | awk \'{print $4}\''
    base_dict['time'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                        ' -p ' + port + ' sel time get'
    base_dict['os_name'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                           ' -p ' + port + ' mc getsysinfo os_name'
    base_dict['mac'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                           ' -p ' + port + ' lan print | grep -i mac | awk \'{print $4}\''
    base_dict['addr'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                        ' -p ' + port + ' lan print | grep -i "IP Address" | tail -n1'
    return base_dict


def hardware_info(host, user, passwd, port='623'):
    hardware_dict = dict()
    hardware_dict['fans'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                            ' -p ' + port + ' sdr | grep -i Fan'
    hardware_dict['power'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                             ' -p ' + port + ' sdr | grep -i Power'
    hardware_dict['mem'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                             ' -p ' + port + ' sdr | grep -i DIMM'
    hardware_dict['cpu'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                           ' -p ' + port + ' sdr | grep -i CPU'
    hardware_dict['disk'] = 'ipmitool' + ' -H ' + host + ' -I lanplus' + ' -U ' + user + ' -P ' + passwd + \
                            ' -p ' + port + ' sdr | grep -i C1'
    return hardware_dict