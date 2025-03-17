import requests
import json
from helper import get_env_variable

# get variable list from the workspace
# get id of the specified variable
# edit variable



def change_value_of_tf_variable(variable_name:str)-> None:
    tf_token = get_env_variable('TF_TOKEN')
    workspace = 'DHub'
    variable_name = 'local_ip'
    headers = {'Authorization': 'Bearer '+tf_token,
           'Content-Type': 'application/vnd.api+json'
           }
    workspace_vars_endpoint = f'https://app.terraform.io/api/v2/workspaces/{workspace}/vars'
    # get variable list from the workspace
    tf_vars_response = requests.request("POST", workspace_vars_endpoint, headers=headers)
    if  tf_vars_response.status_code == 201:
        print("retrieved the response..")
        print(tf_vars_response.content)
    else:
        print(tf_vars_response.content)
        print("Did not get the required response")

if __name__=='__main__':
    change_value_of_tf_variable('local_ip')