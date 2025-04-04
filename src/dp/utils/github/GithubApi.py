import time
import jwt

class GithubApi:
    def __init__():
        pass
    
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