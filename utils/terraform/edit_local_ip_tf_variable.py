from TFCloud import TFCloud
from helper import get_public_ip_address


def change_tf_local_ip_variable_to_current_public_ip(tf_local_ip_variable_name:str):
    # init tfcloud instance
    tf_api = TFCloud()
    tf_api.set_header()
    tf_api.set_organization_name()
    tf_api.set_workspace_name()

    # check if local ip variable is the same as current public ip address
    current_public_address = get_public_ip_address()
    is_equal = tf_api.is_equal_to_variable_value(current_public_address,tf_local_ip_variable_name)

    if is_equal:
        print('ip addresses are equal')
        pass
    else:
        print('changing the ip address variable')
        tf_api.edit_variable_value(variable_name=tf_local_ip_variable_name,new_variable_value=current_public_address)

if __name__ == '__main__':
    change_tf_local_ip_variable_to_current_public_ip('local_ip')
