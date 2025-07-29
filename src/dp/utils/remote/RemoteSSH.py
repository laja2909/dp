from pathlib import Path
import paramiko

from dp.utils.hetzner.HetznerApi import HetznerApi

class RemoteSSH:
    def __init__(self, hostname:str, port:int, user:str, private_key_name:str):
        self._hostname = hostname
        self._port = port
        self._user = user
        self._private_key_name = private_key_name
    
    def get_hostname(self):
        return self._hostname
    
    def get_port(self):
        return self._port
    
    def get_user(self):
        return self._user
    
    def get_private_key_name(self):
        return self._private_key_name

    def execute_via_private_key(self,command:str):
        #create ssh client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey.from_private_key_file(self.get_private_key_name())
        try:
            #connect
            ssh.connect(hostname=self.get_hostname(),
                        port=self.get_port(),
                        username=self.get_user(),
                        pkey=private_key)
            # Execute the command
            stdin, stdout, stderr = ssh.exec_command(command)
            # Fetch output and errors
            output = stdout.read().decode()
            error = stderr.read().decode()

            print("OUTPUT:")
            print(output)

            if error:
                print("ERROR:")
                print(error)
        finally:
            ssh.close()
    
    def get_file_content_via_sftp(self,target_file_path:str):
        #create ssh client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey.from_private_key_file(self.get_private_key_name())

        try:
            ssh.connect(hostname=self.get_hostname(),
                        port=self.get_port(),
                        username=self.get_user(),
                        pkey=private_key)
            try:
                sftp = ssh.open_sftp()
                with sftp.file(target_file_path, 'r') as remote_file:
                    content = remote_file.read().decode('utf-8')
            finally:
                sftp.close()
        finally:
            ssh.close()
        return content


if __name__=='__main__':
    hetz_api = HetznerApi()
    ip = hetz_api.get_server_ipv4_by_name('dp')

    ssh = RemoteSSH(hostname=ip, port=22, user='root')
    command = 'ls -la'
