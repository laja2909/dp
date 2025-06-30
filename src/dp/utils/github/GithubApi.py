import requests
import json

from base64 import b64encode
from nacl import encoding, public

from dp.utils.confs import confs
from dp.utils.helper import get_env_variable



class GithubApi:
    """
    Class to help with Github API calls
    
    """
    def __init__(self,token_name:str=confs['github']['api_token']['name']):
        token = get_env_variable(token_name)
        self._header = {'Authorization': f'token {token}',
                        'Accept': 'application/vnd.github+json'}
    
    def get_header(self):
        return self._header
    
    def create_repo_variable(self,var_name:str, var_value:str,
                             owner:str=get_env_variable(confs['github']['user']['name']),
                             repo:str=get_env_variable(confs['github']['repository']['name'])) -> None:
        end_point = f'https://api.github.com/repos/{owner}/{repo}/actions/variables'

        payload = {'name':var_name, 'value':var_value}
        response = self.call_api('POST',end_point=end_point, payload=payload)
        content = self.get_content_response(response)
        return content
    
    def encrypt(self, public_key:str, secret_value:str) -> str:
        """Encrypt a Unicode string using the public key."""
        public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return b64encode(encrypted).decode("utf-8")


    def create_repo_secret(self,secret_name:str, secret_value:str,
                             owner:str=get_env_variable(confs['github']['user']['name']),
                             repo:str=get_env_variable(confs['github']['repository']['name'])) -> None:
        
        #get public key
        end_point_public_key = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key'
        response = self.call_api('GET',end_point=end_point_public_key)
        content = self.get_content_response(response)
        public_key = content["key"]
        key_id = content["key_id"]

        #encrypt the secret
        encrypted_secret = self.encrypt(public_key,secret_value)

        #upload secret
        end_point_secret_url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}"
        payload = {
             "encrypted_value": encrypted_secret,
             "key_id": key_id}
        response = self.call_api('PUT',end_point=end_point_secret_url, payload=payload)
        content = self.get_content_response(response)

        return content


    def get_repo_secrets(self,owner:str=get_env_variable(confs['github']['user']['name']),
                         repo:str=get_env_variable(confs['github']['repository']['name'])) -> json:

        end_point = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets'
        response = self.call_api('GET',end_point=end_point)
        content = self.get_content_response(response)
        return content
    
    def get_repo_variables(self,owner:str=get_env_variable(confs['github']['user']['name']),
                         repo:str=get_env_variable(confs['github']['repository']['name'])):

        end_point = f'https://api.github.com/repos/{owner}/{repo}/actions/variables'
        response = self.call_api('GET',end_point=end_point)
        content = self.get_content_response(response)
        return content

    ##UTIL
    def call_api(self,method,end_point,payload:json=None) -> requests.Response:
        if payload!=None:
            print(f'Calling: {end_point}')
            response = requests.request(method, end_point, headers=self.get_header(),data=json.dumps(payload))
        else:
            print(f'Calling: {end_point}')
            response = requests.request(method, end_point, headers=self.get_header())
        return response
    
    def get_content_response(self,response:requests.Response) -> json:
        """
        Response is always in json object
        
        """
        try:
            content = response.json()
            print("retrieved the response..")
        except json.JSONDecodeError as e:
            raise Exception('No response: ', e)
        return content
    
if __name__=='__main__':
    git = GithubApi()
    git.create_repo_secret(secret_name='test',secret_value='testvalue')