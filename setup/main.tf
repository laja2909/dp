
# hetzner setup

resource "hcloud_ssh_key" "main" {
  name       = var.ssh_public_name
  public_key = var.ssh_path
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

resource "hcloud_server" "dhub" {
  name         = "dhub"
  location     = var.server_location
  image        = var.server_image
  server_type  = var.server_type
  ssh_keys     = [hcloud_ssh_key.main.]
  firewall_ids = [hcloud_firewall.myfirewall.id]
}
