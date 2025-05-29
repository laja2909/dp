import json

from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from dp.utils.helper import get_public_ip_address


class Payloads:
    def __init__(self):
        pass

    def init_payloads(self, tf_instance:TFCloudCustom, config_variables:json):

        # to create organization
        payload_organization = {
            "data": {
                "type": "organizations",
                "attributes": {
                    "name": config_variables['terraform_organization'],
                    "email": config_variables['terraform_email']
                }
            }}
    
        #To register github as vcp
        payload_vcp = {
        "data": {
            "type": "oauth-clients",
            "attributes": {
                "name": "GitHub OAuth",
                "service-provider": "github",
                "http-url": "https://github.com",
                "api-url": "https://api.github.com",
                "oauth-token-string": config_variables['github_api_token']
            }
        }}

        # to create workspace
        github_client_id = tf_instance.get_oauth_client_id_by_service_provider('github')
        github_oauth_token_id = tf_instance.get_oauth_token_id_by_client_id(github_client_id)
        
        payload_workspace = {
        "data": {
            "attributes": {
                "name": config_variables['terraform_workspace'],
                "working-directory": "/setup",
                "execution-mode": "remote",
                "trigger-prefixes": ["/setup"],
                "auto-apply":True,
                "vcs-repo": {
                    "identifier":f"{config_variables['github_user']}/{config_variables['github_repository']}",
                    "oauth-token-id": github_oauth_token_id,
                    "branch": ""
                }
            },
            "type": "workspaces"
            }
        }

        #to create local ip variable
        payload_local_ip = {
        "data": {
            "type":"vars",
            "attributes": {
                "key":"local_ip",
                "value":get_public_ip_address(),
                "description":"local ip address needed for firewall configs",
                "category":"terraform",
                "hcl":False,
                "sensitive":False
            }
        }}

        #to create hetzner cloud token variable
        payload_hcloud_token = {
        "data": {
            "type":"vars",
            "attributes": {
                "key":"hcloud_token",
                "value":config_variables['hetzner_api_token'],
                "description":"hetzner token to enable resource creation",
                "category":"terraform",
                "hcl":False,
                "sensitive":True
            }
        }}

        payloads = {"organization":payload_organization,
                    "vcp":payload_vcp,
                    "workspace":payload_workspace,
                    "local_ip":payload_local_ip,
                    "hcloud_token":payload_hcloud_token
                }
        return payloads

    
    def init_tf_resource_payload(self, tf_instance:TFCloudCustom):
        payload_init_tf_resources = {
            "data": {
                "attributes": {
                    "message": 'Initialising data platform'
                },
            "type":"runs",
            "relationships": {
                "workspace": {
                    "data": {
                        "type": "workspaces",
                        "id": tf_instance.get_workspace_id()
                    }
                }
            }
            }}
        return payload_init_tf_resources