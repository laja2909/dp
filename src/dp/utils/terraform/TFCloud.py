import json
import time

import requests
from pathlib import Path

from dp.utils.general.API import API
from dp.utils.helper import get_global_confs 

class TFCloud:
    """
    Class to help with Terraform Cloud API calls
    This class expects you to work on specific organization and workspace
    
    """
    def __init__(self,token:str,organization:str,workspace:str):
        
        self._organization_name=organization
        self._workspace_name=workspace
        self._header = {'Authorization': 'Bearer '+token,
                     'Content-Type': 'application/vnd.api+json'}
    
    #ATTRIBUTES
    def get_organization_name(self):
        return self._organization_name
    
    def get_workspace_name(self):
        return self._workspace_name
    
    def get_header(self):
        return self._header
    
    #Create
    def create_organization(self,payload:dict):
        endpoint='https://app.terraform.io/api/v2/organizations'
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
        api = API()
        response = api.call_endpoint('POST',endpoint=endpoint,headers=self.get_header(),payload=payload)
        content = api.get_content_response(response=response)
        return content

    def create_workspace(self,payload:dict):
        endpoint=f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}/workspaces'
        api = API()
        response = api.call_endpoint('POST',endpoint=endpoint,headers=self.get_header(),payload=payload)
        content = api.get_content_response(response=response)
        return content

    def create_workspace_variable(self, payload:dict):
        endpoint=f'https://app.terraform.io/api/v2/workspaces/{self.get_workspace_id()}/vars'
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
        api = API()
        api.call_endpoint('POST',endpoint=endpoint,headers=self.get_header(),payload=payload)
    
    def create_oauth_client(self,payload:dict):
        endpoint = f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}/oauth-clients'
        api = API()
        response = api.call_endpoint('POST',endpoint=endpoint,headers=self.get_header(),payload=payload)
        content = api.get_content_response(response=response)
        return content


    #GET
    def get_account_details(self) -> dict:
        endpoint = f'https://app.terraform.io/api/v2/account/details'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        content = api.get_content_response(response)
        return content
    
    def get_github_oauth_token_id(self) -> str:
        url_path = self.get_account_details()['data']['relationships']['github-app-oauth-tokens']['links']['related']
        endpoint = f'https://app.terraform.io{url_path}'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        content = api.get_content_response(response)
        return content['data'][0]['id']


    def get_oauth_clients_content(self) -> dict:
        endpoint = f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}/oauth-clients'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        content = api.get_content_response(response)
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
        endpoint = f'https://app.terraform.io/api/v2/oauth-clients/{client_id}/oauth-tokens'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        content = api.get_content_response(response)
        return content['data'][0]['id']

    def get_workspace_id(self) -> str:
        endpoint = f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}/workspaces'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        content = api.get_content_response(response)
        for ind, value in enumerate(content['data']):
            if value['attributes']['name']==self.get_workspace_name():
                workspace_id = value['id']
            else:
                raise Exception(f"workspace name mismatch between project confs and api endpoint workspace call: {self.get_workspace_name()}<>{value['attributes']['name']}")
        return workspace_id
    
    def get_vars_end_point_content(self):
        """
        fetches vars endpoint content
        vars end point needs the id of workspace that the variables are associated with

        """
        endpoint = f'https://app.terraform.io/api/v2/workspaces/{self.get_workspace_id()}/vars'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        content = api.get_content_response(response)
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
        endpoint = f'https://app.terraform.io/api/v2/state-versions?filter[workspace][name]={self.get_workspace_name()}&filter[organization][name]={self.get_organization_name()}'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        content = api.get_content_response(response)
        return content['data'][0]['id']
    
    def get_meta_of_state_version(self,state_version_id:str)-> json:
        endpoint = f'https://app.terraform.io/api/v2/state-versions/{state_version_id}'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        content = api.get_content_response(response)
        return content
    
    def get_content_of_state_version(self,state_version_id:str)-> json:
        state_version_meta = self.get_meta_of_state_version(state_version_id)
        url_path_to_state_version_content = state_version_meta['data']['attributes']['hosted-json-state-download-url']
        api = API()
        response = api.call_endpoint('GET',endpoint=url_path_to_state_version_content,headers=self.get_header())
        content = api.get_content_response(response)
        return content
    
    def get_resources_from_workspace(self, workspace_id:str) -> json:
        endpoint = f'https://app.terraform.io/api/v2/workspaces/{workspace_id}/resources'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        content = api.get_content_response(response)
        return content

    #UPDATE
    def update_variable_value(self,variable_name:str,payload:dict)->None:
        """
        Change existing variable value
        """
        variable_id = self.get_variable_id(variable_name)
        endpoint=f'https://app.terraform.io/api/v2/vars/{variable_id}'
        api = API()
        api.call_endpoint('PATCH',endpoint=endpoint,payload=payload,headers=self.get_header())

    ##DELETE
    def delete_organization(self):
        if self.has_terraform_organization():
            endpoint=f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}'
            api = API()
            api.call_endpoint('DELETE',endpoint=endpoint,headers=self.get_header())
        else:
            print('No need to delete, organization not found.')

    def delete_workspace(self):
        if self.has_terraform_workspace():
            endpoint=f'https://app.terraform.io/api/v2/workspaces/{self.get_workspace_id()}/actions/safe-delete'
            api = API()
            api.call_endpoint('POST',endpoint=endpoint,headers=self.get_header())
        else:
            print('No need to delete, workspace not found.')

    def delete_variable(self,variable_name:str):
        variable_id = self.get_variable_id(variable_name=variable_name)
        endpoint=f'https://app.terraform.io/api/v2/workspaces/{self.get_workspace_id}/vars/{variable_id}'
        api = API()
        api.call_endpoint('DELETE',endpoint=endpoint,headers=self.get_header())

    def delete_oauth_token_by_service_provider(self,service_provider:str):
        oauth_token_client_id = self.get_oauth_client_id_by_service_provider(service_provider=service_provider)
        oauth_token_id = self.get_oauth_token_id_by_client_id(client_id=oauth_token_client_id)

        endpoint=f'https://app.terraform.io/api/v2/oauth-tokens/{oauth_token_id}'
        api = API()
        api.call_endpoint('DELETE',endpoint=endpoint,headers=self.get_header())
    
    def delete_resources_from_workspace(self):
        payload = {
            "data": {
                "attributes": {
                    "message": "Destroy resources in workspace",
                    "is_destroy": True
                },
                "type":"runs",
                "relationships": {
                    "workspace": {
                        "data": {
                            "type": "workspaces",
                            "id": self.get_workspace_id()
                        }
                    }
                }
            }
        }
        self.run_in_runs_end_point(payload=payload)

    def delete_terraform_multiple_objects(self, objects:list):
        valid_objects_to_destroy = {'resources':1,'workspace':2,'organization':3}
        sorted_objects = sorted(objects, key=lambda x: valid_objects_to_destroy[x])

        for object in sorted_objects:
            if object not in valid_objects_to_destroy.keys():
                raise Exception (f'object {object} is not valid object to destroy. Valid objects are: {valid_objects_to_destroy}')
            else:
                if object == 'resources':
                    #1. destroy resources from workspace
                    if self.has_workspace_resources_running():
                        self.delete_resources_from_workspace()
                        print('Resources destroyed')
                        time.sleep(60)
                    else:
                        print('No resources running. Skip destruction')
                ## delete workspace
                elif object == 'workspace':
                    self.delete_workspace()
                    time.sleep(60)
                ## delete organization
                elif object == 'organization':
                    self.delete_organization()
    ##RUN
    def run_in_runs_end_point(self,payload:dict):
        """
        runs the terraform run in cloud
        """
        endpoint=f'https://app.terraform.io/api/v2/runs'
        api = API()
        response = api.call_endpoint('POST',endpoint=endpoint,payload=payload,headers=self.get_header())
        content = api.get_content_response(response)
        return content
    
    
    ##BOOL
    def is_equal_to_variable_value(self, comparison_value:str,variable_name:str)->bool:
        variable_value = self.get_variable_value(variable_name)
        return comparison_value==variable_value
    
    def has_terraform_organization(self) -> bool:
        endpoint = f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        if response.status_code==200:
            has_organization=True
        elif response.status_code==404:
            has_organization = False
        else:
            response.raise_for_status()
        return has_organization
    
    def has_terraform_workspace(self) -> bool:
        endpoint = f'https://app.terraform.io/api/v2/organizations/{self.get_organization_name()}/workspaces'
        api = API()
        response = api.call_endpoint('GET',endpoint=endpoint,headers=self.get_header())
        has_workspace = False
        
        if response.status_code==200:
            content = api.get_content_response(response)
            for ind, value in enumerate(content['data']):
                if value['attributes']['name']==self.get_workspace_name():
                    has_workspace = True
                    break
                else:
                    continue
        else:
            response.raise_for_status()
        return has_workspace
    
    
    def has_workspace_resources_running(self) -> bool:
        if self.has_terraform_workspace():
            workspace_id = self.get_workspace_id()
        else:
            return False
        resources = self.get_resources_from_workspace(workspace_id)
        if resources.get('data')!=None:
            has_resources = len(resources['data'])>0
        else:
            has_resources = False
        return has_resources

    
if __name__=='__main__':
    confs = get_global_confs(file_path=Path(__file__).parent.parent.parent.joinpath('setup/confs.json').as_posix())
    tf_api = TFCloud(token=confs['terraform_api_token']['value'],workspace=confs['terraform_workspace']['value'],organization=confs['terraform_organization']['value'])
    print(tf_api.get_oauth_client_id_by_service_provider(service_provider='github'))