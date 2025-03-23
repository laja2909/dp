
# hetzner setup

terraform {
  required_providers {
    hcloud = {
      source = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }
}

provider "hcloud" {
  token = var.hcloud_token
}

resource "tls_private_key" "generic-ssh-key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}


resource "hcloud_ssh_key" "main" {
  name       = "primary-ssh-key"
  public_key = tls_private_key.generic-ssh-key.public_key_openssh
}

resource "hcloud_firewall" "myfirewall" {
  name = "my-firewall"
  rule {
    direction = "in"
    protocol  = "tcp"
    port = "22"
    source_ips = [
      var.local_ip
    ]
  }

  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "8080"
    source_ips = [
      var.local_ip
    ]
  }

}

resource "hcloud_server" "dp" {
  name         = "dp"
  location     = var.server_location
  image        = var.server_image
  server_type  = var.server_type
  ssh_keys     = [hcloud_ssh_key.main.name]
  firewall_ids = [hcloud_firewall.myfirewall.id]
  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }
}
