# Telhas Pipeline – Projeto Integrado (Data Science)

**Equipe:** Julia Docema de Carvalho e Julia Fernandes de Ovidio

## Descrição

O problema do projeto é a falta de controle da queima de lenha em cada forno de uma fábrica de telhas de barro. Para começar a resolver isso, o repositório tem:

- um **simulador de dados** (`simulador/`) que gera registros de queima dos fornos e de compra de lenha em arquivos CSV;
- o código da **infraestrutura** (`infraestrutura/`) que cria e prepara uma máquina virtual (VM) Linux onde o simulador roda.

Tudo é feito por código:

| Ferramenta | O que faz |
|---|---|
| OpenTofu | Cria a VM (libvirt/KVM) na máquina hospedeira |
| cloud-init | Configuração inicial da VM: usuário, chave SSH, hostname e fuso horário |
| Ansible | Instala o Python e cria as pastas do simulador |
| SSH/SCP | Envia o simulador para a VM e executa lá dentro |

## Arquitetura

```
Máquina hospedeira (Linux)
  ├─ OpenTofu ──► cria a VM
  ├─ cloud-init ► usuário "aluno" + chave SSH
  ├─ Ansible ───► Python 3 e pastas
  └─ SSH/SCP ───► envia o simulador
                        │
                        ▼
Máquina virtual (Ubuntu 24.04)
  └─ simulador.py ──► CSVs em /home/aluno/dados
```

## Estrutura do repositório

```
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
```

## Requisitos (máquina hospedeira)

- Linux (Ubuntu ou Linux Mint) com virtualização ativada na BIOS
- libvirt/KVM: `sudo apt install -y qemu-system-x86 libvirt-daemon-system libvirt-clients`
- Seu usuário nos grupos `libvirt` e `kvm`: `sudo usermod -aG libvirt,kvm $USER` (depois, sair e entrar de novo na sessão)
- OpenTofu 1.6 ou mais novo: https://opentofu.org/docs/intro/install/
- Ansible e Git: `sudo apt install -y ansible git`
- Internet (para baixar a imagem Ubuntu 24.04, cerca de 600 MB)
- Cerca de 12 GB livres em disco e 2 GB de RAM livres para a VM

## Configurações locais (nada sensível vai para o repositório)

- **Chave SSH:** o cloud-init autoriza a chave pública `~/.ssh/id_ed25519.pub`. Se ela não existir:
  `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""`
  Para usar outra chave: `tofu apply -var 'chave_publica=~/.ssh/outra_chave.pub'`
  (e trocar `ansible_ssh_private_key_file` no `inventory.ini`).
- **IP da VM:** o IP muda quando a VM é recriada. Depois do `tofu apply`, atualize o `inventory.ini` (comando no passo 3).
- Estado do OpenTofu (`*.tfstate`), pasta `.terraform/`, chaves privadas e senhas **não** são publicados (ver `.gitignore`).

## Como reproduzir

**1. Clonar o repositório**

```
git clone https://github.com/judocema/telhas-pipeline.git
cd telhas-pipeline/infraestrutura
```

**2. Criar a VM com OpenTofu (usa o cloud-init)**

```
tofu init
tofu plan
tofu apply
```

**3. Atualizar o IP no inventário do Ansible**

```
sed -i "s/ansible_host=[0-9.]*/ansible_host=$(tofu output -raw ip_da_vm)/" ansible/inventory.ini
```

**4. Preparar a VM com Ansible** (rodar de novo não causa erro)

```
cd ansible
ansible -i inventory.ini simulador -m ping
ansible-playbook -i inventory.ini playbook.yml
cd ../..
```

**5. Enviar o simulador por SSH/SCP**

```
IP=$(cd infraestrutura && tofu output -raw ip_da_vm)
scp simulador/simulador.py simulador/requirements.txt aluno@$IP:/home/aluno/simulador/
```

**6. Executar o simulador dentro da VM**

```
ssh aluno@$IP "python3 /home/aluno/simulador/simulador.py"
ssh aluno@$IP "ls -l /home/aluno/dados"
```

Cada execução cria arquivos novos (com data e hora no nome), então os dados anteriores não são perdidos.

**7. Destruir a VM (opcional)**

```
cd infraestrutura
tofu destroy
```

## Problemas conhecidos

- **`Permission denied` ao criar a VM (AppArmor do Ubuntu):**
  ```
  sudo sed -i -E 's,#?(security_driver)\s*=.*,\1 = "none",g' /etc/libvirt/qemu.conf
  sudo systemctl restart libvirtd
  ```
  e rodar `tofu apply` de novo.
- **`REMOTE HOST IDENTIFICATION HAS CHANGED` no SSH:** a VM foi recriada. Rode `ssh-keygen -R $IP`.

## Dados gerados

O simulador gera, a cada execução, dois arquivos CSV em `/home/aluno/dados` (na VM):

- `telhas_queimas_<data_hora>.csv`: 12 registros, um por forno (F001 a F012).
- `telhas_compras_<data_hora>.csv`: de 0 a 4 compras de lenha.

Campos de `telhas_queimas`:

- **Identificação:** `id_queima`, `id_lote`, `id_forno`, `tipo_forno`
- **Lenha:** `tipo_lenha_utilizada`, `quantidade_lenha_utilizada_kg`
- **Queima:** `data_inicio_queima`, `data_fim_queima`, `tempo_total_queima_horas`, `temperatura_forno_c`, `responsavel_queima`
- **Produção:** `quantidade_telhas_no_forno`, `quantidade_telhas_produzidas`, `quantidade_telhas_com_defeito`

Campos de `telhas_compras`: `id_compra`, `data_compra`, `tipo_lenha`, `fornecedor`, `quantidade_comprada_m3`, `valor_pago`, `umidade_lenha_pct`.

Um exemplo de saída está em `dados/exemplo_dados.csv`.
