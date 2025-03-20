import os
import socket
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