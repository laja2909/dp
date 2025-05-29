import os
import socket
import json
from pathlib import Path

import requests


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

def get_global_confs(file_path:str):
    with open(file_path) as f:
        data = json.load(f)
    
    flattened_data = {}
    for system,variables in data.items():
        for key,value in variables.items():
            name_of_key = f'{system}_{key}'
            if value['type']=='LOCAL_ENV':
                value_of_key = get_env_variable(value['name'])
            elif value['type']=='RAW':
                value_of_key = value['name']
            else:
                raise Exception('Invalid variable type')
            flattened_data.update({name_of_key:value_of_key})
    return flattened_data
    
                    


if __name__ == '__main__':
    path_to_confs = Path(__file__).parent.parent.joinpath('confs_new.json')
    get_global_confs(path_to_confs.as_posix())
    #print(path_to_confs)
