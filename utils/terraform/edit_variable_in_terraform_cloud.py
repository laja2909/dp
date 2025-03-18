import requests
import json
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


if __name__=='__main__':
    edit_tf_local_ip_variable('dhub-dev','DHub')