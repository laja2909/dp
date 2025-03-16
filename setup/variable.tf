
#hetzner
variable "ssh_public_name" {
    description = "name of the generated ssh key public file"
    type = string
    default = "hetz.pub"
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