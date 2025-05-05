from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from dp.utils.confs import confs
from dp.utils.helper import get_env_variable, get_public_ip_address


class Payloads:
    def __init__(self):
        pass

    def init_payloads(self):
        tf_session = TFCloudCustom()

        # to create organization
        payload_organization = {
            "data": {
                "type": "organizations",
                "attributes": {
                    "name": tf_session.get_organization_name(),
                    "email": get_env_variable(confs['terraform']['email']['name'])
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
                #'key':get_env_variable(confs['github']['tc_client_id']['name']),
                #'secret':get_env_variable(confs['github']['tc_client_token']['name']),
                "oauth-token-string": get_env_variable(confs['github']['api_token']['name'])
            }
        }}

        # to create workspace
        github_client_id = tf_session.get_oauth_client_id_by_service_provider('github')
        github_oauth_token_id = tf_session.get_oauth_token_id_by_client_id(github_client_id)
        
        payload_workspace = {
        "data": {
            "attributes": {
                "name": tf_session.get_workspace_name(),
                "working-directory": "/setup",
                "execution-mode": "remote",
                "trigger-prefixes": ["/setup"],
                "auto-apply":True,
                "vcs-repo": {
                    "identifier":f"{get_env_variable(confs['github']['user']['name'])}/{get_env_variable(confs['github']['repository']['name'])}",
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
                "value":get_env_variable(confs['hetzner']['api_token']['name']),
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

    
    def init_tf_resource_payload(self):
        tf_session = TFCloudCustom()
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
                        "id": tf_session.get_workspace_id()
                    }
                }
            }
            }}
        return payload_init_tf_resources