import time
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

import requests

from dp.utils.confs import confs
from dp.utils.helper import get_env_variable

class GithubApi:
    def __init__(self,token_name:str=confs['github']['api_token']['name'],
                 user_name:str=confs['github']['user']['name'],
                 repository:str=confs['github']['repository']['name']):
        
        token = get_env_variable(token_name)
        self._user_name=get_env_variable(user_name)
        self._repository=get_env_variable(repository)

        self._headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
        }


    def get_headers(self):
        return self._headers
    
    def get_user(self):
        return self._user_name
    
    def get_repository(self):
        return self._repository

    def create_private_key(self, key_name):
        """Generate a new RSA private key for the GitHub App"""
        # Generate a private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
    
        # Serialize the private key to PEM format
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    
        # Save the key to a file
        with open(key_name, "wb") as f:
            f.write(pem)
    
        return pem.decode('utf-8')
    
    def create_jwt_token_from_local_key(self, file_name, app_id):
        with open(file_name, 'r') as key_file:
            private_key = key_file.read()
    
        now = int(time.time())
        payload = {
            'iat': now,
            'exp': now + (10 * 60),  # JWT expires in 10 minutes
            'iss': app_id
            }
    
        token = jwt.encode(payload, private_key, algorithm='RS256')
        return token

