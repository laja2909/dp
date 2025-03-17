# DHub
Data platform project

To define and run data pipelines with following tools:
1. hetzner cloud server:
- airflow to orchestrate dataflows
2. DigitalOcean managed postgres database:
- data storage
3. AWS s3:
- raw data storage
- logging

**Note! This setup is not free, you are charged based on services above.**
Initial setup costs you roughly 27€ / month:
- 8€ / month to run server in hetzner, 19€ / month for DigitalOcean database. (AWS s3 is free if you not have much data there)

## Prerequisites
1. Terraform (docs/init_terraform.md)
2. hetzner cloud account & project (docs/init_hetzner.md)
3. DigitalOcean account (docs/init_digital_ocean.md)
4. AWS account (docs/init_aws.md)
5. Python

## Set up
Now you should have:
1. terraform installed and terraform cloud set up
- add hcloud_token as your variable in terraform cloud
- add your local ip4 address as "local_ip" variable in terraform cloud
2. hetzner account created & project initialised & token created
3. DigitalOcean account created
4. AWS account created and user with s3 access and aws cli
5. Python installed

Next:
-merge branch to main branch and terraform cloud should trigger a run which initialises all resources defined in main.tf file:
    - server in hetzner cloud
    - digitalocean managed database
    - aws s3 bucket
-create python virtual environment and load requirements.txt (see docs/create_venv.md)

