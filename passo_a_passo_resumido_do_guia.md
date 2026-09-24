## Passo a passo resumido – Checkpoint 01 (DevOps)
Só os comandos, na ordem. O conteúdo completo dos arquivos está no guia detalhado (mesma numeração de passos).
Repositório: https://github.com/judocema/telhas-pipeline   |   Entrega: 30/09/2026
Tudo é feito no computador Linux (máquina hospedeira). Faça um commit a cada etapa que funcionou. Os IP=... valem só no terminal em que foram digitados: se abrir um terminal novo, digite de novo.
## Passo 1 – Instalar as ferramentas
cat /etc/os-release
egrep -c '(vmx|svm)' /proc/cpuinfo
sudo apt update
sudo apt install -y qemu-system-x86 libvirt-daemon-system libvirt-clients ansible git curl
sudo usermod -aG libvirt,kvm $USER
O egrep deve mostrar 1 ou mais (se for 0, ligar a virtualização na BIOS). Depois do usermod, saia da sessão e entre de novo. Aí continue:
groups
virsh -c qemu:///system list --all
virsh -c qemu:///system net-list --all
# se a rede "default" estiver inactive:
virsh -c qemu:///system net-start default
virsh -c qemu:///system net-autostart default
curl --proto '=https' --tlsv1.2 -fsSL \
https://get.opentofu.org/install-opentofu.sh -o install-opentofu.sh
chmod +x install-opentofu.sh
./install-opentofu.sh --install-method deb
rm -f install-opentofu.sh
tofu version
## Passo 2 – Chave SSH e Git
[ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "telhas-vm"
ls ~/.ssh
git config --global user.name "Julia Docema de Carvalho"
git config --global user.email "julia.docema@sou.unifeob.edu.br"
git config --global credential.helper 'cache --timeout=3600'
Gerar um token no GitHub (Settings > Developer settings > Personal access tokens, permissão repo). Ele é a senha do git push.
## Passo 3 – Repositório
No GitHub (conta judocema): New repository > telhas-pipeline > vazio (sem README e sem .gitignore).
mkdir -p ~/telhas-pipeline/infraestrutura/ansible
mkdir -p ~/telhas-pipeline/simulador
mkdir -p ~/telhas-pipeline/dados
cd ~/telhas-pipeline
git init
git branch -M main
Criar o .gitignore na raiz (conteúdo no guia detalhado, Passo 3.3). Depois:
git add .gitignore
git commit -m "Cria .gitignore do projeto"
git remote add origin https://github.com/judocema/telhas-pipeline.git
git push -u origin main
## Passo 4 – Simulador
cp ~/telhas/scripts/gerador.py ~/telhas-pipeline/simulador/simulador.py
No simulador.py, trocar só a linha PASTA_SAIDA = ... pelo bloco do Passo 4 do guia detalhado. Criar simulador/requirements.txt (só comentários). Depois:
cd ~/telhas-pipeline
git add simulador
git commit -m "Adiciona simulador de dados da queima de lenha"
git push
## Passo 5 – Arquivos da infraestrutura
Criar, em ~/telhas-pipeline/infraestrutura/, os arquivos abaixo (conteúdo no guia detalhado, Passo 5):
variables.tf
main.tf
cloud_init.cfg
## Passo 6 – Criar a VM (OpenTofu)
cd ~/telhas-pipeline/infraestrutura
tofu init
tofu plan
tofu apply
No apply, digitar yes. Deve terminar com Plan: 5 to add no plan e Apply complete! com o ip_da_vm. Depois:
tofu state list
virsh -c qemu:///system list --all
ping -c 3 $(tofu output -raw ip_da_vm)
Se der Permission denied no apply: rodar os comandos abaixo (correção do AppArmor) e repetir o tofu apply.
sudo sed -i -E 's,#?(security_driver)\s*=.*,\1 = "none",g' /etc/libvirt/qemu.conf
sudo systemctl restart libvirtd
cd ~/telhas-pipeline
git add infraestrutura/main.tf infraestrutura/variables.tf infraestrutura/.terraform.lock.hcl
git commit -m "Adiciona OpenTofu para provisionar a VM"
git push
## Passo 7 – Conferir o cloud-init
Esperar cerca de 1 minuto depois do apply. Na primeira conexão, digitar yes.
IP=$(cd ~/telhas-pipeline/infraestrutura && tofu output -raw ip_da_vm)
ssh aluno@$IP
Dentro da VM:
hostname
whoami
sudo whoami
timedatectl | grep "Time zone"
cat /etc/cloud-init-telhas.txt
cloud-init status
sudo sshd -T | grep -i passwordauthentication
exit
Esperado: telhas-vm, aluno, root, America/Sao_Paulo, texto do arquivo, status: done, passwordauthentication no.
cd ~/telhas-pipeline
git add infraestrutura/cloud_init.cfg
git commit -m "Adiciona cloud-init: usuario, chave SSH, hostname e fuso horario"
git push
## Passo 8 – Preparar a VM (Ansible)
Criar infraestrutura/ansible/inventory.ini e infraestrutura/ansible/playbook.yml (conteúdo no guia detalhado, Passo 8.1). Depois:
cd ~/telhas-pipeline/infraestrutura
sed -i "s/ansible_host=[0-9.]*/ansible_host=$(tofu output -raw ip_da_vm)/" ansible/inventory.ini
grep ansible_host ansible/inventory.ini
cd ansible
ansible -i inventory.ini simulador -m ping
ansible-playbook -i inventory.ini playbook.yml
# rodar de novo: na segunda vez tem que dar changed=0
ansible-playbook -i inventory.ini playbook.yml
cd ~/telhas-pipeline
IP=$(cd infraestrutura && tofu output -raw ip_da_vm)
ssh aluno@$IP "python3 --version; pip3 --version; ls -ld /home/aluno/simulador /home/aluno/dados"
cd ~/telhas-pipeline
git add infraestrutura/ansible
git commit -m "Adiciona inventario e playbook do Ansible"
git push
## Passo 9 – Enviar o simulador (SSH/SCP)
cd ~/telhas-pipeline
IP=$(cd infraestrutura && tofu output -raw ip_da_vm)
scp simulador/simulador.py simulador/requirements.txt aluno@$IP:/home/aluno/simulador/
ssh aluno@$IP "ls -l /home/aluno/simulador"
## Passo 10 – Rodar o simulador na VM
cd ~/telhas-pipeline
IP=$(cd infraestrutura && tofu output -raw ip_da_vm)
ssh aluno@$IP "python3 /home/aluno/simulador/simulador.py"
ssh aluno@$IP "ls -l /home/aluno/dados"
ssh aluno@$IP 'head -n 4 $(ls -t /home/aluno/dados/telhas_queimas_*.csv | head -n 1)'
Rodar de novo (os arquivos antigos ficam, aparecem novos; cada arquivo tem 13 linhas = cabeçalho + 12 fornos):
ssh aluno@$IP "python3 /home/aluno/simulador/simulador.py"
ssh aluno@$IP "ls -l /home/aluno/dados"
ssh aluno@$IP "wc -l /home/aluno/dados/telhas_queimas_*.csv"
Salvar um exemplo no repositório:
ssh aluno@$IP 'cat $(ls -t /home/aluno/dados/telhas_queimas_*.csv | head -n 1)' > ~/telhas-pipeline/dados/exemplo_dados.csv
head -n 3 ~/telhas-pipeline/dados/exemplo_dados.csv
cd ~/telhas-pipeline
git add dados/exemplo_dados.csv
git commit -m "Adiciona exemplo de dados gerados pelo simulador na VM"
git push
## Passo 11 – README e conferência
cp ~/Downloads/README.md ~/telhas-pipeline/README.md
cd ~/telhas-pipeline
git add README.md
git commit -m "Adiciona README com instrucoes de reproducao"
git push
git status
git log --oneline
git ls-files
Em git ls-files não pode aparecer terraform.tfstate, .terraform/ nem chave privada. A Julia Fernandes de Ovidio também precisa aparecer no histórico (commits com o usuário dela).
## Passo 12 – Teste de reprodução
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
Se a nova VM gerar os CSVs no final, a reprodução funcionou.
# Prints para o relatório
tofu version, ansible --version e a rede default ativa (Passo 1)
tofu apply concluído, tofu state list e virsh list --all (Passo 6)
SSH entrando sem senha e os comandos do cloud-init (Passo 7)
Playbook na 1ª e na 2ª execução (changed=0) e a conferência na VM (Passo 8)
scp e ls -l /home/aluno/simulador na VM (Passo 9)
Simulador rodando duas vezes, ls -l dos dados e head do CSV (Passo 10)
git log --oneline, git ls-files e o repositório no GitHub (Passo 11)
# Checklist final
- [ ]  Ferramentas instaladas e chave SSH criada
- [ ]  Repositório criado, com .gitignore
- [ ]  Simulador em simulador/
- [ ]  main.tf, variables.tf e cloud_init.cfg em infraestrutura/
- [ ]  VM criada por tofu apply e cloud-init conferido
- [ ]  Ansible rodado duas vezes (changed=0 na segunda)
- [ ]  Simulador enviado por scp e executado na VM (duas vezes)
- [ ]  dados/exemplo_dados.csv e README.md no repositório
- [ ]  Commits das duas integrantes; sem chaves nem estado do OpenTofu no repositório
- [ ]  Teste de reprodução (Passo 12) ensaiado
- [ ]  Link do repositório no Classroom até 30/09/2026