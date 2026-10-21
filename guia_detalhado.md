# Projeto Integrado – Fábrica de Telhas

Checkpoint 01 – DevOps e Infraestrutura Privada
Guia detalhado: criar uma VM por código e rodar o simulador de dados dentro dela

| Projeto | Projeto Integrado – Data Science (fábrica de telhas de barro: controle da queima de lenha nos fornos) |
| --- | --- |
| Equipe | Julia Docema de Carvalho e Julia Fernandes de Ovidio |
| Repositório | https://github.com/judocema/telhas-pipeline |
| Entrega | 30/09/2026 (link do repositório no Classroom) |


# 1. O que este guia faz
Este guia mostra, passo a passo, como criar uma máquina virtual (VM) usando código, configurá-la automaticamente e rodar dentro dela o simulador de dados do projeto.
O caminho completo é este:
O OpenTofu cria a VM no computador Linux (a máquina hospedeira).
O cloud-init faz a configuração inicial da VM: usuário, chave SSH, nome e fuso horário.
O Ansible instala o Python e cria as pastas que o simulador precisa.
O SSH/SCP envia o simulador da máquina hospedeira para a VM.
O simulador roda dentro da VM e guarda os arquivos CSV lá mesmo.
Todo o código fica no GitHub, na pasta infraestrutura/ (infraestrutura) e simulador/ (aplicação).

Sobre o simulador: é o mesmo gerador.py que já usamos na automação do projeto, com uma única mudança: a pasta de saída dos CSVs agora é relativa à pasta do simulador, para ele funcionar em qualquer máquina (o professor pediu que a aplicação não dependa de caminhos que só existem no computador hospedeiro). O vigia.sh e o processar.py ficam para as próximas etapas do Projeto Integrado.
# 2. Ferramentas usadas

| Ferramenta | Para que serve | Como conferir a versão |
| --- | --- | --- |
| Linux (Ubuntu ou Linux Mint) | Computador onde tudo é executado (máquina hospedeira) | cat /etc/os-release |
| libvirt + KVM/QEMU | Cria e executa máquinas virtuais no Linux | virsh --version |
| OpenTofu | Infraestrutura como código: cria a VM a partir de arquivos .tf | tofu version |
| Provider dmacvicar/libvirt 0.8.3 | Ensina o OpenTofu a conversar com o libvirt | tofu version (depois do tofu init) |
| Ubuntu 24.04 cloud image | Imagem pronta que serve de base para a VM | Dentro da VM: cat /etc/os-release |
| cloud-init | Configura a VM no primeiro boot | Dentro da VM: cloud-init status |
| Ansible | Instala programas e cria pastas na VM | ansible --version |
| SSH e SCP | Acesso remoto e cópia de arquivos para a VM | ssh -V |
| Git e GitHub | Versionamento do código | git --version |
| Python 3 | Linguagem do simulador | python3 --version |


Por que a versão 0.8.3 do provider? O provider do libvirt foi reescrito na versão 0.9, com uma sintaxe diferente. Fixamos a 0.8.3 no main.tf para o código funcionar sempre do mesmo jeito.
# 3. Estrutura do repositório
telhas-pipeline/
├── infraestrutura/
│   ├── main.tf              # OpenTofu: pool, discos, cloud-init e VM
│   ├── variables.tf         # variáveis (nome da VM, memória, chave SSH...)
│   ├── cloud_init.cfg       # configuração inicial da VM
│   └── ansible/
│       ├── inventory.ini    # como o Ansible acessa a VM
│       └── playbook.yml     # instala o Python e cria as pastas
├── simulador/
│   ├── simulador.py         # gerador de dados simulados
│   └── requirements.txt
├── dados/
│   └── exemplo_dados.csv    # exemplo de arquivo gerado pelo simulador
├── .gitignore
└── README.md
A pasta infraestrutura/ tem tudo que cria e configura a VM. A pasta simulador/ tem só a aplicação. A pasta dados/ guarda um exemplo dos dados gerados. Assim a infraestrutura e a aplicação ficam separadas.
# 4. Passo a passo
Faça os passos na ordem, no computador Linux que será a máquina hospedeira. A cada etapa que funcionou, faça o commit no Git (assim o histórico do repositório mostra o desenvolvimento).
## Passo 1 – Conferir o computador e instalar as ferramentas
### 1.1 Ver o sistema e se a virtualização está ligada
cat /etc/os-release
egrep -c '(vmx|svm)' /proc/cpuinfo
O primeiro comando mostra o sistema (Ubuntu ou Linux Mint). O segundo mostra um número: se for 1 ou mais, a virtualização está ativa. Se for 0, é preciso ligar a virtualização (Intel VT-x ou AMD-V) na BIOS do computador.
### 1.2 Instalar libvirt/KVM, Ansible, Git e curl
sudo apt update
sudo apt install -y qemu-system-x86 libvirt-daemon-system libvirt-clients ansible git curl
### 1.3 Dar permissão ao seu usuário
sudo usermod -aG libvirt,kvm $USER
Depois saia da sessão e entre de novo (ou reinicie o computador). Isso é necessário para o Linux reconhecer os novos grupos. Depois confira:
groups
virsh -c qemu:///system list --all
virsh -c qemu:///system net-list --all
Em groups deve aparecer libvirt.
Em net-list deve aparecer a rede default com estado active. Se estiver inactive, rode:
virsh -c qemu:///system net-start default
virsh -c qemu:///system net-autostart default
### 1.4 Instalar o OpenTofu
curl --proto '=https' --tlsv1.2 -fsSL \
https://get.opentofu.org/install-opentofu.sh -o install-opentofu.sh
chmod +x install-opentofu.sh
./install-opentofu.sh --install-method deb
rm -f install-opentofu.sh
tofu version
Deve aparecer a versão do OpenTofu (por exemplo, OpenTofu v1.x.x). O projeto usa a versão 1.6 ou mais nova.
## Passo 2 – Chave SSH e configuração do Git
### 2.1 Criar a chave SSH (se ainda não existir)
[ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "telhas-vm"
ls ~/.ssh
Devem aparecer id_ed25519 (chave privada, nunca vai para o GitHub) e id_ed25519.pub (chave pública, é ela que o cloud-init coloca na VM). Se a chave já existia, o comando não faz nada.
### 2.2 Configurar o Git
git config --global user.name "Julia Docema de Carvalho"
git config --global user.email "julia.docema@sou.unifeob.edu.br"
git config --global credential.helper 'cache --timeout=3600'
A última linha guarda o token do GitHub por 1 hora na memória, para não precisar digitar a cada git push.
### 2.3 Gerar o token do GitHub
O GitHub não aceita mais a senha da conta no git push. Gere um token: GitHub > Settings > Developer settings > Personal access tokens > gerar um token com a permissão repo. Guarde o token em local seguro e não coloque ele em nenhum arquivo do projeto.
## Passo 3 – Criar o repositório e as pastas
### 3.1 Criar o repositório no GitHub
Entre na conta judocema e clique em New repository.
Nome: telhas-pipeline. Deixe vazio (sem README e sem .gitignore).
Se ele for Private, adicione o professor e a Julia Fernandes em Settings > Collaborators. Como o repositório não tem senha nem chave, ele também pode ser Public.
### 3.2 Criar as pastas e iniciar o Git
mkdir -p ~/telhas-pipeline/infraestrutura/ansible
mkdir -p ~/telhas-pipeline/simulador
mkdir -p ~/telhas-pipeline/dados
cd ~/telhas-pipeline
git init
git branch -M main
### 3.3 Criar o .gitignore
Abra a pasta no VS Code com code ~/telhas-pipeline, crie o arquivo .gitignore na raiz e cole:
# OpenTofu: estado e cache locais (nunca publicar)
.terraform/
*.tfstate
*.tfstate.*
crash.log
*.tfvars

# Chaves e senhas (nunca publicar)
*.pem
*.key
id_ed25519
id_rsa

# Python
__pycache__/
*.pyc

# Ansible
*.retry

# Dados gerados pelo simulador (só o exemplo_dados.csv vai para o repositório)
dados/telhas_*.csv
Esse arquivo impede que subam para o GitHub o estado do OpenTofu, as chaves e os CSVs gerados (que ficam na VM). Repare que o .terraform.lock.hcl não está na lista: ele deve ser versionado.
### 3.4 Primeiro commit e primeiro push
git add .gitignore
git commit -m "Cria .gitignore do projeto"
git remote add origin https://github.com/judocema/telhas-pipeline.git
git push -u origin main
No git push, o usuário é judocema e a senha é o token do passo 2.3.
## Passo 4 – Colocar o simulador no projeto
cp ~/telhas/scripts/gerador.py ~/telhas-pipeline/simulador/simulador.py
Se o seu gerador.py estiver em outra pasta, ajuste o caminho do comando. Abra o simulador.py no VS Code, ache a linha que começa com PASTA_SAIDA = e troque só essa linha pelo bloco abaixo (o arquivo já tem import os no topo):
# Pasta de saída: por padrão é a pasta "dados", ao lado da pasta do simulador
# (na VM fica em /home/aluno/dados). Dá para trocar com a variável PASTA_SAIDA.
PASTA_SAIDA = os.environ.get(
'PASTA_SAIDA',
os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dados'))
)
Com isso o simulador grava sempre na pasta dados, ao lado da pasta simulador. Na VM, isso vira /home/aluno/dados. O resto do código continua igual: cada execução gera 12 registros de queima (um por forno) e de 0 a 4 compras de lenha, em arquivos novos com data e hora no nome.
Crie também o arquivo simulador/requirements.txt. O simulador só usa bibliotecas que já vêm com o Python, então o arquivo só tem comentários:
# O simulador usa só bibliotecas que já vêm com o Python 3 (csv, random, datetime, os).
# Não precisa instalar nada extra.
Faça o commit:
cd ~/telhas-pipeline
git add simulador
git commit -m "Adiciona simulador de dados da queima de lenha"
git push
## Passo 5 – Escrever os arquivos da infraestrutura
Crie estes 3 arquivos dentro de ~/telhas-pipeline/infraestrutura/. No VS Code: clique com o botão direito na pasta infraestrutura > New File.
### 5.1 variables.tf
Guarda os valores que podem mudar (nome da VM, CPUs, memória, disco, usuário, chave e imagem). Para mudar algo, altere o default.
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
### 5.2 main.tf
É o arquivo principal do OpenTofu. Ele descreve, em código, tudo que precisa existir:
libvirt_pool: a pasta onde ficam os discos da VM.
libvirt_volume "base": baixa a imagem Ubuntu 24.04 (cloud image).
libvirt_volume "disco": cria o disco da VM (10 GB) a partir da imagem base.
libvirt_cloudinit_disk: monta o disco do cloud-init com o arquivo cloud_init.cfg e coloca a chave pública nele.
libvirt_domain: a VM em si (2 CPUs, 2 GB de memória, rede default).
output "ip_da_vm": mostra o IP da VM no final.
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

# Disco do cloud-init (usa o arquivo cloud_init.cfg)
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

# A máquina virtual
resource "libvirt_domain" "vm" {
name   = var.vm_nome
memory = var.vm_memoria_mb
vcpu   = var.vm_vcpus

cloudinit = libvirt_cloudinit_disk.init.id

cpu {
mode = "host-passthrough"
}

disk {
volume_id = libvirt_volume.disco.id
}

network_interface {
network_name   = "default"
wait_for_lease = true
}

# Sem o console serial o Ubuntu pode travar na inicialização
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

output "ip_da_vm" {
description = "Endereço IP da VM (usar no inventário do Ansible e no SSH)"
value       = libvirt_domain.vm.network_interface[0].addresses[0]
}
### 5.3 cloud_init.cfg
É a configuração inicial da VM, aplicada automaticamente no primeiro boot. O arquivo precisa começar com #cloud-config. Os trechos ${hostname}, ${usuario} e ${chave_publica} são preenchidos pelo OpenTofu.
#cloud-config
hostname: ${hostname}
manage_etc_hosts: true
timezone: America/Sao_Paulo

users:
- name: ${usuario}
gecos: Usuario do projeto telhas
groups: [sudo]
shell: /bin/bash
sudo: ALL=(ALL) NOPASSWD:ALL
lock_passwd: true
ssh_authorized_keys:
- "${chave_publica}"

ssh_pwauth: false

write_files:
- path: /etc/cloud-init-telhas.txt
permissions: "0644"
content: |
VM criada com OpenTofu e configurada pelo cloud-init.
Projeto Integrado - Fabrica de telhas (controle de queima de lenha).

| Trecho | O que faz |
| --- | --- |
| hostname e manage_etc_hosts | Define o nome da VM (telhas-vm) |
| timezone | Coloca o fuso horário de São Paulo (as datas dos CSVs saem no nosso horário) |
| users | Cria o usuário aluno, com sudo sem senha e a chave pública autorizada |
| lock_passwd e ssh_pwauth | Bloqueiam o login por senha: só entra quem tem a chave SSH |
| write_files | Cria o arquivo /etc/cloud-init-telhas.txt, que serve de prova de que o cloud-init rodou |


## Passo 6 – Criar a VM com o OpenTofu
cd ~/telhas-pipeline/infraestrutura
tofu init
tofu plan
tofu apply
tofu init baixa o provider do libvirt e cria o arquivo .terraform.lock.hcl.
tofu plan mostra o que será criado. Deve terminar com Plan: 5 to add, 0 to change, 0 to destroy.
tofu apply cria de verdade. Digite yes quando pedir. Na primeira vez ele baixa a imagem (cerca de 600 MB), então pode demorar alguns minutos.
No final aparece Apply complete! Resources: 5 added e a saída ip_da_vm = "192.168.122.x".
Se aparecer o erro Permission denied ao criar a VM: é o AppArmor do Ubuntu bloqueando o disco criado pelo provider. Essa correção é conhecida para esse provider no Ubuntu. Rode:
sudo sed -i -E 's,#?(security_driver)\s*=.*,\1 = "none",g' /etc/libvirt/qemu.conf
sudo systemctl restart libvirtd
tofu apply
### Conferir que a VM foi criada por código
tofu state list
virsh -c qemu:///system list --all
ping -c 3 $(tofu output -raw ip_da_vm)
tofu state list lista os 5 recursos criados pelo OpenTofu.
virsh ... list --all deve mostrar telhas-vm com estado running.
ping mostra que a VM responde na rede.
Faça o commit (o .terraform.lock.hcl entra, mas o estado terraform.tfstate fica de fora por causa do .gitignore):
cd ~/telhas-pipeline
git add infraestrutura/main.tf infraestrutura/variables.tf infraestrutura/.terraform.lock.hcl
git commit -m "Adiciona OpenTofu para provisionar a VM"
git push
## Passo 7 – Conferir o cloud-init
Espere cerca de 1 minuto depois do tofu apply (o cloud-init ainda está terminando) e entre na VM por SSH:
IP=$(cd ~/telhas-pipeline/infraestrutura && tofu output -raw ip_da_vm)
ssh aluno@$IP
Na primeira vez o SSH pergunta se confia no servidor: digite yes. Se você entrou sem pedir senha, o cloud-init funcionou: ele criou o usuário aluno e autorizou a sua chave. Já dentro da VM, rode:
hostname
whoami
sudo whoami
timedatectl | grep "Time zone"
cat /etc/cloud-init-telhas.txt
cloud-init status
sudo sshd -T | grep -i passwordauthentication
exit

| Comando | O que deve aparecer (prova do cloud-init) |
| --- | --- |
| hostname | telhas-vm |
| whoami | aluno (usuário criado pelo cloud-init) |
| sudo whoami | root, sem pedir senha |
| timedatectl | grep "Time zone" | America/Sao_Paulo |
| cat /etc/cloud-init-telhas.txt | O texto definido em write_files |
| cloud-init status | status: done |
| sudo sshd -T | grep -i passwordauthentication | passwordauthentication no |


cd ~/telhas-pipeline
git add infraestrutura/cloud_init.cfg
git commit -m "Adiciona cloud-init: usuario, chave SSH, hostname e fuso horario"
git push
## Passo 8 – Preparar a VM com o Ansible
### 8.1 Criar o inventário e o playbook
Crie os arquivos dentro de ~/telhas-pipeline/infraestrutura/ansible/.
inventory.ini – diz ao Ansible como chegar na VM (IP, usuário e chave):
[simulador]
telhas-vm ansible_host=192.168.122.100

[simulador:vars]
ansible_user=aluno
ansible_ssh_private_key_file=~/.ssh/id_ed25519
ansible_python_interpreter=/usr/bin/python3
ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
O IP 192.168.122.100 é só um valor inicial: o próximo passo troca pelo IP real. A opção StrictHostKeyChecking=no evita erro quando a VM é recriada e muda a identificação dela (só usamos isso porque é um ambiente de laboratório).
playbook.yml – as tarefas que preparam o ambiente:
---
- name: Preparar a VM para rodar o simulador de dados
hosts: simulador
become: true

vars:
usuario: aluno
pasta_app: /home/aluno/simulador
pasta_dados: /home/aluno/dados

tasks:
- name: Esperar o cloud-init terminar
ansible.builtin.command: cloud-init status --wait
changed_when: false
failed_when: false

- name: Instalar Python 3 e pip
ansible.builtin.apt:
name:
- python3
- python3-pip
state: present
update_cache: true
cache_valid_time: 3600

- name: Criar a pasta da aplicação
ansible.builtin.file:
path: "{{ pasta_app }}"
state: directory
owner: "{{ usuario }}"
group: "{{ usuario }}"
mode: "0755"

- name: Criar a pasta dos dados gerados
ansible.builtin.file:
path: "{{ pasta_dados }}"
state: directory
owner: "{{ usuario }}"
group: "{{ usuario }}"
mode: "0755"

| Tarefa | O que faz |
| --- | --- |
| Esperar o cloud-init terminar | Evita que o Ansible mexa no apt enquanto o cloud-init ainda está rodando |
| Instalar Python 3 e pip | Instala os pacotes que o simulador precisa |
| Criar a pasta da aplicação | Cria /home/aluno/simulador (onde o simulador será copiado) |
| Criar a pasta dos dados gerados | Cria /home/aluno/dados (onde os CSVs serão gravados) |


O playbook pode ser rodado várias vezes sem erro: o Ansible só muda o que ainda não está como deveria (isso se chama idempotência).
### 8.2 Colocar o IP atual no inventário
cd ~/telhas-pipeline/infraestrutura
sed -i "s/ansible_host=[0-9.]*/ansible_host=$(tofu output -raw ip_da_vm)/" ansible/inventory.ini
grep ansible_host ansible/inventory.ini
### 8.3 Testar a conexão e rodar o playbook
cd ansible
ansible -i inventory.ini simulador -m ping
ansible-playbook -i inventory.ini playbook.yml
# rodar de novo: na segunda vez tem que dar changed=0
ansible-playbook -i inventory.ini playbook.yml
O ping do Ansible deve responder "ping": "pong".
Na primeira execução do playbook aparecem tarefas changed. No PLAY RECAP deve ter failed=0 e unreachable=0.
Na segunda execução deve aparecer changed=0: nada mudou, porque o ambiente já estava pronto.
### 8.4 Conferir dentro da VM
cd ~/telhas-pipeline
IP=$(cd infraestrutura && tofu output -raw ip_da_vm)
ssh aluno@$IP "python3 --version; pip3 --version; ls -ld /home/aluno/simulador /home/aluno/dados"
Devem aparecer as versões do Python e do pip e as duas pastas (/home/aluno/simulador e /home/aluno/dados) com dono aluno.
cd ~/telhas-pipeline
git add infraestrutura/ansible
git commit -m "Adiciona inventario e playbook do Ansible"
git push
## Passo 9 – Enviar o simulador para a VM (SSH/SCP)
cd ~/telhas-pipeline
IP=$(cd infraestrutura && tofu output -raw ip_da_vm)
scp simulador/simulador.py simulador/requirements.txt aluno@$IP:/home/aluno/simulador/
ssh aluno@$IP "ls -l /home/aluno/simulador"
O scp copia arquivos usando a conexão SSH. O último comando lista a pasta da VM e mostra que o simulador.py e o requirements.txt chegaram lá.
## Passo 10 – Rodar o simulador dentro da VM
cd ~/telhas-pipeline
IP=$(cd infraestrutura && tofu output -raw ip_da_vm)
ssh aluno@$IP "python3 /home/aluno/simulador/simulador.py"
ssh aluno@$IP "ls -l /home/aluno/dados"
ssh aluno@$IP 'head -n 4 $(ls -t /home/aluno/dados/telhas_queimas_*.csv | head -n 1)'
O simulador roda na VM (o comando é executado lá pelo SSH). Devem aparecer as mensagens Arquivo gerado: /home/aluno/dados/telhas_queimas_...csv (e, às vezes, telhas_compras_...csv, porque a quantidade de compras varia de 0 a 4). O head mostra o cabeçalho e os primeiros registros.
Agora rode de novo para provar que os dados antigos não são apagados:
ssh aluno@$IP "python3 /home/aluno/simulador/simulador.py"
ssh aluno@$IP "ls -l /home/aluno/dados"
ssh aluno@$IP "wc -l /home/aluno/dados/telhas_queimas_*.csv"
Devem aparecer arquivos novos junto com os anteriores. Cada arquivo telhas_queimas tem 13 linhas: 1 de cabeçalho + 12 registros (um por forno).
### Como os dados se ligam ao problema do projeto
O problema é a falta de controle da queima de lenha em cada forno. Cada registro do simulador representa uma queima e tem:
Identificador: id_queima (e id_lote, id_forno).
Variáveis do problema: tipo_lenha_utilizada, quantidade_lenha_utilizada_kg, temperatura_forno_c, tempo_total_queima_horas, quantidade_telhas_produzidas e quantidade_telhas_com_defeito.
Informação temporal: data_inicio_queima e data_fim_queima.
O arquivo de compras (telhas_compras) traz fornecedor, quantidade em m³, valor pago e umidade da lenha.
### Salvar um exemplo dos dados no repositório
ssh aluno@$IP 'cat $(ls -t /home/aluno/dados/telhas_queimas_*.csv | head -n 1)' > ~/telhas-pipeline/dados/exemplo_dados.csv
head -n 3 ~/telhas-pipeline/dados/exemplo_dados.csv
cd ~/telhas-pipeline
git add dados/exemplo_dados.csv
git commit -m "Adiciona exemplo de dados gerados pelo simulador na VM"
git push
## Passo 11 – README e conferência final do repositório
O README explica o projeto e como reproduzir tudo. Copie o arquivo README.md que acompanha este guia para a raiz do projeto, confira se os nomes e a URL do repositório estão certos e faça o commit:
cp ~/Downloads/README.md ~/telhas-pipeline/README.md
cd ~/telhas-pipeline
git add README.md
git commit -m "Adiciona README com instrucoes de reproducao"
git push
O README tem: descrição do projeto, arquitetura, estrutura das pastas, requisitos, configurações locais (sem expor nada sensível), comandos para reproduzir (criar a VM, configurar, enviar por SSH e executar), problemas conhecidos e a descrição dos dados gerados.
Agora confira o repositório:
git status
git log --oneline
git ls-files
git log --oneline mostra o histórico de commits.
git ls-files lista tudo que está no repositório. Não pode aparecer terraform.tfstate, a pasta .terraform/ nem chave privada.
Abra o repositório no GitHub e confira se as pastas infraestrutura/, simulador/ e dados/ e o README.md estão lá.
cd ~/telhas-pipeline
git config user.name "Julia Fernandes de Ovidio"
git config user.email "EMAIL_DA_JULIA_FERNANDES"
## Passo 12 – Teste de reprodução (destruir e criar de novo)
O professor quer ver que o ambiente pode ser reproduzido a partir do repositório. Ensaie isto antes da apresentação: apagar a VM e criar tudo de novo só com o código.
cd ~/telhas-pipeline/infraestrutura
tofu destroy
tofu apply
IP=$(tofu output -raw ip_da_vm)
ssh-keygen -R $IP
sed -i "s/ansible_host=[0-9.]*/ansible_host=$IP/" ansible/inventory.ini
cd ansible && ansible-playbook -i inventory.ini playbook.yml && cd ../..
scp simulador/simulador.py simulador/requirements.txt aluno@$IP:/home/aluno/simulador/
ssh aluno@$IP "python3 /home/aluno/simulador/simulador.py"
ssh aluno@$IP "ls -l /home/aluno/dados"
A VM antiga é apagada (com os dados dela) e a nova nasce do zero, só com o que está no repositório. Se ao final o simulador gerar os arquivos na VM nova, a reprodução funcionou. O comando ssh-keygen -R limpa a identificação antiga da VM, caso o IP se repita.
# 5. Como comprovar cada requisito na apresentação
A tabela liga cada item da avaliação ao que mostrar. Deixe o computador pronto para a demonstração prática, com as ferramentas instaladas e o Passo 12 já testado.

| Item (nota) | O que mostrar | Onde está |
| --- | --- | --- |
| Simulador (1,00) | Código em simulador/ no GitHub Roda com um comando, sem interface gráfica 12 registros por execução, com identificador, variáveis do problema e data/hora, em CSV | Passos 4 e 10 |
| OpenTofu (1,25) | Arquivos .tf em infraestrutura/ tofu apply criando a VM e o cloud-init integrado VM ligada e respondendo | Passo 6: tofu apply, tofu state list, virsh list --all, ping |
| cloud-init (0,75) | cloud_init.cfg no GitHub Usuário, chave SSH, hostname, fuso e arquivo marcador dentro da VM | Passo 7 |
| Ansible (1,25) | Inventário e playbook em infraestrutura/ansible/ Playbook rodando com sucesso Segunda execução com changed=0 | Passo 8 |
| SSH (0,75) | Conexão SSH da hospedeira para a VM Envio com scp Arquivos no destino da VM | Passo 9 |
| Execução na VM (1,25) | Simulador rodando dentro da VM Dados gravados na VM Nova execução cria arquivos novos e mantém os antigos | Passo 10 |
| GitHub e documentação (0,75) | README completo Pasta infraestrutura/ separada da aplicação Histórico de commits Sem senhas, chaves ou estado do OpenTofu | Passo 11: git log --oneline e git ls-files |


# 6. Problemas comuns

| Problema | Causa provável | O que fazer |
| --- | --- | --- |
| Permission denied ao criar a VM (tofu apply) | AppArmor do Ubuntu bloqueando o disco | Aplicar a correção do Passo 6 (security_driver = "none") e rodar tofu apply de novo. |
| tofu init não acha o provider | Sem internet ou versão errada | Conferir a conexão e se o main.tf tem version = "0.8.3". |
| tofu plan diz que não achou o arquivo ~/.ssh/id_ed25519.pub | A chave SSH ainda não foi criada | Voltar ao Passo 2.1, criar a chave e rodar tofu plan de novo. |
| Erro dizendo que a rede default não existe ou está inativa | Rede do libvirt desligada | Rodar os dois comandos net-start e net-autostart do Passo 1. |
| Erro de KVM ao iniciar a VM | Virtualização desligada na BIOS | Conferir o número do egrep no Passo 1 e ativar VT-x/AMD-V na BIOS. |
| SSH: Connection refused ou timed out logo depois do apply | O cloud-init ainda está configurando a VM | Esperar cerca de 1 minuto e tentar de novo. Ver o IP com virsh -c qemu:///system domifaddr telhas-vm. |
| SSH: Permission denied (publickey) | A VM foi criada com outra chave, ou a chave não existia | Conferir se ~/.ssh/id_ed25519.pub existe, rodar tofu destroy e tofu apply de novo. |
| SSH: REMOTE HOST IDENTIFICATION HAS CHANGED | A VM foi recriada com o mesmo IP | Rodar ssh-keygen -R $IP. |
| Ansible: UNREACHABLE | IP errado no inventário | Rodar de novo o sed do Passo 8.2 e conferir com grep ansible_host. |
| Ansible: erro de lock do apt | O apt está em uso pelo cloud-init | Esperar um pouco e rodar o playbook de novo. |
| tofu destroy reclama de Directory not empty no pool | Sobrou arquivo na pasta do pool | Rodar sudo rm -f /var/lib/libvirt/images/telhas/* e depois tofu destroy de novo. |
| tofu apply diz que o domínio já existe | A VM antiga ficou registrada no libvirt | Rodar virsh -c qemu:///system destroy telhas-vm e virsh -c qemu:///system undefine telhas-vm, e depois tofu apply. |
| git push pede senha e falha | O GitHub só aceita token | Usar o token do Passo 2.3 no lugar da senha. |


