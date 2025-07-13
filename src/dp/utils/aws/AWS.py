import json

import boto3
import botocore

class AWS:
    def __init__(self):
        pass
    
    def start_session(self, aws_access_key:str, aws_secret_access_key:str):
        session = boto3.Session(aws_access_key_id=aws_access_key,
                                aws_secret_access_key=aws_secret_access_key)
        return session
    
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
        data = self.convert_object_to_data(object_body)
        return data
    
    def convert_object_to_format(object, to_format:str='json'):
        if to_format=='json':
            data = json.loads(object)
        else:
            raise 'unknown format'
        return data
    
if __name__=='__main__':
    aws = AWS()
    