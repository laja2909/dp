import json

import requests

from dp.utils.confs import *
from dp.utils.helper import get_env_variable


class TFCloud:
    """
    Class to help with Terraform Cloud API calls
    
    """
    def __init__(self):
        pass

    #ATTRIBUTES
    def set_header(self,token_name:str=LOCAL_ENV_TF_TOKEN_NAME) -> dict:
        token = get_env_variable(token_name)
        header = {'Authorization': 'Bearer '+token,
                     'Content-Type': 'application/vnd.api+json'}
        self._header = header

    def get_header(self):
        return self._header
    
    def set_organization_name(self,organization_name:str=TF_ORGANIZATION_NAME) -> str:
        self._organization_name = organization_name
    
    def get_organization_name(self):
        return self._organization_name
    
    def set_workspace_name(self,workspace_name:str=TF_WORKSPACE_NAME) -> str:
        self._workspace_name = workspace_name
    
    def get_workspace_name(self):
        return self._workspace_name
    
    #GET
    def get_workspace_id(self) -> str:
        header = self.get_header()
        end_point = f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}/workspaces'
        response = requests.request("GET", end_point, headers=header)
        content = self.get_content_response(response)
        for ind, value in enumerate(content['data']):
            if value['attributes']['name']==self.get_workspace_name():
                workspace_id = value['id']
            else:
                continue
        return workspace_id
    
    def get_vars_end_point_content(self):
        """
        fetches vars endpoint content
        vars end point needs the id of workspace that the variables are associated with

        """
        workspace_id = self.get_workspace_id()
        end_point = f'https://app.terraform.io/api/v2/workspaces/{workspace_id}/vars'
        header = self.get_header()
        response = requests.request("GET", end_point, headers=header)
        content = self.get_content_response(response)
        return content
    
    def get_variable_id(self,variable_name:str)-> None:
        """
        -fetch vars endpoint content
        -find element associated with variable name
        -return variable id
        """
        content = self.get_vars_end_point_content()
        for ind, value in enumerate(content['data']):
            if value['attributes']['key']==variable_name:
                variable_id = value['id']
            else:
                continue
        return variable_id
    
    def get_variable_value(self, variable_name:str)-> None:
        """
        -fetch vars endpoint content
        -find element associated with variable_name
        return variable value
        """
        content = self.get_vars_end_point_content()
        for ind, value in enumerate(content['data']):
            if value['attributes']['key']==variable_name:
                variable_value = value['attributes']['value']
            else:
                continue
        return variable_value
    
    def get_latest_state_version_id(self) -> str:
        end_point = f'https://app.terraform.io/api/v2/state-versions?filter[workspace][name]={self.get_workspace_name()}&filter[organization][name]={self.get_organization_name()}'
        response = requests.request("GET", end_point, headers=self.get_header())
        content = self.get_content_response(response)
        return content['data'][0]['id']
    
    def get_meta_of_state_version(self,state_version_id:str)-> json:
        end_point = f'https://app.terraform.io/api/v2/state-versions/{state_version_id}'
        response = requests.request("GET", end_point, headers=self.get_header())
        content = self.get_content_response(response)
        return content
    
    def get_content_of_state_version(self,state_version_id:str)-> json:
        state_version_meta = self.get_meta_of_state_version(state_version_id)
        url_path_to_state_version_content = state_version_meta['data']['attributes']['hosted-json-state-download-url']
        response = requests.request("GET", url_path_to_state_version_content, headers=self.get_header())
        content = self.get_content_response(response)
        return content


    #EDIT
    def edit_variable_value(self,variable_name:str,new_variable_value:str)->None:
        """
        Change existing variable value
        """
        variable_id = self.get_variable_id(variable_name)
        payload = {
            "data":{
                "id":variable_id,
                "attributes":{
                    "key":variable_name,
                    "value":new_variable_value,
                    "description": "description",
                    "category":"terraform",
                    "hcl": False,
                    "sensitive": False
                },
                "type":"vars"
            }}
        end_point=f'https://app.terraform.io/api/v2/vars/{variable_id}'
        requests.request("PATCH", end_point, headers=self.get_header(),data=json.dumps(payload))

    ##RUN
    def run(self):
        """
        runs the terraform run in cloud
        """
        workspace_id = self.get_workspace_id()
        payload = {
            "data": {
                "attributes": {
                    "message": "Custom message"
                },
                "type":"runs",
                "relationships": {
                    "workspace": {
                        "data": {
                            "type": "workspaces",
                            "id": workspace_id
                        }
                    }
                }
            }
        }

        end_point=f'https://app.terraform.io/api/v2/runs'
        response = requests.request("POST", end_point, headers=self.get_header(),data=json.dumps(payload))
        content = self.get_content_response(response)
        return content

    
    
    ##UTIL
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
    
    ##BOOL
    def is_equal_to_variable_value(self, comparison_value:str,variable_name:str)->bool:
        variable_value = self.get_variable_value(variable_name)
        return comparison_value==variable_value



if __name__=='__main__':
    tf_api = TFCloud()
    tf_api.set_header()
    tf_api.set_organization_name()
    tf_api.set_workspace_name()

    print(tf_api.get_variable_id('local_ip'))