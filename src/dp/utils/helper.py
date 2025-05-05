import os
import socket

import requests

from dp.confs_new import *

def get_env_variable(name):
    try:
        env_var = os.environ[name]
    except KeyError:
        raise KeyError(f'environment variable of {name} does not exists')

    return env_var

def get_local_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_public_ip_address():
    public_ip = requests.get('https://api.ipify.org').text
    return public_ip

def write_files_to_local(content,file_name)-> None:
    with open(file_name, "w") as f:
        f.write(content)

def get_global_var_value(target_system:str, name_of_variable:str) -> str:
    if target_system=='terraform':
        for key,value in terraform_vars.items():
            if key == name_of_variable:
                if value['type']=='LOCAL_ENV':
                    var_value = get_env_variable(value['name'])
                elif value['type']=='RAW':
                    var_value=value['name']
                else:
                    raise Exception('Invalid variable type')
                break
            else:
                continue
    elif target_system=='github':
        for key,value in github_vars.items():
            if key == name_of_variable:
                if value['type']=='LOCAL_ENV':
                    var_value = get_env_variable(value['name'])
                elif value['type']=='RAW':
                    var_value=value['name']
                else:
                    raise Exception('Invalid variable type')
                break
            else:
                continue
    elif target_system=='hetzner':
        for key,value in hetzner_vars.items():
            if key == name_of_variable:
                if value['type']=='LOCAL_ENV':
                    var_value = get_env_variable(value['name'])
                elif value['type']=='RAW':
                    var_value=value['name']
                else:
                    raise Exception('Invalid variable type')
                break
            else:
                continue
    elif target_system=='local':
        for key,value in local_vars.items():
            if key == name_of_variable:
                if value['type']=='LOCAL_ENV':
                    var_value = get_env_variable(value['name'])
                elif value['type']=='RAW':
                    var_value=value['name']
                else:
                    raise Exception('Invalid variable type')
                break
            else:
                continue
    elif target_system=='remote':
        for key,value in remote_vars.items():
            if key == name_of_variable:
                if value['type']=='LOCAL_ENV':
                    var_value = get_env_variable(value['name'])
                elif value['type']=='RAW':
                    var_value=value['name']
                else:
                    raise Exception('Invalid variable type')
                break
            else:
                continue
    else:
        raise Exception('Incorrect target system.')
    return var_value
                
                    


if __name__ == '__main__':
    print(get_global_var_value('local','ssh_path'))
