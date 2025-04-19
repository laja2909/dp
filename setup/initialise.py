import argparse

from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from payloads import init_payloads

class InitialiseProject:
    def __init__(self):
        pass
    
    def init_project(self):
        # create terraform organization
        tf_session = TFCloudCustom()
        payloads = init_payloads()

        #tf_session.create_organization(payload=payloads['organization'])
        #tf_session.create_oauth_client(payload=payloads['vcp'])
        
        #tf_session.create_workspace(payload=payloads['workspace'])

        #tf_session.create_workspace_variable(payload=payloads['local_ip'])
        #tf_session.create_workspace_variable(payload=payloads['hcloud_token'])
    
        tf_session.run_in_runs_end_point(payload=payloads['init_tf_resources'])
        
    

if __name__=='__main__':
    init_proj = InitialiseProject()

    parser = argparse.ArgumentParser(description="Run a specific function.")
    parser.add_argument("function", choices=["init_project", "destroy_resources", "destroy_terraform_resources_workspace"])

    args = parser.parse_args()

    if args.function == "init_project":
        init_proj.init_project()
    elif args.function == "destroy_resources":
        tf_session = TFCloudCustom()
        tf_session.delete_resources_from_workspace()
    elif args.function == "destroy_terraform_resources_workspace":
        tf_session = TFCloudCustom()
        tf_session.delete_terraform_multiple_objects(objects=['resources','workspace'])
    else:
        print('pass')
