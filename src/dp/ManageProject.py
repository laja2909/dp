import json
from pathlib import Path
import argparse

from dp.setup.source_confs import PayloadsTerraform, VariablesGithub
from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from dp.utils.remote.RemoteSSH import RemoteSSH
from dp.utils.hetzner.HetznerApi import HetznerApi
from dp.utils.github.GithubApi import GithubApi

from dp.utils.helper import get_global_confs


class ManageProject:
    def __init__(self, file_path_to_config_file:str=Path(__file__).parent.joinpath('setup/confs.json').as_posix()):
        self._config = get_global_confs(file_path_to_config_file)
    
    def set_config(self,file_path_to_config_file:str):
        self._config = get_global_confs(file_path=file_path_to_config_file)

    def get_config_variable(self, variable_name:str) -> json:
        return self._config[variable_name]['value']
    
    def get_config(self) -> json:
        return self._config
    
    def get_main_ids(self):
        hetz = HetznerApi(api_token=self.get_config_variable('hetzner_api_token'))
        ip = hetz.get_server_ipv4_by_name(server_name=self.get_config_variable('hetzner_main_server_name'))
        id_dict = {'hetzner_main_server_ip':ip}
        print(id_dict)


    def init_terraform_resources(self):
        tf_cloud = TFCloudCustom(token=self.get_config_variable('terraform_api_token'),
                                 organization=self.get_config_variable('terraform_organization'),
                                 workspace=self.get_config_variable('terraform_workspace'))
        
        #create terraform objects
        terraform_payloads = PayloadsTerraform(tf_cloud, self.get_config())
        tf_cloud.create_organization(payload=terraform_payloads.get_payload_organization())
        tf_cloud.create_oauth_client(payload=terraform_payloads.get_payload_vcp())
        terraform_payloads.set_payload_workspace(workspace_name=tf_cloud.get_workspace_name(),
                                                 github_user=self.get_config_variable('github_user'),
                                                 github_repo=self.get_config_variable('github_repository'))
        tf_cloud.create_workspace(payload=terraform_payloads.get_payload_workspace())
        
        #create terraform variables
        terraform_payloads.set_payload_variables(variables=self.get_config())
        if terraform_payloads.get_payload_variables():
            for key,value in terraform_payloads.get_payload_variables().items():
                tf_cloud.create_workspace_variable(payload=value)
        

    def init_remote_server(self):
        tf_cloud = TFCloudCustom(token=self.get_config_variable('terraform_api_token'),
                            organization=self.get_config_variable('terraform_organization'),
                            workspace=self.get_config_variable('terraform_workspace'))

        # copy ssh keys from remote to local
        tf_cloud.copy_tls_ssh_keys_from_remote_to_local(to_key_name=self.get_config_variable('local_ssh_key_name'),
                                                       to_ssh_path_name=self.get_config_variable('local_ssh_path'))
        
        # run commands in remote server
        ## variables for connecting to remote server
        hetz_api = HetznerApi(api_token=self.get_config_variable('hetzner_api_token'))
        ip = hetz_api.get_server_ipv4_by_name(server_name=self.get_config_variable('hetzner_main_server_name'))
        https_github_repo = f"https://github.com/{self.get_config_variable('github_user')}/{self.get_config_variable('github_repository')}.git"
        commands = [
            #create project directory
            f"mkdir {self.get_config_variable('remote_root_folder_name')}",
            #clone repo to project directory
            f"cd ./{self.get_config_variable('remote_root_folder_name')} && git clone {https_github_repo}",
            #generate ssh-key
            f"cd ./{self.get_config_variable('remote_root_folder_name')} && ssh-keygen -t rsa -b 4096 -N \"\" -f ~/.ssh/id_rsa <<<y >/dev/null 2>&1",
            #copy ssh key content to authorized keys
            f"cd ./{self.get_config_variable('remote_root_folder_name')} && cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys",
            #install python devs
            f"cd ./{self.get_config_variable('remote_root_folder_name')}/{self.get_config_variable('github_repository')} && apt-get update",
            f"cd ./{self.get_config_variable('remote_root_folder_name')}/{self.get_config_variable('github_repository')} && apt-get install -y python3-pip",
            f"cd ./{self.get_config_variable('remote_root_folder_name')}/{self.get_config_variable('github_repository')} && apt-get install -y python3-venv",
            #create venv
            f"cd ./{self.get_config_variable('remote_root_folder_name')}/{self.get_config_variable('github_repository')} && python3 -m venv venv",
            #activate venv and install requirements
            f"cd ./{self.get_config_variable('remote_root_folder_name')}/{self.get_config_variable('github_repository')} && source venv/bin/activate && python3 -m pip install -r requirements.txt",
            #activate venv and install project in editable state to get the imports work correctly
            f"cd ./{self.get_config_variable('remote_root_folder_name')}/{self.get_config_variable('github_repository')} && source venv/bin/activate && python3 -m pip install -e ."
            ]
        
        
        # initialise connection
        ssh = RemoteSSH(hostname=ip,
                        port=self.get_config_variable('hetzner_firewall_ssh_port'),
                        user=self.get_config_variable('remote_user'),
                        private_key_name=Path(self.get_config_variable('local_ssh_path')).joinpath(self.get_config_variable('local_ssh_key_name')).as_posix()
        )
    
        #run commands
        for cmd in commands:
            ssh.execute_via_private_key(command=cmd)
        
    def init_github(self):
        git = GithubApi(token=self.get_config_variable('github_api_token'))
        github_variables = VariablesGithub()
        github_variables.set_github_variables(variables=self.get_config())

        git_vars = {}
        git_secrets = {}
        for key,value in github_variables.get_github_variables().items():
            if value['github_configurations']['is_sensitive']=="False":
                git_vars.update({key:value['value']})
            else:
                git_secrets.update({key:value['value']})
        
        for key, value in git_vars.items():
            git.update_and_insert_repo_variable(var_name=key,var_value=value, owner=self.get_config_variable('github_user'),
                                     repo=self.get_config_variable('github_repository'))
        
        for key,value in git_secrets.items():
            git.update_and_insert_repo_secret(secret_name=key, secret_value=value,owner=self.get_config_variable('github_user'),
                                     repo=self.get_config_variable('github_repository'))
        
    def update_terraform_variables(self, list_of_variable_names=None):
        tf_cloud = TFCloudCustom(token=self.get_config_variable('terraform_api_token'),
                                 organization=self.get_config_variable('terraform_organization'),
                                 workspace=self.get_config_variable('terraform_workspace'))
        
        terraform_payloads = PayloadsTerraform(tf_cloud, self.get_config())
        #set terraform variables
        terraform_payloads.set_payload_variables(variables=self.get_config())
        
        if list_of_variable_names==None:
            if terraform_payloads.get_payload_variables():
                for key,value in terraform_payloads.get_payload_variables().items():
                    tf_cloud.create_workspace_variable(payload=value)
        else:
            if terraform_payloads.get_payload_variables():
                for key,value in terraform_payloads.get_payload_variables().items():
                    if key in list_of_variable_names:
                        tf_cloud.create_workspace_variable(payload=value)
                    else:
                        continue

    def update_local_ip_terraform_variable(self):
        self.update_terraform_variables(list_of_variable_names=['local_ip'])
        
    def trigger_terraform_run(self):
        tf_session = TFCloudCustom(token=init_proj.get_config_variable('terraform_api_token'),
                                 organization=init_proj.get_config_variable('terraform_organization'),
                                 workspace=init_proj.get_config_variable('terraform_workspace'))
        payload_trigger_run = {
             "data": {
                "attributes": {
                     "message": 'run triggered'
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
        tf_session.run_in_runs_end_point(payload=payload_trigger_run)

        
    

if __name__=='__main__':
    init_proj = ManageProject()

    parser = argparse.ArgumentParser(description="Run a specific function.")
    parser.add_argument("function", choices=["init_terraform_resources",
                                             "init_remote_server",
                                             "init_github",
                                             "trigger_terraform_run",
                                             "update_terraform_variables",
                                             "update_local_ip_terraform_variable",
                                             "get_main_ids",
                                             "destroy_resources",
                                             "destroy_terraform_resources_workspace"])

    args = parser.parse_args()

    if args.function == "init_terraform_resources":
        init_proj.init_terraform_resources()
    elif args.function == "init_remote_server":
        init_proj.init_remote_server()
    elif args.function == "init_github":
        init_proj.init_github()
    elif args.function == "trigger_terraform_run":
         init_proj.trigger_terraform_run()
    elif args.function == "update_terraform_variables":
        init_proj.update_terraform_variables()
    elif args.function == "update_local_ip_terraform_variable":
        init_proj.update_local_ip_terraform_variable()
    elif args.function == "get_main_ids":
        init_proj.get_main_ids()

    elif args.function == "destroy_resources":
        tf_session = TFCloudCustom(token=init_proj.get_config_variable('terraform_api_token'),
                                 organization=init_proj.get_config_variable('terraform_organization'),
                                 workspace=init_proj.get_config_variable('terraform_workspace'))
        tf_session.delete_resources_from_workspace()
    elif args.function == "destroy_terraform_resources_workspace":
        tf_cloud = TFCloudCustom(token=init_proj.get_config_variable('terraform_api_token'),
                                 organization=init_proj.get_config_variable('terraform_organization'),
                                 workspace=init_proj.get_config_variable('terraform_workspace'))
        tf_cloud.delete_terraform_multiple_objects(objects=['resources','workspace','organization'])
    else:
        print('pass')
