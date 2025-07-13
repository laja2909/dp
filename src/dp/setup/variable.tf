
#hetzner
variable "hetzner_api_token" {
    description = "api token"
    type = string
    sensitive = true
}

variable "local_ip" {
    description = "your local ip4 address"
    type = string
    sensitive = false
}

variable "hetzner_main_server_name" {
    description = ""
    type = string
    sensitive = false
}
variable "hetzner_main_server_location" {
    description = ""
    type = string
    sensitive = false
}
variable "hetzner_main_server_image" {
    description = ""
    type = string
    sensitive = false
}
variable "hetzner_main_server_type" {
    description = ""
    type = string
    sensitive = false
}

variable "hetzner_ssh_key_name" {
    description = ""
    type = string
    sensitive = false
}
variable "hetzner_firewall_name" {
    description = ""
    type = string
    sensitive = false
}
variable "hetzner_firewall_ssh_port" {
    description = ""
    type = string
    sensitive = false
}
variable "hetzner_firewall_airflow_port" {
    description = ""
    type = string
    sensitive = false
}

#aws
variable "aws_region" {
    description = ""
    type = string
    sensitive = false
}

variable "aws_access_key" {
    description = ""
    type = string
    sensitive = true
}

variable "aws_secret_access_key" {
    description = ""
    type = string
    sensitive = true
}

variable "aws_s3_bucket_name" {
    description = ""
    type = string
    sensitive = false
}

