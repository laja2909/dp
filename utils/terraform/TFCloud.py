import json

import requests

from helper import get_env_variable, get_public_ip_address


class TFCloud:
    """
    Class to help with Terraform Cloud API calls
    
    """
    def __init__(self):
        pass

    def set_header(self,token_name:str='TF_TOKEN') -> dict:
        token = get_env_variable(token_name)
        header = {'Authorization': 'Bearer '+token,
                     'Content-Type': 'application/vnd.api+json'}
        self._header = header

    def get_header(self):
        return self._header
        
    def get_content_response(self,response:requests.Response) -> json:
        """
        Response is always in json object
        
        """
        if  response.status_code == 200:
            print("retrieved the response..")
            content = response.json()
        else:
            # if error occurs print the error
            print(response.content)
            raise Exception
        return content
    
    def get_workspace_id_for_organization(self,organization_name:str, workspace_name:str) -> str:
        header = self.get_header()
        end_point = f'https://app.terraform.io/api/v2/organizations/{organization_name}/workspaces'
        response = requests.request("GET", end_point, headers=header)
        content = self.get_content_response(response)
        for ind, value in enumerate(content['data']):
            if value['attributes']['name']==workspace_name:
                workspace_id = value['id']
            else:
                continue
        return workspace_id

if __name__=='__main__':
    tf_api = TFCloud()
    tf_api.set_header()
    print(tf_api.get_workspace_id_for_organization('dhub-dev','DHub'))