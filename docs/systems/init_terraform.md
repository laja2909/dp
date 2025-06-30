## Steps to install terraform

### windows
- go to: https://developer.hashicorp.com/terraform/install

- download latest version

- add path of your downloaded application to the PATH system environment variable

- verify that terraform works by running in terminal:
```
terraform --version
```
It should output the version you installed. If not, close terminal, then try again. Might require you to restart computer

## Steps to configure terraform cloud
- Use terraform cloud to save your infrastracture state and to store sensitive variables there
- go to: https://app.terraform.io/
- create account
- create api token
    - save api token as "TF_TOKEN" environment variable
