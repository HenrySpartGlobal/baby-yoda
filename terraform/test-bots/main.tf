module "vultr-instances" {
  source = "git::https://github.com/HenrySpartGlobal/vultr-deployment.git//modules/vultr-instance"

  plan = "vc2-1c-1gb"
  region = "lhr"
  # Ubuntu 22.04 LTS x64
  os_id = 1743
  label = "Baby Yoda Bot"
  tags = ["baby-yoda", "Test", "Version: 0.0.1"]
  hostname = "baby-yoda-bot"
  api_key = var.api_key
}

output "main_ip" {
  value = module.vultr-instances.testing
}

resource "vultr_ssh_key" "ssh-key" {
  name    = "ssh-key"
  ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC3K5HBsqtLMLIqwSnC2pkjKm4mJhR+kQT6TlOX20BFtNz1UkKrJkFukvq+voW3FJF6nnXYiK6ZXKW0WKliudq2gS+JkBieajbIoAJoF+aPYXVA0z3ORSu5gmYdVXxmDni0Pzu3NQbqvfrpCVtf2JERKvReipBOsWMt2nDpQodBbC/Hz5wtDjmbhHd5AbUfGq+mI2xxXTypEwldH3VAcHHv3RBJTI1XiF7WGGHOUWI/4KrvrQus8QedTmxgo0LrrOpsIh54jAHKTHhsxLw5Ww6d8yqKhRiW/i+Qg8f+WZ4ONd/94Arx4mbOdHngGoS4wsG349WEYJRq3o7Zy5q5Y6RtVmbavsFA3vK03uCxQNBBjfbR7q190uBLr2Pd/Yc4eaAAncBmX+JGpdq9V7STLgAp9bp7c6TysIGjrk2eVj9zvbaWuf0sU92VfxmoIpvp90pho0V7kD8Njda2MHV0WHfGHFhtnHN2zYK7w0iE/dJI/5scwc5hQbepaA6Z4gchIDs= Henry.koleoso@kensalfss-MacBook-Pro.local"
}