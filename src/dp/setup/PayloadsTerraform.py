import json

from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from dp.utils.helper import get_public_ip_address


class PayloadsTerraform:
    def __init__(self, tf_instance:TFCloudCustom, config_variables:json):
        self.terraform_cloud_instance = tf_instance
        
        self._payload_organization = {
            "data": {
                "type": "organizations",
                "attributes": {
                    "name": config_variables['terraform_organization'],
                    "email": config_variables['terraform_email']
                }
            }}
        
        self._payload_vcp = {
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
        
        self._payload_public_ip ={
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
        
        self._payload_hcloud_token = {
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
    
    def get_payload_organization(self):
        return self._payload_organization
    
    def get_payload_vcp(self):
        return self._payload_vcp
    
    def get_payload_workspace(self):
        return self._payload_workspace
    
    def get_payload_public_ip(self):
        return self._payload_public_ip
    
    def get_payload_hcloud_token(self):
        return self._payload_hcloud_token
     
    def set_payload_workspace(self, workspace_name:str, github_user:str, github_repo:str):
        # to create workspace
        github_client_id = self.terraform_cloud_instance.get_oauth_client_id_by_service_provider('github')
        github_oauth_token_id = self.terraform_cloud_instance.get_oauth_token_id_by_client_id(github_client_id)
        
        self._payload_workspace = {
        "data": {
            "attributes": {
                "name": workspace_name,
                "working-directory": "./src/dp/setup",
                "execution-mode": "remote",
                "trigger-prefixes": ["./src/dp/setup"],
                "auto-apply":True,
                "vcs-repo": {
                    "identifier":f"{github_user}/{github_repo}",
                    "oauth-token-id": github_oauth_token_id,
                    "branch": ""
                }
            },
            "type": "workspaces"
            }
        }
