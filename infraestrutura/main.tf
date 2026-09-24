terraform {
  required_version = ">= 1.6.0"

  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "0.8.3"
    }
  }
}

provider "libvirt" {
  uri = "qemu:///system"
}

# Pasta onde ficam os discos da VM
resource "libvirt_pool" "telhas" {
  name = "telhas_pool"
  type = "dir"

  target {
    path = "/var/lib/libvirt/images/telhas"
  }
}

# Imagem base (Ubuntu cloud image), baixada da internet
resource "libvirt_volume" "base" {
  name   = "ubuntu-noble-base.qcow2"
  pool   = libvirt_pool.telhas.name
  source = var.imagem_url
  format = "qcow2"
}

# Disco da VM, criado a partir da imagem base
resource "libvirt_volume" "disco" {
  name           = "${var.vm_nome}-disco.qcow2"
  pool           = libvirt_pool.telhas.name
  base_volume_id = libvirt_volume.base.id
  format         = "qcow2"
  size           = var.disco_gb * 1024 * 1024 * 1024
}

# Disco do cloud-init
resource "libvirt_cloudinit_disk" "init" {
  name = "${var.vm_nome}-cloudinit.iso"
  pool = libvirt_pool.telhas.name

  user_data = templatefile("${path.module}/cloud_init.cfg", {
    hostname      = var.vm_nome
    usuario       = var.usuario_vm
    chave_publica = trimspace(file(pathexpand(var.chave_publica)))
  })

  meta_data = <<-EOT
    instance-id: ${var.vm_nome}
    local-hostname: ${var.vm_nome}
  EOT
}

# Máquina virtual
resource "libvirt_domain" "vm" {
  lifecycle {
    ignore_changes = [
      cloudinit,
      type,
      graphics,
      console,
      nvram,
      fw_cfg_name
    ]
  }

  name      = var.vm_nome
  memory    = var.vm_memoria_mb
  vcpu      = var.vm_vcpus
  running   = true
  cloudinit = libvirt_cloudinit_disk.init.id

  cpu {
    mode = "host-passthrough"
  }

  disk {
    volume_id = libvirt_volume.disco.id
  }

  network_interface {
    network_name   = "default"
    wait_for_lease = false
  }

  # Console serial
  console {
    type        = "pty"
    target_port = "0"
    target_type = "serial"
  }

  # Console virtio
  console {
    type        = "pty"
    target_port = "1"
    target_type = "virtio"
  }

  # Interface gráfica SPICE
  graphics {
    type        = "spice"
    listen_type = "address"
    autoport    = true
  }
}

output "ip_da_vm" {
  description = "Endereço IP da VM (usar no inventário do Ansible e no SSH)"
  value       = try(libvirt_domain.vm.network_interface[0].addresses[0], "")
}
