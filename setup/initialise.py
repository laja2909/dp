from dp.utils.terraform.TFCloudCustom import TFCloudCustom

class InitialiseProject:
    def __init__(self):
        pass

    def init_terraform_session(self):
        tf_session = TFCloudCustom()
        tf_session.set_header()
        tf_session.set_organization_name()
        tf_session.set_workspace_name()
        return tf_session

    def init_terraform_resources(self):
        tf_session = self.init_terraform_session()
        if self.has_terraform_workspace_resources_running():
            raise Exception ('workspace already has resources initialised')
        tf_session.run_with_message('Initialising data platform')

    def has_terraform_workspace_resources_running(self):
        tf_session = self.init_terraform_session()
        workspace_id = tf_session.get_workspace_id()
        resources = tf_session.get_resources_from_workspace(workspace_id)
        return len(resources['data'])>0
    
    def destroy_terraform_resources(self):
        tf_session = self.init_terraform_session()
        
        
        



if __name__=='__main__':
    init_proj = InitialiseProject()
    init_proj.init_terraform_resources()


