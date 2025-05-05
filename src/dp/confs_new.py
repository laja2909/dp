terraform_vars ={
        'api_token':{
            'type':'LOCAL_ENV',
            'name':'TF_TOKEN',
            'description':'local environment variable to store terraform api token'
        },
        'email':{
            'type':'LOCAL_ENV',
            'name':'TF_EMAIL',
            'description':'local environment variable to store terraform organization email'
        },
        'organization':{
            'type':'RAW',
            'name':'dp-data-platform',
            'description':'name of default organization name for the project'
        },
        'workspace':{
            'type':'RAW',
            'name':'dp',
            'description':'name of default workspace name for the project'
        }
}

github_vars = {
        'api_token':{
            'type':'LOCAL_ENV',
            'name':'GH_TOKEN',
            'description':'local environment variable to store github personal access token'
        },
        'user':{
            'type':'LOCAL_ENV',
            'name':'GH_USER_NAME',
            'description':'local environment variable to store github user name'
        },
        'repository':{
            'type':'LOCAL_ENV',
            'name':'GH_REPOSITORY_NAME',
            'description':'local environment variable to store github repository name'
        },
        'tc_client_id':{
            'type':'LOCAL_ENV',
            'name':'GH_TC_CLIENT_ID',
            'description':'local environment variable to store github OAuth client id for terraform cloud'
        },
        'tc_client_token':{
            'type':'LOCAL_ENV',
            'name':'GH_TC_CLIENT_TOKEN',
            'description':'local environment variable to store github OAuth client token for terraform cloud'
        }
}

hetzner_vars = {
        'api_token':{
            'type':'LOCAL_ENV',
            'name':'HETZ_TOKEN',
            'description':'local environment variable to store hetzner api key'
        }
}

local_vars = {
        'ssh_path':{
            'type':'LOCAL_ENV',
            'name':'SSH_PATH',
            'description':'local environment variable to store default path of ssh keys'
        },
        'ssh_key_name':{
            'type':'RAW',
            'name':'id_hetzner',
            'description':'defines the name of your local ssh key'
        }
}

remote_vars = {
        'user':{
            'type':'LOCAL_ENV',
            'name':'REMOTE_USER',
            'description': 'default user in the remote server, by default its root'
        }

}