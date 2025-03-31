confs = {
    'terraform':{
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
    },
    'github':{
        'user':{
            'type':'LOCAL_ENV',
            'name':'GH_USER_NAME',
            'description':'local environment variable to store github user name'
        },
        'repository':{
            'type':'LOCAL_ENV',
            'name':'GH_REPOSITORY_NAME',
            'description':'local environment variable to store github repository name'
        }
    },
    'hetzner':{
        'api_token':{
            'type':'LOCAL_ENV',
            'name':'HETZ_TOKEN',
            'description':'local environment variable to store hetzner api key'
        }
    },
    'local':{
        'ssh_path':{
            'type':'LOCAL_ENV',
            'name':'SSH_PATH',
            'description':'local environment variable to store default path of ssh keys'
        }
    }
}