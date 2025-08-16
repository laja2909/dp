import json

from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from dp.utils.hetzner.HetznerApi import HetznerApi
from dp.utils.remote.RemoteSSH import RemoteSSH
from dp.utils.helper import get_public_ip_address


class InitTerraform:
    def __init__(self, tf_instance:TFCloudCustom, config_variables:json):
        self.terraform_cloud_instance = tf_instance
        
        self._payload_organization = {
            "data": {
                "type": "organizations",
                "attributes": {
                    "name": config_variables['terraform_organization']['value'],
                    "email": config_variables['terraform_email']['value']
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
                    "oauth-token-string": config_variables['github_api_token']['value']
                }
            }}
    
    def get_payload_organization(self):
        return self._payload_organization
    
    def get_payload_vcp(self):
        return self._payload_vcp
    
    def get_payload_workspace(self):
        return self._payload_workspace
    
    def get_payload_variables(self):
        return self._payload_variables
    
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
                    "branch": "main"
                }
            },
            "type": "workspaces"
            }
        }

    def set_payload_variables(self,variables:dict):
        final_variable_dict = {}

        #dynamic variables
        final_variable_dict.update(
        {"local_ip":
            {"data": {
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
        })
        
        #static variables
        for key,value in variables.items():
            if value.get("terraform_configurations"):
                final_variable_dict.update(
                    {key:
                     {"data": {
                         "type":"vars",
                         "attributes": {
                             "key":key,
                             "value":value['value'],
                             "description":"",
                             "category":"terraform",
                             "hcl":False,
                             "sensitive":value['terraform_configurations']['is_sensitive']=="True"
                            }
                        }
                    }})
        self._payload_variables = final_variable_dict
    

class InitRemote:
    def __init__(self):
        pass

    def get_initialisation_script(self):
        return self._initialisation_script.strip()

    def set_initialisation_script(self,variables:dict):
        https_github_repo = f"https://github.com/{variables['github_user']['value']}/{variables['github_repository']['value']}.git"
        self._initialisation_script = f"""
        set -e
        mkdir -p {variables['remote_root_folder_name']['value']}
        cd {variables['remote_root_folder_name']['value']}
        git clone {https_github_repo}
        ssh-keygen -t rsa -b 4096 -N \"\" -f ~/.ssh/id_rsa <<<y >/dev/null 2>&1
        cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
        cd {variables['github_repository']['value']}
        sudo apt-get update
        sudo apt-get install -y python3-pip python3-venv
        python3 -m venv venv
        source venv/bin/activate
        python3 -m pip install -r requirements.txt
        python3 -m pip install -e .
        """

class InitGithub:
    def __init__(self):
        pass

    def get_github_variables(self):
        return self._github_variables
    
    def set_github_variables(self,variables:dict):
        #static variables
        final_variable_dict = {}
        for key,value in variables.items():
            if value.get("github_configurations"):
                final_variable_dict.update({key:value})
        
        #dynamic variables
        hetz_api = HetznerApi(api_token=variables['hetzner_api_token']['value'])
        ip = hetz_api.get_server_ipv4_by_name(server_name=variables['hetzner_main_server_name']['value'])
        ssh = RemoteSSH(hostname=ip,
                        port=variables['hetzner_firewall_ssh_port']['value'], 
                        user=variables['remote_user']['value'],
                        private_key_name=f"{variables['local_ssh_path']['value']}/{variables['local_ssh_key_name']['value']}")
        private_key_content = ssh.get_file_content_via_sftp(target_file_path=f"/{ssh.get_user()}/.ssh/id_rsa")
        
        final_variable_dict.update({'REMOTE_SSH_HOST_IP':
                                        {'value':ip,
                                         'terraform_configurations':None,
                                         'github_configurations':{
                                             'is_github_variable':"True",
                                             'is_sensitive':"True"
                                             }
                                        }
                                    })
        final_variable_dict.update({'REMOTE_SSH_PRIVATE_KEY':
                                        {'value':private_key_content,
                                         'terraform_configurations':None,
                                         'github_configurations':{
                                             'is_github_variable':"True",
                                             'is_sensitive':"True"
                                             }
                                        }
                                    })
        
        self._github_variables = final_variable_dict

class InitAirflow:
    def __init__(self):
        pass

    def get_initialisation_script(self):
        return self._initialisation_script.strip()

    def set_initialisation_script(self,variables:dict):
        self._initialisation_script = f"""
        set -e
        sudo apt update
        sudo apt upgrade -y
        sudo apt install -y ca-certificates curl gnupg lsb-release
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
            https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | \
            sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt update
        sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        sudo usermod -aG docker $USER
        newgrp docker
        cd {variables['remote_root_folder_name']['value']}\dp\src\dp\setup\airflow
        echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
        docker compose up airflow-init
        docker compose up -d
        """