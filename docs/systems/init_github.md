## Initialise github environment for the project

- You have github account created
- Fork the repository
- create personal access token
- create github oauth application for terraform (this will allow us to use vcs provider flow in the terraform cloud)
    - in github go to settings -> applications -> new OAuth application:
        - specs: {"Application name":"Terraform Cloud",
                  "Homepage URL":"https://app.terraform.io",
                  "Authorization callback URL":"https://app.terraform.io/auth/oauth/callback" }
    - save the "Client ID" as "GH_TC_CLIENT_ID" environment variable
    - generate Client secret
    - save the "Client secret" as "GH_TC_CLIENT_TOKEN" environment variable
    - update the application
- Create feature branch
- Checkout to the feature branch locally