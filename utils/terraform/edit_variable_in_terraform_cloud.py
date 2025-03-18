import requests
import json
from helper import get_env_variable

# get variable list from the workspace
# get id of the specified variable
# edit variable

def get_response_content(response:requests.Response):
    if  response.status_code >= 200 and response.status_code < 300:
        print("retrieved the response..")
        content = response.content
    else:
        print("Did not get the required response")
        content = None
    return content

def get_workspace_id(organization_name:str)-> None:
    tf_token = get_env_variable('TF_TOKEN')
    headers = {'Authorization': 'Bearer '+tf_token,
               'Content-Type': 'application/vnd.api+json'}
    tf_organizations_endpoint = f'https://app.terraform.io/api/v2/organizations/{organization_name}/workspaces'
    tf_response = requests.request("GET", tf_organizations_endpoint, headers=headers)
    print(tf_response)
    content = get_response_content(tf_response)
    return content['data']['id']
    


def change_value_of_tf_variable(variable_name:str)-> None:
    tf_token = get_env_variable('TF_TOKEN')
    tf_organization='dhub-dev'
    # get workspaces and their ids
    headers = {'Authorization': 'Bearer '+tf_token,
               'Content-Type': 'application/vnd.api+json'}
    
    tf_organizations_endpoint = f'https://app.terraform.io/api/v2/organizations/{tf_organization}/workspaces'
    tf_response = requests.request("GET", tf_organizations_endpoint, headers=headers)
    tf_response.content['data']['id']

   

    """
    tf_variable = variable_name
    
    
    workspace_vars_endpoint = f'https://app.terraform.io/api/v2/workspaces/{tf_workspace}/vars'
    # get variable list from the workspace
    tf_vars_response = requests.request("GET", workspace_vars_endpoint, headers=headers)
    """

if __name__=='__main__':
    print(get_workspace_id('dhub-dev'))