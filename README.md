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
1. terraform installed
2. hetzner account created & project initialised
3. DigitalOcean account created
4. AWS account created and user with s3 access and aws cli
5. Python installed

Next:
- terraform configuration files are in setup folder
- save all sensitive variables into environment variables:
    - TF_VAR_ssh_path = ```path to your ssh file```
    - TF_VAR_local_ip = ```your local ip4 address```
    - 


