# dp
Data platform project

To define and run data pipelines with following tools:
1. hetzner cloud server:
- airflow to orchestrate dataflows
2. DigitalOcean managed postgres database:
- data storage
3. AWS s3:
- raw data storage
- logging
4. Terraform & Terraform cloud
- to set up infrastacture

**Note! This setup is not free, you are charged based on services above.**
Initial setup costs you roughly 27€ / month:
- 8€ / month to run server in hetzner, 19€ / month for DigitalOcean database. (AWS s3 is free if you not have much data there)

## Prerequisites
1. Fork the repository
    - create new branch from the main
    - checkout to new branch
2. Install Python (if not having it already)
3. Create Python virtual environment, instructions [here](docs/create_venv.md)
4. install repo in editable state, to get import references work, instruction [here](docs/init_project.md)
5. [init Terraform](docs/systems/init_terraform.md)
6. [init hetzner](docs/systems//hetzner/init_hetzner.md)
7. [init DigitalOcean](docs/systems/init_digital_ocean.md)
8. [init AWS](docs/systems/init_aws.md)

## Folder structure
.github = folder to keep github workflow files
docs = folder to keep all documentations of the project
setup = only used when initialising the resources and maybe destroying them
src = all datapipelines and db migrations there and dependencies related to them (more detailed in the docs)


## Set up
### Status
1. terraform installed and terraform cloud set up
2. hetzner account created & project initialised & token created (cloud server)
3. DigitalOcean account created (maybe not??)
4. AWS account created and user with s3 access and aws cli

### Steps

- go to confs file and check that you have added necessary local environment variables, you can change the "RAW" types the name that you like
- run initialise.py from setup folder (Note! After this you resources are running and they are billable):
---creates terraform organization and workspace with needed variables
---run terraform resources
---copies ssh keys to local
---create project folder
---clone repo in hetzner
---create ssh keys there

#### config remote ssh access
- once remote server is created, copy the ssh keys from remote server to your local computer [here](docs/systems/hetzner/remote_connection_hetzner.md)

- edit ssh config file and connect to server

#### set up github sync
- Everytime we push changes to main branch, we want to remote server be in sync with the latest changes
- remote access to hetzner server, and go to root users home directory (/root)
- create projects directory
```mkdir projects```
```cd projects```
- clone repository
```git clone <https path>```
- create SSH key
```ssh-keygen -t rsa -b 4096```
- add public key to authorized_keys file
```cat <path/to/public/key> >> ~/.ssh/authorized_keys```
- copy content of private key
```cat <path/to/private/key>```
- go to github repo
    - settings > secrets > actions
- create the following repository secrets
----HETZ_SERVER_NAME
----HETZ_TOKEN
----MAIN_BRANCH
----SSH_HOST
----SSH_PRIVATE_KEY
----SSH_USER
----WORK_DIR







Next:
- Install Airflow to hetzner server, instructions [here](docs/systems/hetzner/init_airflow.md)
