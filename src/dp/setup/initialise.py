import json
from pathlib import Path
import argparse

from dp.setup.Payloads import Payloads
from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from dp.utils.remote.RemoteSSH import RemoteSSH
from dp.utils.hetzner.HetznerApi import HetznerApi
from dp.utils.github.GithubApi import GithubApi

from dp.utils.helper import get_global_confs


class ManageProject:
    def __init__(self, file_path_to_config_file:str=Path(__file__).parent.joinpath('confs.json').as_posix()):
        self._config = get_global_confs(file_path_to_config_file)
    
    def set_config(self,file_path_to_config_file:str):
        self._config = get_global_confs(file_path=file_path_to_config_file)

    def get_config(self) -> json:
        return self._config
    
    def init_terraform_resources(self):
        tf_cloud = TFCloudCustom(token=self.get_config()['terraform_api_token'],
                                 organization=self.get_config()['terraform_organization'],
                                 workspace=self.get_config()['terraform_workspace'])

        terraform_payloads = Payloads(tf_cloud, self.get_config())
        payloads_init = terraform_payloads.init_payloads()

        tf_cloud.create_organization(payload=payloads_init['organization'])
        tf_cloud.create_oauth_client(payload=payloads_init['vcp'])
        tf_cloud.create_workspace(payload=payloads_init['workspace'])

        tf_cloud.create_workspace_variable(payload=payloads_init['local_ip'])
        tf_cloud.create_workspace_variable(payload=payloads_init['hcloud_token'])

        payload_init_tf_resources = terraform_payloads.init_tf_resource_payload()
    
        tf_cloud.run_in_runs_end_point(payload=payload_init_tf_resources)

    def init_remote_server(self):
        tf_cloud = TFCloudCustom(token=self.get_config()['terraform_api_token'],
                            organization=self.get_config()['terraform_organization'],
                            workspace=self.get_config()['terraform_workspace'])

        # copy ssh keys from remote to local
        tf_cloud.copy_tls_ssh_keys_from_remote_to_local(to_key_name=self.get_config()['local_ssh_key_name'],
                                                        to_ssh_path_name=self.get_config()['local_ssh_path'])
        
        #variables for connecting to server
        hetz_api = HetznerApi()
        ip = hetz_api.get_server_ipv4_by_name(server_name=self.get_config()['hetzner_main_server_name'])

        # commands to run in remote
        ## create project folder
        ## clone repo
        ## generate ssh key in remote
        https_github_repo = f"https://github.com/{self.get_config()['github_user']}/{self.get_config()['github_repository']}.git"
        commands = [
            f'mkdir {self.get_config()['remote_root_folder_name']}',
            f'cd ./{self.get_config()['remote_root_folder_name']} && git clone {https_github_repo}',
            f'cd ./{self.get_config()['remote_root_folder_name']} && ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa <<<y >/dev/null 2>&1',
            f'cd ./{self.get_config()['remote_root_folder_name']} && cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys']
        
        
        # initialise connection
        ssh = RemoteSSH(hostname=ip,
                        port=self.get_config()['hetzner_firewall_ssh_port'],
                        user=self.get_config()['remote_user'])
    
        #run commands
        for cmd in commands:
            ssh.execute_via_private_key(command=cmd)
        
    def init_github(self):
        git = GithubApi()
        
        git_vars = {'HETZ_MAIN_SERVER_NAME':self.get_config()['hetzner_main_server_name'],
                    'MAIN_BRANCH':'main',
                    'WORK_DIR_IN_REMOTE':'projects'}

        #create github secrets
        hetz_api = HetznerApi()
        ip = hetz_api.get_server_ipv4_by_name(server_name=self.get_config()['hetzner_main_server_name'])

        ssh = RemoteSSH(hostname=ip,
                        port=self.get_config()['hetzner_firewall_ssh_port'], 
                        user=self.get_config()['remote_user'])
        private_key_content = ssh.get_file_content_via_sftp(target_file_path=f'/{self.get_config()['remote_user']}/.ssh/id_rsa')
        
        git_secrets = {'HETZ_TOKEN':self.get_config()['hetzner_api_token'],
                       'SSH_HOST':ip,
                       'SSH_PRIVATE_KEY':private_key_content,
                       'SSH_USER':self.get_config()['remote_user']}
        
        for key,value in git_secrets.items():
            git.create_repo_secret(secret_name=key, secret_value=value)
        
        print('done!')

        
        
    

if __name__=='__main__':
    init_proj = ManageProject()

    parser = argparse.ArgumentParser(description="Run a specific function.")
    parser.add_argument("function", choices=["init_terraform_resources",
                                             "init_remote_server",
                                             "init_github",
                                             "destroy_resources",
                                             "destroy_terraform_resources_workspace"])

    args = parser.parse_args()

    if args.function == "init_terraform_resources":
        init_proj.init_terraform_resources()
    elif args.function == "init_remote_server":
        init_proj.init_remote_server()
    elif args.function == "init_github":
        init_proj.init_github()
    elif args.function == "destroy_resources":
        tf_session = TFCloudCustom()
        tf_session.delete_resources_from_workspace()
    elif args.function == "destroy_terraform_resources_workspace":
        tf_session = TFCloudCustom()
        tf_session.delete_terraform_multiple_objects(objects=['resources','workspace'])
    else:
        print('pass')
