import argparse

from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from Payloads import Payloads

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
        tf_session.copy_ssh_keys_from_remote_to_local(ssh_resource_name='generic-ssh-key', key_name='id_hetzner')

        # create project folder
        # clone repo
        # generate ssh key in remote

        # add secrets to github
        pass
        
    

if __name__=='__main__':
    init_proj = ManageProject()

    parser = argparse.ArgumentParser(description="Run a specific function.")
    parser.add_argument("function", choices=["init_terraform_resources", "init_remote_server","destroy_resources", "destroy_terraform_resources_workspace"])

    args = parser.parse_args()

    if args.function == "init_terraform_resources":
        init_proj.init_terraform_resources()
    elif args.function == "init_remote_server":
        init_proj.init_remote_server()
    elif args.function == "destroy_resources":
        tf_session = TFCloudCustom()
        tf_session.delete_resources_from_workspace()
    elif args.function == "destroy_terraform_resources_workspace":
        tf_session = TFCloudCustom()
        tf_session.delete_terraform_multiple_objects(objects=['resources','workspace'])
    else:
        print('pass')
