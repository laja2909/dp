import requests
import json

from dp.utils.confs import confs
from dp.utils.helper import get_env_variable

class HetznerApi:
    def __init__(self, api_token:str=get_env_variable(confs['hetzner']['api_token']['name'])):
        self._header = {'Authorization': 'Bearer '+ api_token}

    def get_header(self):
        return self._header
    
    def get_all_servers(self):
        end_point = 'https://api.hetzner.cloud/v1/servers'
        response = self.call_api('GET',end_point=end_point)
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

    #utils
    def call_api(self,method,end_point,payload:json=None) -> requests.Response:
        if payload!=None:
            print(f'Calling: {end_point}')
            response = requests.request(method, end_point, headers=self.get_header(),data=json.dumps(payload))
        else:
            print(f'Calling: {end_point}')
            response = requests.request(method, end_point, headers=self.get_header())
        return response
    
    def get_content_response(self,response:requests.Response) -> json:
        """
        Response is always in json object
        
        """
        try:
            content = response.json()
            print("retrieved the response..")
        except json.JSONDecodeError as e:
            raise Exception('No response: ', e)
        return content


if __name__=='__main__':
    hetz_api = HetznerApi()
    print(hetz_api.get_server_ipv4_by_name('dp'))
