import requests
import json

class API:
    def __init__(self):
        pass

    def call_endpoint(self,method,endpoint,headers:str,payload:json=None) -> requests.Response:
        if payload!=None:
            print(f'Calling: {endpoint}')
            response = requests.request(method, endpoint, headers=headers,data=json.dumps(payload))
        else:
            print(f'Calling: {endpoint}')
            response = requests.request(method, endpoint, headers=headers)
        if response.status_code>=400:
            print(f'Error in the call:\n{response.json()}')
        else:
            print('call successful')
        return response
    
    def get_content_response(self,response:requests.Response) -> json:
        """
        
        """
        if response.status_code>=400:
            raise Exception('No content to retrieve due to error in the call')
        if response.status_code==204:
            print('Response content empty')
            content={}
        else:
            try:
                content = response.json()
            except json.JSONDecodeError as e:
                raise Exception('Cannot convert response content to json: ', e)
        return content