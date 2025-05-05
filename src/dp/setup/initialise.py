import argparse

from dp.setup.Payloads import Payloads
from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from dp.utils.remote.RemoteSSH import RemoteSSH
from dp.utils.hetzner.HetznerApi import HetznerApi
from dp.utils.github.GithubApi import GithubApi

from dp.utils.confs import confs
from dp.utils.helper import get_env_variable


class ManageProject:
    def __init__(self):
        pass
    
    def init_terraform_resources(self):
        # create terraform organization
        tf_session = TFCloudCustom()
        payloads = Payloads()
        payloads_init = payloads.init_payloads()

        tf_session.create_organization(payload=payloads_init['organization'])
        tf_session.create_oauth_client(payload=payloads_init['vcp'])
        
        tf_session.create_workspace(payload=payloads_init['workspace'])

        tf_session.create_workspace_variable(payload=payloads_init['local_ip'])
        tf_session.create_workspace_variable(payload=payloads_init['hcloud_token'])

        payload_init_tf_resources = payloads.init_tf_resource_payload()
    
        tf_session.run_in_runs_end_point(payload=payload_init_tf_resources)

    def init_remote_server(self):
        tf_session = TFCloudCustom()
        # copy ssh keys from remote to local
        tf_session.copy_ssh_keys_from_remote_to_local(ssh_resource_name='generic-ssh-key')
        
        #variables for connecting to server
        server_name='dp' # resource name in main.tf
        hetz_api = HetznerApi()
        ip = hetz_api.get_server_ipv4_by_name(server_name=server_name)
        remote_user = get_env_variable(confs['remote']['user']['name']) # sign in as root user
        port = 22 # we've opened port 22 for ssh

        # commands to run in remote
        ## create project folder
        ## clone repo
        ## generate ssh key in remote
        https_github_repo = f"https://github.com/{get_env_variable(confs['github']['user']['name'])}/{get_env_variable(confs['github']['repository']['name'])}.git"
        commands = [
            'mkdir projects',
            #'git config --global user.name "dp"',
            #'git config --global user.email dp@gmail.com',
            f'cd ./projects && git clone {https_github_repo}',
            'cd ./projects && ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa <<<y >/dev/null 2>&1',
            'cd ./projects && cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys']
        
        
        # initialise connection
        ssh = RemoteSSH(hostname=ip, port=port, user=remote_user)
    
        #run commands
        for cmd in commands:
            ssh.execute_via_private_key(command=cmd)
        
    def init_github(self):
        git = GithubApi()
        
        git_vars = {'HETZ_MAIN_SERVER_NAME':'dp',
                    'MAIN_BRANCH':'main',
                    'WORK_DIR_IN_REMOTE':'projects'}

        #create github variables
        """
        for key,value in git_vars.items():
            git.create_repo_variable(var_name=key, var_value=value)
        """
        #create github secrets
        ##variables for connecting to server
        server_name='dp' # resource name in main.tf
        hetz_api = HetznerApi()
        ip = hetz_api.get_server_ipv4_by_name(server_name=server_name)
        remote_user = get_env_variable(confs['remote']['user']['name'])
        port = 22 # we've opened port 22 for ssh

        ssh = RemoteSSH(hostname=ip, port=port, user=remote_user)
        private_key_content = ssh.get_file_content_via_sftp(target_file_path='/root/.ssh/id_rsa')
        
        git_secrets = {'HETZ_TOKEN':get_env_variable(confs['hetzner']['api_token']['name']),
                       'SSH_HOST':ip,
                       'SSH_PRIVATE_KEY':private_key_content,
                       'SSH_USER':get_env_variable(confs['remote']['user']['name'])}
        
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
