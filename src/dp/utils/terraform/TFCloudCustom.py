import argparse
from pathlib import Path

from dp.utils.terraform.TFCloud import TFCloud
from dp.utils.helper import get_public_ip_address, write_files_to_local

class TFCloudCustom(TFCloud):
    """
    Class to help with Terraform Cloud API calls
    This class is specific to data platform project which is why subclass is created.

    
    """
    def __init__(self,token:str,organization:str,workspace:str):
        super().__init__(token,organization,workspace)
    
    def change_local_ip_variable_to_current_public_ip(self,tf_local_ip_variable_name:str):
        # check if local ip variable is the same as current public ip address
        current_public_address = get_public_ip_address()
        is_equal = self.is_equal_to_variable_value(current_public_address,tf_local_ip_variable_name)

        if is_equal:
            print('ip addresses are equal')
            pass
        else:
            print('changing the ip address variable')
            payload = {
                "data":{
                    "id":self.get_variable_id(tf_local_ip_variable_name),
                    "attributes":{
                        "key":tf_local_ip_variable_name,
                        "value":current_public_address,
                        "description": "Changing local ip variable",
                        "category":"terraform",
                        "hcl": False,
                        "sensitive": False
                },
                "type":"vars"
            }}
            self.update_variable_value(variable_name=tf_local_ip_variable_name,payload=payload)

    def get_tls_ssh_keys(self) -> dict:
        ssh_key_dict = {}
        latest_state_version_id = self.get_latest_state_version_id()
        state_file_content = self.get_content_of_state_version(latest_state_version_id)

        for ind,value in enumerate(state_file_content['values']['root_module']['resources']):
            if value['type']=='tls_private_key':
                ssh_key_dict['private_key'] = value['values']['private_key_openssh']
                ssh_key_dict['public_key'] = value['values']['public_key_openssh']
            else:
                continue
        return ssh_key_dict

    def copy_tls_ssh_keys_from_remote_to_local(self,to_key_name:str,to_ssh_path_name:str) -> None:
        """
        copies ssh keys from state file and saves them to local folder
        """
        ssh_path = Path(to_ssh_path_name)
        private_key_path = ssh_path.joinpath(to_key_name)
        public_key_path = ssh_path.joinpath(to_key_name+'.pub')

        # get ssh keys
        ssh_keys = self.get_tls_ssh_keys()
        #copy keys to local
        write_files_to_local(ssh_keys['private_key'],private_key_path)
        write_files_to_local(ssh_keys['public_key'],public_key_path)

    def run_change_local_ip_variable_to_current_public_ip(self,tf_local_ip_variable_name:str):
        ##change the variable name
        self.change_local_ip_variable_to_current_public_ip(tf_local_ip_variable_name)
        ##immediately run the change
        payload = {
            "data": {
                "attributes": {
                    "message": "Changing local ip variable to current public ip"
                },
                "type":"runs",
                "relationships": {
                    "workspace": {
                        "data": {
                            "type": "workspaces",
                            "id": self.get_workspace_id()
                        }
                    }
                }
            }
        }
        self.run_in_runs_end_point(payload=payload)


if __name__=='__main__':
    # init tfcloud instance
    tf_api = TFCloudCustom()
    parser = argparse.ArgumentParser(description="Run a specific function.")
    parser.add_argument("function", choices=["change_local_ip", "copy_ssh_key"])

    args = parser.parse_args()

    if args.function == "change_local_ip":
        tf_api.run_change_local_ip_variable_to_current_public_ip('local_ip')
    elif args.function == "copy_ssh_key":
        tf_api.copy_ssh_keys_from_remote_to_local('generic-ssh-key','id_hetz')
    else:
        pass
    

