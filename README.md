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

**Note! This setup is not free, you are charged based on services above.**
Initial setup costs you roughly 27€ / month:
- 8€ / month to run server in hetzner, 19€ / month for DigitalOcean database. (AWS s3 is free if you not have much data there)

## Prerequisites
1. Fork the repository
2. Install Python (if not having it already)
3. Create Python virtual environment, instructions [here](docs/create_venv.md)
4. install repo in editable state, to get import references worrk, instruction [here](docs/init_project.md)
5. [Terraform docs](docs/systems/init_terraform.md)
6. [hetzner docs](docs/systems//hetzner/init_hetzner.md)
7. [DigitalOcean docs](docs/systems/init_digital_ocean.md)
8. [AWS docs](docs/systems/init_aws.md)


## Set up
Now you should have:
1. terraform installed and terraform cloud set up
- add "hcloud_token" as your variable in terraform cloud
- add your local ip4 address as "local_ip" variable in terraform cloud
2. hetzner account created & project initialised & token created
3. DigitalOcean account created
4. AWS account created and user with s3 access and aws cli
5. Python installed

Next:
- Install Airflow to hetzner server, instructions [here](docs/systems/hetzner/init_airflow.md)
