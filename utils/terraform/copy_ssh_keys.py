from pathlib import Path

from TFCloud import TFCloud
from helper import write_files_to_local, get_env_variable


def get_ssh_keys(ssh_resource_name:str) -> dict:
    ssh_key_dict = {}
    # init tfcloud instance
    tf_api = TFCloud()
    tf_api.set_header()
    tf_api.set_organization_name()
    tf_api.set_workspace_name()

    latest_state_version_id = tf_api.get_latest_state_version_id()
    state_file_content = tf_api.get_content_of_state_version(latest_state_version_id)

    for ind,value in enumerate(state_file_content['values']['root_module']['resources']):
        if value['name']==ssh_resource_name:
            ssh_key_dict['private_key'] = value['values']['private_key_openssh']
            ssh_key_dict['public_key'] = value['values']['public_key_openssh']
        else:
            continue
    return ssh_key_dict

def copy_ssh_keys_from_remote_to_local(ssh_resource_name:str,key_name:str,name_of_ssh_path_env_variable:str='SSH_PATH') -> None:
    """
    copies ssh keys from state file and saves them to local folder
    """
    ssh_path = Path(get_env_variable(name_of_ssh_path_env_variable))
    private_key_path = ssh_path.joinpath(key_name)
    public_key_path = ssh_path.joinpath(key_name+'.pub')

    # get ssh keys
    ssh_keys = get_ssh_keys(ssh_resource_name)
    #copy keys to local
    write_files_to_local(ssh_keys['private_key'],private_key_path)
    write_files_to_local(ssh_keys['public_key'],public_key_path)

if __name__=='__main__':
    copy_ssh_keys_from_remote_to_local('generic-ssh-key','id_hetz')
    