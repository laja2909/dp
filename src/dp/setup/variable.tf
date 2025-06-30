
#hetzner
variable "hcloud_token" {
    description = "api token"
    type = string
    sensitive = true
}

variable "local_ip" {
    description = "your local ip4 address"
    type = string
    sensitive = false
}

variable "hetzner_main_server_name" {}
variable "hetzner_main_server_location" {}
variable "hetzner_main_server_image" {}
variable "hetzner_main_server_type" {}

variable "hetzner_ssh_key_name" {}
variable "hetzner_firewall_name" {}
variable "hetzner_firewall_ssh_port" {}
variable "hetzner_firewall_airflow_port" {}