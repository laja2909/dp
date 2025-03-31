import json

import requests

from dp.utils.confs import confs
from dp.utils.helper import get_env_variable


class TFCloud:
    """
    Class to help with Terraform Cloud API calls
    This class expects you to work on specific organization and workspace
    
    """
    def __init__(self,token_name:str=confs['terraform']['api_token']['name'],
                 organization:str=confs['terraform']['organization']['name'],
                 workspace:str=confs['terraform']['workspace']['name']
                 ):
        
        self._token_name=token_name
        self._organization_name=organization
        self._workspace_name=workspace

        token = get_env_variable(token_name)
        self._header = {'Authorization': 'Bearer '+token,
                     'Content-Type': 'application/vnd.api+json'}
    
    
    #ATTRIBUTES
    def get_token_name(self):
        return self._token_name
        
    def get_organization_name(self):
        return self._organization_name
    
    def get_workspace_name(self):
        return self._workspace_name
    
    def get_header(self):
        return self._header
    
    #Create
    def create_organization(self,payload:dict):
        end_point='https://app.terraform.io/api/v2/organizations'
        """
        payload={
            "data": {
                "type": "organizations",
                "attributes": {
                    "name": organization_name,
                    "email": email
                }
            }
        }
        """
        self.call_api('POST',end_point=end_point,payload=payload)
        #requests.request("POST", end_point, headers=self.get_header(),data=json.dumps(payload))

    def create_workspace(self,payload:dict):
        end_point=f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}/workspaces'
        response = self.call_api('POST',end_point=end_point,payload=payload)
        content = self.get_content_response(response=response)
        return content
        #requests.request("PATCH", end_point, headers=self.get_header(),data=json.dumps(payload))

    def create_workspace_variable(self, payload:dict):
        end_point=f'https://app.terraform.io/api/v2/workspaces/{self.get_workspace_id()}/vars'
        """
        payload = {
        "data": {
            "type":"vars",
            "attributes": {
                "key":"some_key",
                "value":"some_value",
                "description":"some description",
                "category":"terraform",
                "hcl":false,
                "sensitive":false
            }
        }}
        """
        self.call_api('POST',end_point=end_point,payload=payload)
        #requests.request("POST", end_point, headers=self.get_header(),data=json.dumps(payload))


    #GET
    def get_account_details(self) -> dict:
        end_point = f'https://app.terraform.io/api/v2/account/details'
        response = self.call_api('GET',end_point=end_point)
        content = self.get_content_response(response)
        return content
    
    def get_github_oauth_token_id(self) -> str:
        url_path = self.get_account_details()['data']['relationships']['github-app-oauth-tokens']['links']['related']
        end_point = f'https://app.terraform.io{url_path}'
        response = self.call_api('GET',end_point=end_point)
        content = self.get_content_response(response)
        return content['data'][0]['id']


    def get_oauth_clients_content(self) -> dict:
        end_point = f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}/oauth-clients'
        response = self.call_api('GET',end_point=end_point)
        #response = requests.request("GET", end_point, headers=self.get_header())
        content = self.get_content_response(response)
        return content
    
    def get_oauth_client_ids(self) -> list:
        client_ids = []
        content = self.get_oauth_clients_content()
        for ind, value in enumerate(content['data']):
            client_ids.append(value['id'])
        return client_ids

    def get_oauth_client_id_by_service_provider(self,service_provider:str) -> str:
        content = self.get_oauth_clients_content()
        for ind, value in enumerate(content['data']):
            if value['attributes']['service-provider']==service_provider:
                client_id = value['id']
            else:
                continue
        return client_id
    
    def get_oauth_token_id_by_client_id(self,client_id:str)-> str:
        end_point = f'https://app.terraform.io/api/v2/oauth-clients/{client_id}/oauth-tokens'
        response = self.call_api('GET',end_point=end_point)
        #response = requests.request("GET", end_point, headers=self.get_header())
        content = self.get_content_response(response)
        return content['data'][0]['id']

    def get_workspace_id(self) -> str:
        end_point = f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}/workspaces'
        response = self.call_api('GET',end_point=end_point)
        #response = requests.request("GET", end_point, headers=self.get_header())
        content = self.get_content_response(response)
        for ind, value in enumerate(content['data']):
            if value['attributes']['name']==self.get_workspace_name():
                workspace_id = value['id']
            else:
                workspace_id=''
        return workspace_id
    
    def get_vars_end_point_content(self):
        """
        fetches vars endpoint content
        vars end point needs the id of workspace that the variables are associated with

        """
        end_point = f'https://app.terraform.io/api/v2/workspaces/{self.get_workspace_id()}/vars'
        response = self.call_api('GET',end_point=end_point)
        #response = requests.request("GET", end_point, headers=self.get_header())
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
        response = self.call_api('GET',end_point=end_point)
        #response = requests.request("GET", end_point, headers=self.get_header())
        content = self.get_content_response(response)
        return content['data'][0]['id']
    
    def get_meta_of_state_version(self,state_version_id:str)-> json:
        end_point = f'https://app.terraform.io/api/v2/state-versions/{state_version_id}'
        response = self.call_api('GET',end_point=end_point)
        #response = requests.request("GET", end_point, headers=self.get_header())
        content = self.get_content_response(response)
        return content
    
    def get_content_of_state_version(self,state_version_id:str)-> json:
        state_version_meta = self.get_meta_of_state_version(state_version_id)
        url_path_to_state_version_content = state_version_meta['data']['attributes']['hosted-json-state-download-url']
        response = self.call_api('GET',end_point=url_path_to_state_version_content)
        #response = requests.request("GET", url_path_to_state_version_content, headers=self.get_header())
        content = self.get_content_response(response)
        return content
    
    def get_resources_from_workspace(self, workspace_id:str) -> json:
        end_point = f'https://app.terraform.io/api/v2/workspaces/{workspace_id}/resources'
        response = self.call_api('GET',end_point=end_point)
        #response = requests.request("GET", end_point, headers=self.get_header())
        content = self.get_content_response(response)
        return content

    #UPDATE
    def update_variable_value(self,variable_name:str,payload:dict)->None:
        """
        Change existing variable value
        """
        variable_id = self.get_variable_id(variable_name)
        end_point=f'https://app.terraform.io/api/v2/vars/{variable_id}'
        self.call_api('PATCH',end_point=end_point,payload=payload)
        #requests.request("PATCH", end_point, headers=self.get_header(),data=json.dumps(payload))

    ##DELETE
    def delete_organization(self):
        end_point=f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}'
        self.call_api('DELETE',end_point=end_point)
        #requests.request("DELETE", end_point, headers=self.get_header())

    def delete_workspace(self):
        end_point=f'https://app.terraform.io/api/v2/workspaces/{self.get_workspace_id()}/actions/safe-delete'
        self.call_api('POST',end_point=end_point)
        #requests.request("POST", end_point, headers=self.get_header())

    def delete_variable(self,variable_name:str):
        variable_id = self.get_variable_id(variable_name=variable_name)
        end_point=f'https://app.terraform.io/api/v2/workspaces/{self.get_workspace_id}/vars/{variable_id}'
        self.call_api('DELETE',end_point=end_point)
        #requests.request("DELETE", end_point, headers=self.get_header())

    def delete_oauth_token_by_service_provider(self,service_provider:str):
        oauth_token_client_id = self.get_oauth_client_id_by_service_provider(service_provider=service_provider)
        oauth_token_id = self.get_oauth_token_id_by_client_id(client_id=oauth_token_client_id)

        end_point=f'https://app.terraform.io/api/v2/oauth-tokens/{oauth_token_id}'
        self.call_api('DELETE',end_point=end_point)
        #requests.request("DELETE", end_point, headers=self.get_header())
        
    ##RUN
    def run_in_runs_end_point(self,payload:dict):
        """
        runs the terraform run in cloud
        """
        end_point=f'https://app.terraform.io/api/v2/runs'
        response = self.call_api('POST',end_point=end_point,payload=payload)
        #response = requests.request("POST", end_point, headers=self.get_header(),data=json.dumps(payload))
        content = self.get_content_response(response)
        return content

    ##UTIL
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
    
    
    ##BOOL
    def is_equal_to_variable_value(self, comparison_value:str,variable_name:str)->bool:
        variable_value = self.get_variable_value(variable_name)
        return comparison_value==variable_value



if __name__=='__main__':
    tf_api = TFCloud()
    print(tf_api.get_oauth_clients_content())