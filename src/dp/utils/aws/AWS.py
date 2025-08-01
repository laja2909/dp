import json

import boto3
import botocore
from botocore.exceptions import ClientError
from pathlib import Path

from dp.utils.helper import get_global_confs 

class AWS:
    def __init__(self, aws_access_key:str, aws_secret_access_key:str):
        self._aws_access_key = aws_access_key
        self._aws_secret_access_key = aws_secret_access_key

    def get_aws_access_key(self):
        return self._aws_access_key
    
    def get_aws_secrect_access_key(self):
        return self._aws_secret_access_key
    
    def start_session(self):
        session = boto3.Session(aws_access_key_id=self.get_aws_access_key(),
                                aws_secret_access_key=self.get_aws_secrect_access_key())
        return session
    
    #LOAD
    def load_file_to_s3(self,data,bucket:str,key_path:str):
        session = self.start_session()
        s3 = session.resource('s3')
        object = s3.Object(bucket,key_path)
        result = object.put(Body = data)

    def load_file_from_s3(self,bucket,key_path:str):
        session = self.start_session()
        s3 = session.resource('s3')
        object = s3.Object(bucket,key_path)
        object_body = object.get()['Body'].read().decode('utf-8')
        data = self.convert_object_to_format(object_body)
        return data
    
    #BOOL
    def has_bucket(self,bucket_name:str)->bool:
        session = self.start_session()
        s3 = session.resource('s3')
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                return False
            elif error_code == 403:
                # Bucket exists but access denied
                return True
            else:
                raise
        
    #UTILS
    def convert_object_to_format(object, to_format:str='json'):
        if to_format=='json':
            data = json.loads(object)
        else:
            raise 'unknown format'
        return data
    
if __name__=='__main__':
    confs = get_global_confs(file_path=Path(__file__).parent.parent.parent.joinpath('setup/confs.json').as_posix())
    aws_api = AWS(aws_access_key=confs['aws_access_key']['value'], aws_secret_access_key=confs['aws_secret_access_key']['value'])
    print(aws_api.has_bucket(bucket_name='sewasd'))
    