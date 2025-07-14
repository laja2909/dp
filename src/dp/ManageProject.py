import json
from pathlib import Path
import argparse

from dp.setup.PayloadsTerraform import PayloadsTerraform
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
    
    def init_terraform_resources(self):
        tf_cloud = TFCloudCustom(token=self.get_config_variable('terraform_api_token'),
                                 organization=self.get_config_variable('terraform_organization'),
                                 workspace=self.get_config_variable('terraform_workspace'))
        
        terraform_payloads = PayloadsTerraform(tf_cloud, self.get_config())
        #create terraform organization
        tf_cloud.create_organization(payload=terraform_payloads.get_payload_organization())
        # create github client for the version control
        tf_cloud.create_oauth_client(payload=terraform_payloads.get_payload_vcp())

        #set terrafrom workspace payload
        terraform_payloads.set_payload_workspace(workspace_name=tf_cloud.get_workspace_name(),
                                                 github_user=self.get_config_variable('github_user'),
                                                 github_repo=self.get_config_variable('github_repository'))
        
        tf_cloud.create_workspace(payload=terraform_payloads.get_payload_workspace())
        
        #set terraform variables
        terraform_payloads.set_payload_variables(variables=self.get_config_variable())

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
        
        #variables for connecting to server
        hetz_api = HetznerApi(api_token=self.get_config_variable('hetzner_api_token'))
        ip = hetz_api.get_server_ipv4_by_name(server_name=self.get_config_variable('hetzner_main_server_name'))

        
        # commands to run in remote
        ## create project folder
        ## clone repo
        ## generate ssh key in remote
        https_github_repo = f"https://github.com/{self.get_config_variable('github_user')}/{self.get_config_variable('github_repository')}.git"
        commands = [
            f"mkdir {self.get_config_variable('remote_root_folder_name')}",
            f"cd ./{self.get_config_variable('remote_root_folder_name')} && git clone {https_github_repo}",
            f"cd ./{self.get_config_variable('remote_root_folder_name')} && ssh-keygen -t rsa -b 4096 -N \"\" -f ~/.ssh/id_rsa <<<y >/dev/null 2>&1",
            f"cd ./{self.get_config_variable('remote_root_folder_name')} && cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys",
            f"cd ./{self.get_config_variable('remote_root_folder_name')}/{self.get_config_variable('github_repository')} && apt install python3-pip && apt install python3-venv && python3 -m venv venv",
            f"cd ./{self.get_config_variable('remote_root_folder_name')}/{self.get_config_variable('github_repository')} && source venv/bin/activate && python3 -m pip install -r requirements.txt",
            f"cd ./{self.get_config_variable('remote_root_folder_name')}/{self.get_config_variable('github_repository')} && python3 -m pip install -e ."
            ]
        
        
        # initialise connection
        ssh = RemoteSSH(hostname=ip,
                        port=self.get_config_variable('hetzner_firewall_ssh_port'),
                        user=self.get_config_variable('remote_user'))
    
        #run commands
        for cmd in commands:
            ssh.execute_via_private_key(command=cmd, private_key_path=self.get_config_variable('local_ssh_path'),
                                        key_name=self.get_config_variable('local_ssh_key_name'))
        
        
    def init_github(self):
        git = GithubApi(token=self.get_config_variable('github_api_token'))
        
        git_vars = {'HETZNER_MAIN_SERVER_NAME':self.get_config_variable('hetzner_main_server_name'),
                    'GIT_MAIN_BRANCH_NAME':'main',
                    'REMOTE_ROOT_FOLDER_NAME':self.get_config_variable('remote_root_folder_name'),
                    'GIT_REPOSITORY': self.get_config_variable('github_repository')}

        for key, value in git_vars.items():
            git.create_repo_variable(var_name=key,var_value=value, owner=self.get_config_variable('github_user'),
                                     repo=self.get_config_variable('github_repository'))
        
        #create github secrets
        hetz_api = HetznerApi(api_token=self.get_config_variable('hetzner_api_token'))
        ip = hetz_api.get_server_ipv4_by_name(server_name=self.get_config_variable('hetzner_main_server_name'))

        ssh = RemoteSSH(hostname=ip,
                        port=self.get_config_variable('hetzner_firewall_ssh_port'), 
                        user=self.get_config_variable('remote_user'))
        private_key_content = ssh.get_file_content_via_sftp(target_file_path=f"/{self.get_config_variable('remote_user')}/.ssh/id_rsa",
                                                            private_key_path=self.get_config_variable('local_ssh_path'),
                                                            key_name=self.get_config_variable('local_ssh_key_name'))
        
        git_secrets = {'HETZNER_TOKEN':self.get_config_variable('hetzner_api_token'),
                       'REMOTE_SSH_HOST_IP':ip,
                       'REMOTE_SSH_PRIVATE_KEY':private_key_content,
                       'REMOTE_SSH_USER':self.get_config_variable('remote_user')}
        
        for key,value in git_secrets.items():
            git.create_repo_secret(secret_name=key, secret_value=value,owner=self.get_config_variable('github_user'),
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

    elif args.function == "destroy_resources":
        tf_session = TFCloudCustom(token=init_proj.get_config_variable()['terraform_api_token']['value'],
                                 organization=init_proj.get_config_variable()['terraform_organization']['value'],
                                 workspace=init_proj.get_config_variable()['terraform_workspace']['value'])
        tf_session.delete_resources_from_workspace()
    elif args.function == "destroy_terraform_resources_workspace":
        tf_cloud = TFCloudCustom(token=init_proj.get_config_variable()['terraform_api_token']['value'],
                                 organization=init_proj.get_config_variable()['terraform_organization']['value'],
                                 workspace=init_proj.get_config_variable()['terraform_workspace']['value'])
        tf_cloud.delete_terraform_multiple_objects(objects=['resources','workspace','organization'])
    else:
        print('pass')
