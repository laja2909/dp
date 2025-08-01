import requests
import json
from pathlib import Path

from base64 import b64encode
from nacl import encoding, public

from dp.utils.helper import get_global_confs
from dp.utils.general.API import API

class GithubApi(API):
    """
    Class to help with Github API calls
    
    """
    def __init__(self,token:str):
        self._header = {'Authorization': f'token {token}',
                        'Accept': 'application/vnd.github+json'}
    
    def get_header(self):
        return self._header
    
    def create_repo_variable(self,var_name:str, var_value:str,owner:str,repo:str) -> json:
        endpoint = f'https://api.github.com/repos/{owner}/{repo}/actions/variables'

        payload = {'name':var_name, 'value':var_value}
        response = self.call_endpoint(method='POST',endpoint=endpoint, headers=self.get_header(),payload=payload)
        content = self.get_content_response(response)
        return content
    
    def encrypt(self, public_key:str, secret_value:str) -> str:
        """Encrypt a Unicode string using the public key."""
        public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return b64encode(encrypted).decode("utf-8")


    def create_repo_secret(self,secret_name:str, secret_value:str,owner:str,repo:str) -> json:
        
        #get public key
        endpoint_public_key = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key'
        response = self.call_endpoint(method='GET',endpoint=endpoint_public_key, headers=self.get_header())
        content = self.get_content_response(response)
        public_key = content["key"]
        key_id = content["key_id"]

        #encrypt the secret
        encrypted_secret = self.encrypt(public_key,secret_value)

        #upload secret
        endpoint_secret_url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}"
        payload = {
             "encrypted_value": encrypted_secret,
             "key_id": key_id}
        response = self.call_endpoint(method='PUT',endpoint=endpoint_secret_url,headers=self.get_header(),payload=payload)
        content = self.get_content_response(response)

        return content

    def update_and_insert_repo_secret(self,secret_name:str,secret_value:str,owner:str,repo:str) -> json:
        """
        if secret variable already exists, update it's value, if not create it.
        
        """
        repo_secrets = self.get_repo_secrets(owner=owner, repo=repo).get('secrets')
        
        secret_exists = False
        # loop through repo secrets
        if repo_secrets!=None:
            for secret in repo_secrets:
                if secret['name']==secret_name.upper():
                    secret_exists=True
                    break
                else:
                    continue
        
        if secret_exists:
            self.delete_repo_secret(secret_name=secret_name,owner=owner,repo=repo)
            self.create_repo_secret(secret_name=secret_name,secret_value=secret_value,owner=owner,repo=repo)
        else:
            self.create_repo_secret(secret_name=secret_name,secret_value=secret_value,owner=owner,repo=repo)

    
    def update_and_insert_repo_variable(self,var_name:str, var_value:str,owner:str,repo:str) -> json:
        """
        if variable already exists, update it's value, if not create it.
        
        """
        repo_variables = self.get_repo_variables(owner=owner, repo=repo).get('variables')
        
        variable_exists = False
        # loop through repo secrets
        if repo_variables!=None:
            for variable in repo_variables:
                if variable['name']==var_name.upper():
                    variable_exists=True
                    break
                else:
                    continue
        
        if variable_exists:
            self.delete_repo_variable(var_name=var_name,owner=owner,repo=repo)
            self.create_repo_variable(var_name=var_name,var_value=var_value,owner=owner,repo=repo)
        else:
            self.create_repo_variable(var_name=var_name,var_value=var_value,owner=owner,repo=repo)

    def get_repo_secrets(self,owner:str,repo:str) -> json:

        endpoint = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets'
        response = self.call_endpoint(method='GET',endpoint=endpoint, headers=self.get_header())
        content = self.get_content_response(response)
        return content
    
    def get_repo_variables(self,owner:str,repo:str) -> json:

        endpoint = f'https://api.github.com/repos/{owner}/{repo}/actions/variables'
        response = self.call_endpoint(method='GET',endpoint=endpoint,headers=self.get_header())
        content = self.get_content_response(response)
        return content
    
    #DELETE
    def delete_repo_variable(self,var_name:str,owner:str,repo:str) -> json:

        endpoint = f'https://api.github.com/repos/{owner}/{repo}/actions/variables/{var_name}'
        response = self.call_endpoint(method='DELETE',endpoint=endpoint, headers=self.get_header())
        content = self.get_content_response(response)
        return content
    
    def delete_repo_secret(self,secret_name:str,owner:str,repo:str) -> json:
        endpoint = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}'
        response = self.call_endpoint(method='DELETE',endpoint=endpoint, headers=self.get_header())
        content = self.get_content_response(response)
        return content
    
if __name__=='__main__':
    confs = get_global_confs(file_path=Path(__file__).parent.parent.parent.joinpath('setup/confs.json').as_posix())
    git = GithubApi(token=confs['github_api_token']['value'])
    print(git.update_and_insert_repo_variable(var_name='test',var_value='test',owner=confs['github_user']['value'],repo=confs['github_repository']['value']))
