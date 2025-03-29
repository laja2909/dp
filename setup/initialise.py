from dp.utils.terraform.TFCloudCustom import TFCloudCustom

class InitialiseProject:
    def __init__(self):
        pass

    def init_terraform_session(self):
        tf_session = TFCloudCustom()
        return tf_session

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
                    "message": "Destroy resources in this workspace",
                    "is-destroy": True  # This will indicate a destroy operation
                },
                "type": "runs"
            }
        }
        tf_session.run_in_workspace_runs_end_point(payload=payload)
        
    def init_project(self):
        # create terraform organization and workspace
        tf_session = self.init_terraform_session()
        tf_session.create_organization(organization_name=tf_session.get_organization_name())
        tf_session.create_workspace(workspace_name=tf_session.get_workspace_name())

if __name__=='__main__':
    init_proj = InitialiseProject()
    tf_session = init_proj.init_terraform_session()
    print(tf_session.get_header())


