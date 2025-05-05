
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

variable "server_location" {
    description = "location of the server"
    type = string
    default = "hel1"
}

variable "server_image" {
    description = "image of the server"
    type = string
    default = "ubuntu-24.04"
}

variable "server_type" {
    description = "type of the server"
    type = string
    default = "cx32"
}

variable "server_name" {
    description = "name of the server"
    type = string
    default = "main_server"
}

