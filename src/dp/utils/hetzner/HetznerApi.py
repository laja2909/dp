import requests
import json

from pathlib import Path

from dp.utils.helper import get_global_confs
from dp.utils.general.API import API

class HetznerApi(API):
    def __init__(self, api_token:str):
        self._header = {'Authorization': 'Bearer '+ api_token}

    def get_header(self):
        return self._header
    
    def get_all_servers(self):
        endpoint = 'https://api.hetzner.cloud/v1/servers'
        response = self.call_endpoint(method='GET', endpoint=endpoint,headers=self.get_header())
        content = self.get_content_response(response)
        return content
    
    def get_server_ipv4_by_name(self,server_name:str):
        all_servers = self.get_all_servers()
        for server in all_servers['servers']:
            if server['name'] == server_name:
                ipv4_address = server['public_net']['ipv4']['ip']
                break
            else:
                continue
        return ipv4_address
    
    #BOOL
    def has_servers_running(self):
        list_of_servers = self.get_all_servers()['servers']
        if list_of_servers:
            has_servers_running = True
        else:
            has_servers_running = False
        return has_servers_running


if __name__=='__main__':
    confs = get_global_confs(file_path=Path(__file__).parent.parent.parent.joinpath('setup/confs.json').as_posix())
    hetz_api = HetznerApi(api_token=confs['hetzner_api_token']['value'])
    print(hetz_api.has_servers_running())
