variable "vm_nome" {
  description = "Nome da máquina virtual"
  type        = string
  default     = "telhas-vm"
}

variable "vm_vcpus" {
  description = "Quantidade de CPUs da VM"
  type        = number
  default     = 2
}

variable "vm_memoria_mb" {
  description = "Memória da VM em MB"
  type        = number
  default     = 2048
}

variable "disco_gb" {
  description = "Tamanho do disco da VM em GB"
  type        = number
  default     = 10
}

variable "usuario_vm" {
  description = "Usuário criado dentro da VM pelo cloud-init"
  type        = string
  default     = "aluno"
}

variable "chave_publica" {
  description = "Caminho da chave pública SSH que será autorizada na VM"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "imagem_url" {
  description = "Imagem cloud do Ubuntu usada como base da VM"
  type        = string
  default     = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"
}
