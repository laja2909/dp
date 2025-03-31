import argparse

from dp.utils.terraform.TFCloudCustom import TFCloudCustom
from dp.utils.confs import confs
from dp.utils.helper import get_env_variable, get_public_ip_address

class InitialiseProject:
    def __init__(self):
        pass

    def init_terraform_session(self):
        tf_session = TFCloudCustom()
        return tf_session
    
    def init_project(self):
        # create terraform organization
        tf_session = self.init_terraform_session()
        payload_organization = {
            "data": {
                "type": "organizations",
                "attributes": {
                    "name": tf_session.get_organization_name(),
                    "email": get_env_variable(confs['terraform']['email']['name'])
                }
            }}        
        tf_session.create_organization(payload=payload_organization)
        
        payload_workspace = {
            "data": {
                "attributes": {
                    "name": tf_session.get_workspace_name()
                },
                "type": "workspaces"
            }}
        
        
        """


        tf_session.create_workspace(payload=payload_workspace)

        # create workspace variables
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
        tf_session.create_workspace_variable(payload=payload_local_ip)
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
        tf_session.create_workspace_variable(payload=payload_hcloud_token)

        ## init resources 
        ##self.init_terraform_resources()
        """

    def init_terraform_resources(self):
        tf_session = self.init_terraform_session()
        if self.has_terraform_workspace_resources_running():
            raise Exception ('workspace already has resources initialised')

        payload = {
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
            }
        }
        tf_session.run_in_runs_end_point(payload=payload)

    def has_terraform_workspace_resources_running(self):
        tf_session = self.init_terraform_session()
        workspace_id = tf_session.get_workspace_id()
        resources = tf_session.get_resources_from_workspace(workspace_id)
        return len(resources['data'])>0
    
    def destroy_terraform_resources(self):
        tf_session = self.init_terraform_session()

        payload = {
            "data": {
                "attributes": {
                    "message": "Destroy resources in workspace",
                    "is_destroy": True
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
            }
        }
        tf_session.run_in_runs_end_point(payload=payload)

    def destroy_terraform_all(self):
        #1. destroy resources from workspace
        if self.has_terraform_workspace_resources_running():
            self.destroy_terraform_resources()
            print('Resources destroyed')
        else:
            print('No resources running. Skip destruction')
        ## delete workspace
        tf_session = self.init_terraform_session()
        tf_session.delete_workspace()
        ## delete organization
        tf_session.delete_organization()


        
    

if __name__=='__main__':
    init_proj = InitialiseProject()

    parser = argparse.ArgumentParser(description="Run a specific function.")
    parser.add_argument("function", choices=["init_project", "destroy_resources", "destroy_terraform_all"])

    args = parser.parse_args()

    if args.function == "init_project":
        init_proj.init_project()
    elif args.function == "destroy_resources":
        init_proj.destroy_terraform_resources()
    elif args.function == "destroy_terraform_all":
        init_proj.destroy_terraform_all()
    else:
        print('pass')
