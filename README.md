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
2. Create Python virtual environment, instructions [here](docs/create_venv.md)
2. Create toml file, instruction [here](docs/create_toml.md)
2. [Terraform docs](docs/systems/init_terraform.md)
3. [hetzner docs](docs/systems/init_hetzner.md)
4. [DigitalOcean docs](docs/systems/init_digital_ocean.md)
5. [AWS docs](docs/systems/init_aws.md)
6. Python installed

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
- run te





-create python virtual environment and load requirements.txt (see docs/create_venv.md)

