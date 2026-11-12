# VM de monitoramento: Prometheus + Grafana
# Usa a mesma pasta de discos (pool), a mesma imagem Ubuntu e o mesmo
# cloud_init.cfg da VM do gerador. So muda o nome.

# Disco da VM de monitoramento, criado a partir da mesma imagem base
resource "libvirt_volume" "disco_monitor" {
  name           = "${var.mon_nome}-disco.qcow2"
  pool           = libvirt_pool.telhas.name
  base_volume_id = libvirt_volume.base.id
  format         = "qcow2"
  size           = var.mon_disco_gb * 1024 * 1024 * 1024
}

# Disco do cloud-init da VM de monitoramento
resource "libvirt_cloudinit_disk" "init_monitor" {
  name = "${var.mon_nome}-cloudinit.iso"
  pool = libvirt_pool.telhas.name

  user_data = templatefile("${path.module}/cloud_init.cfg", {
    hostname      = var.mon_nome
    usuario       = var.usuario_vm
    chave_publica = trimspace(file(pathexpand(var.chave_publica)))
  })

  meta_data = <<-EOT
    instance-id: ${var.mon_nome}
    local-hostname: ${var.mon_nome}
  EOT
}

# Maquina virtual de monitoramento
resource "libvirt_domain" "monitor" {
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

  name      = var.mon_nome
  memory    = var.mon_memoria_mb
  vcpu      = var.mon_vcpus
  running   = true
  cloudinit = libvirt_cloudinit_disk.init_monitor.id

  cpu {
    mode = "host-passthrough"
  }

  disk {
    volume_id = libvirt_volume.disco_monitor.id
  }

  # Mesma rede da VM do gerador, assim uma enxerga a outra
  network_interface {
    network_name   = "default"
    wait_for_lease = true
  }

  console {
    type        = "pty"
    target_port = "0"
    target_type = "serial"
  }

  console {
    type        = "pty"
    target_port = "1"
    target_type = "virtio"
  }

  graphics {
    type        = "spice"
    listen_type = "address"
    autoport    = true
  }
}

output "ip_do_monitor" {
  description = "Endereco IP da VM de monitoramento (Grafana na porta 3000)"
  value       = try(libvirt_domain.monitor.network_interface[0].addresses[0], "")
}
