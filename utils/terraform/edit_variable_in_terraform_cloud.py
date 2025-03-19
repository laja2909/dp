import time
import json

import requests

from helper import get_env_variable, get_public_ip_address

def get_response_content(response:requests.Response) -> json:
    if  response.status_code == 200:
        print("retrieved the response..")
        content = response.json()
    else:
        raise Exception
    return content

def get_workspace_id_for_organization(organization_name:str, workspace_name:str)-> None:
    tf_token = get_env_variable('TF_TOKEN')
    headers = {'Authorization': 'Bearer '+tf_token,
               'Content-Type': 'application/vnd.api+json'}
    tf_organizations_endpoint = f'https://app.terraform.io/api/v2/organizations/{organization_name}/workspaces'
    tf_response = requests.request("GET", tf_organizations_endpoint, headers=headers)
    content = get_response_content(tf_response)
    for ind, value in enumerate(content['data']):
        if value['attributes']['name']==workspace_name:
            workspace_id = value['id']
        else:
            continue
    return workspace_id

def get_variable_id_of_workspace(organization_name:str,workspace_name:str, variable_name:str)-> None:
    tf_token = get_env_variable('TF_TOKEN')
    headers = {'Authorization': 'Bearer '+tf_token,
               'Content-Type': 'application/vnd.api+json'}
    tf_workspace_id = get_workspace_id_for_organization(organization_name,workspace_name)

    tf_workspace_vars_endpoint = f'https://app.terraform.io/api/v2/workspaces/{tf_workspace_id}/vars'
    tf_response = requests.request("GET", tf_workspace_vars_endpoint, headers=headers)
    content = get_response_content(tf_response)
    for ind, value in enumerate(content['data']):
        if value['attributes']['key']==variable_name:
            variable_id = value['id']
        else:
            continue
    return variable_id

def get_variable_value_of_workspace(organization_name:str,workspace_name:str, variable_name:str)-> None:
    tf_token = get_env_variable('TF_TOKEN')
    headers = {'Authorization': 'Bearer '+tf_token,
               'Content-Type': 'application/vnd.api+json'}
    tf_workspace_id = get_workspace_id_for_organization(organization_name,workspace_name)

    tf_workspace_vars_endpoint = f'https://app.terraform.io/api/v2/workspaces/{tf_workspace_id}/vars'
    tf_response = requests.request("GET", tf_workspace_vars_endpoint, headers=headers)
    content = get_response_content(tf_response)
    for ind, value in enumerate(content['data']):
        if value['attributes']['key']==variable_name:
            variable_value = value['attributes']['value']
        else:
            continue
    return variable_value


def public_address_equals_tf_local_ip_variable(organization_name:str,workspace_name:str) -> None:
    tf_token = get_env_variable('TF_TOKEN')
    tf_local_ip_variable_name = 'local_ip'
    # get workspaces and their ids
    headers = {'Authorization': 'Bearer '+tf_token,
               'Content-Type': 'application/vnd.api+json'}
    
    tf_variable_value = get_variable_value_of_workspace(organization_name,workspace_name,tf_local_ip_variable_name)
    my_public_ip_address = get_public_ip_address()
    return tf_variable_value==my_public_ip_address

    
def edit_tf_local_ip_variable(organization_name:str,workspace_name:str)-> None:
    tf_token = get_env_variable('TF_TOKEN')
    tf_local_ip_variable_name = 'local_ip'
    # get workspaces and their ids
    headers = {'Authorization': 'Bearer '+tf_token,
               'Content-Type': 'application/vnd.api+json'}
    
    tf_variable_id = get_variable_id_of_workspace(organization_name,workspace_name,tf_local_ip_variable_name)
    my_public_ip_address = get_public_ip_address()
    # we need to change tf local ip variable into current public ip address
    payload = {"data": {
                "id":tf_variable_id,
                "attributes": {
                    "key":tf_local_ip_variable_name,
                    "value":my_public_ip_address,
                    "description": "description",
                    "category":"terraform",
                    "hcl": False,
                    "sensitive": False
                },
                "type":"vars"
                }
            }
    tf_variable_end_point=f'https://app.terraform.io/api/v2/vars/{tf_variable_id}'
    requests.request("PATCH", tf_variable_end_point, headers=headers,data=json.dumps(payload))

def get_latest_state_version_id(organization_name:str, workspace_name:str)-> str:
    tf_token = get_env_variable('TF_TOKEN')
    headers = {'Authorization': 'Bearer '+tf_token,
               'Content-Type': 'application/vnd.api+json'}
    tf_state_versions_end_point = f'https://app.terraform.io/api/v2/state-versions?filter[workspace][name]={workspace_name}&filter[organization][name]={organization_name}'
    tf_response = requests.request("GET", tf_state_versions_end_point, headers=headers)
    content = get_response_content(tf_response)
    return content['data'][0]['id']

def get_state_version_info(state_version_id:str)-> str:
    tf_token = get_env_variable('TF_TOKEN')
    headers = {'Authorization': 'Bearer '+tf_token,
               'Content-Type': 'application/vnd.api+json'}
    tf_state_version_info_end_point = f'https://app.terraform.io/api/v2/state-versions/{state_version_id}'
    tf_response = requests.request("GET", tf_state_version_info_end_point, headers=headers)
    content = get_response_content(tf_response)
    return content

def get_ssh_keys(state_version_id:str,ssh_resource_name:str) -> dict:
    ssh_key_dict = {}
    tf_token = get_env_variable('TF_TOKEN')
    headers = {'Authorization': 'Bearer '+tf_token,
               'Content-Type': 'application/vnd.api+json'}
    state_version_info = get_state_version_info(state_version_id)
    url_of_state_version_file = state_version_info['data']['attributes']['hosted-json-state-download-url']
    tf_response = requests.request("GET", url_of_state_version_file, headers=headers)
    content = get_response_content(tf_response)
    for ind,value in enumerate(content['values']['root_module']['resources']):
        if value['name']==ssh_resource_name:
            ssh_key_dict['private_key'] = value['values']['private_key_openssh']
            ssh_key_dict['public_key'] = value['values']['public_key_openssh']
        else:
            continue
    return ssh_key_dict


def write_files_to_local(content,file_name)-> None:
    with open(file_name, "w") as f:
        f.write(content)

def write_private_key_to_local(state_version_id,ssh_resource_name,private_key_file_name) -> None:
    ssh_keys = get_ssh_keys(state_version_id,ssh_resource_name)
    write_files_to_local(ssh_keys['private_key'],private_key_file_name)

def write_public_key_to_local(state_version_id,ssh_resource_name,public_key_file_name) -> None:
    ssh_keys = get_ssh_keys(state_version_id,ssh_resource_name)
    write_files_to_local(ssh_keys['private_key'],public_key_file_name)
    
    

if __name__=='__main__':
    write_public_key_to_local('sv-LPGtysANSSUDiwDV','generic-ssh-key','pub_key.pub')