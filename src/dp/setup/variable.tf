
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

