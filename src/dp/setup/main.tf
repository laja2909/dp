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
  name       = var.hetzner_ssh_key_name
  public_key = tls_private_key.generic-ssh-key.public_key_openssh
}

resource "hcloud_firewall" "dp-firewall" {
  name = var.hetzner_firewall_name
  rule {
    direction = "in"
    protocol  = "tcp"
    port = var.hetzner_firewall_ssh_port
    source_ips = [
      var.local_ip
    ]
  }

  rule {
    direction = "in"
    protocol  = "tcp"
    port      = var.hetzner_firewall_airflow_port
    source_ips = [
      var.local_ip
    ]
  }

}

resource "hcloud_server" "main_server" {
  name         = var.hetzner_main_server_name
  location     = var.hetzner_main_server_location
  image        = var.hetzner_main_server_image
  server_type  = var.hetzner_main_server_type
  ssh_keys     = [hcloud_ssh_key.main.name]
  firewall_ids = [hcloud_firewall.dp-firewall.id]
  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }
}
