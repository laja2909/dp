import json
from pathlib import Path
import argparse

from dp.setup.source_confs import InitTerraform, InitGithub, InitRemote
from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from dp.utils.remote.RemoteSSH import RemoteSSH
from dp.utils.hetzner.HetznerApi import HetznerApi
from dp.utils.github.GithubApi import GithubApi
from dp.utils.aws.AWS import AWS

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
        return id_dict
    
    def get_project_objects_status(self):
        """
        checks default project objects if they are actively running
        """
        project_objects = {}
        #check for terraform objects
        tf_cloud = TFCloudCustom(token=self.get_config_variable('terraform_api_token'),
                                 organization=self.get_config_variable('terraform_organization'),
                                 workspace=self.get_config_variable('terraform_workspace'))
        ## organization
        project_objects.update({'terraform_organization':tf_cloud.has_terraform_organization()})

        #check for hetzner
        hetz_api = HetznerApi(api_token=self.get_config_variable('hetzner_api_token'))
        ##servers
        project_objects.update({'hetzner_servers':hetz_api.has_servers_running()})

        #check for aws
        aws_api = AWS(aws_access_key=self.get_config_variable('aws_access_key'), aws_secret_access_key=self.get_config_variable('aws_secret_access_key'))
        ##bucket
        project_objects.update({'aws_bucket':aws_api.has_bucket(bucket_name=self.get_config_variable('aws_s3_bucket_name'))})
        return project_objects

    #INITIALISATIONS
    def init_terraform_resources(self):
        tf_cloud = TFCloudCustom(token=self.get_config_variable('terraform_api_token'),
                                 organization=self.get_config_variable('terraform_organization'),
                                 workspace=self.get_config_variable('terraform_workspace'))
        
        #create terraform objects
        terraform_payloads = InitTerraform(tf_cloud, self.get_config())
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
        #copy ssh key from terraform state file to access the remote server
        tf_cloud = TFCloudCustom(token=self.get_config_variable('terraform_api_token'),
                                 organization=self.get_config_variable('terraform_organization'),
                                 workspace=self.get_config_variable('terraform_workspace'))
        tf_cloud.copy_tls_ssh_keys_from_remote_to_local(to_key_name=self.get_config_variable('local_ssh_key_name'),
                                                        to_ssh_path_name=self.get_config_variable('local_ssh_path'))
        

        # variables for connecting to remote server
        hetz_api = HetznerApi(api_token=self.get_config_variable('hetzner_api_token'))
        ip = hetz_api.get_server_ipv4_by_name(server_name=self.get_config_variable('hetzner_main_server_name'))
        # initialise connection
        ssh = RemoteSSH(hostname=ip,
                        port=self.get_config_variable('hetzner_firewall_ssh_port'),
                        user=self.get_config_variable('remote_user'),
                        private_key_name=Path(self.get_config_variable('local_ssh_path')).joinpath(self.get_config_variable('local_ssh_key_name')).as_posix()
        )


        #initialise remote script
        remote_script = InitRemote()
        remote_script.set_initialisation_script(variables=self.get_config())
        
        ssh.execute_via_private_key(command=remote_script.get_initialisation_script())
        
    def init_github(self):
        git = GithubApi(token=self.get_config_variable('github_api_token'))
        github_variables = InitGithub()
        github_variables.set_github_variables(variables=self.get_config())
        git_vars = {}
        git_secrets = {}
        for key,value in github_variables.get_github_variables().items():
            if value['github_configurations']['is_sensitive']=="False":
                git_vars.update({key:value['value']})
            else:
                git_secrets.update({key:value['value']})

        for key, value in git_vars.items():
            if key.startswith('github_'):
                new_key=key.replace('github_','git_',1)
                git.update_and_insert_repo_variable(var_name=new_key,var_value=value, owner=self.get_config_variable('github_user'),
                                                    repo=self.get_config_variable('github_repository'))
            else:
                git.update_and_insert_repo_variable(var_name=key,var_value=value, owner=self.get_config_variable('github_user'),
                                                    repo=self.get_config_variable('github_repository'))

        for key,value in git_secrets.items():
            if key.startswith('github_'):
                new_key=key.replace('github_','git_',1)
                git.update_and_insert_repo_secret(secret_name=new_key,secret_value=value, owner=self.get_config_variable('github_user'),
                                                    repo=self.get_config_variable('github_repository'))
            else:
                git.update_and_insert_repo_secret(secret_name=key,secret_value=value, owner=self.get_config_variable('github_user'),
                                                    repo=self.get_config_variable('github_repository'))
        

    def init_airflow(self):
        # variables for connecting to remote server
        hetz_api = HetznerApi(api_token=self.get_config_variable('hetzner_api_token'))
        ip = hetz_api.get_server_ipv4_by_name(server_name=self.get_config_variable('hetzner_main_server_name'))
        # initialise connection
        ssh = RemoteSSH(hostname=ip,
                        port=self.get_config_variable('hetzner_firewall_ssh_port'),
                        user=self.get_config_variable('remote_user'),
                        private_key_name=Path(self.get_config_variable('local_ssh_path')).joinpath(self.get_config_variable('local_ssh_key_name')).as_posix()
        )


        #initialise airflow script
        ##airflow_script = InitAirflow()
        ##InitAirflow.set_initialisation_script(variables=self.get_config())
        
        ##ssh.execute_via_private_key(command=remote_script.get_initialisation_script())

        
    def update_and_insert_terraform_variables(self, list_of_variable_names=None):
        tf_cloud = TFCloudCustom(token=self.get_config_variable('terraform_api_token'),
                                 organization=self.get_config_variable('terraform_organization'),
                                 workspace=self.get_config_variable('terraform_workspace'))
        
        terraform_payloads = InitTerraform(tf_cloud, self.get_config())
        #set terraform variables
        terraform_payloads.set_payload_variables(variables=self.get_config())
        
        if list_of_variable_names==None:
            if terraform_payloads.get_payload_variables():
                for key,value in terraform_payloads.get_payload_variables().items():
                    tf_cloud.update_and_insert_workspace_variable(variable_name=key,payload=value)
        else:
            if terraform_payloads.get_payload_variables():
                for key,value in terraform_payloads.get_payload_variables().items():
                    if key in list_of_variable_names:
                        tf_cloud.update_and_insert_workspace_variable(variable_name=key,payload=value)
                    else:
                        continue
    #UPDATES
    def update_and_insert_local_ip_terraform_variable(self):
        self.update_and_insert_terraform_variables(list_of_variable_names=['local_ip'])
    
    #RUNS
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
                                             "update_and_insert_terraform_variables",
                                             "update_and_insert_local_ip_terraform_variable",
                                             "get_main_ids",
                                             "get_project_objects_status",
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
    elif args.function == "update__and_insert_terraform_variables":
        init_proj.update_and_insert_terraform_variables()
    elif args.function == "update_and_insert_local_ip_terraform_variable":
        init_proj.update_and_insert_local_ip_terraform_variable()
    elif args.function == "get_main_ids":
        print(init_proj.get_main_ids())
    elif args.function == "get_project_objects_status":
        project_objects_statuses = init_proj.get_project_objects_status()
        print(project_objects_statuses)

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
