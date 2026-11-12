# Telhas Pipeline – Projeto Integrado (Data Science)

**Equipe:** Julia Docema de Carvalho e Julia Fernandes de Ovidio

**Tema:** Automação e Escalabilidade de Pipelines de Big Data e Análise de Dados

## 1. Problema

Numa fábrica de telhas de barro, a lenha é o principal insumo da queima, mas não existe controle de quanto cada forno gasta em cada queima. O objetivo do projeto é montar um pipeline de dados que gere, organize e analise esses registros, para responder: **quanto de lenha uma queima deveria gastar e quais queimas gastaram demais?**

## 2. Visão geral do pipeline

```
Máquina hospedeira (Linux)
  ├─ OpenTofu + cloud-init ──► cria as 2 VMs
  └─ Ansible ────────────────► instala os programas nas VMs

VM telhas-vm (Ubuntu 24.04)                 VM telhas-monitor (Ubuntu 24.04)
  ├─ simulador.py ──► CSVs                    ├─ Prometheus (coleta a cada 15 s)
  └─ node_exporter ─────── CPU, RAM, ───────► └─ Grafana (gráficos)
                           disco e rede

CSVs ──► Limpeza (R) ──► CSV limpo ──► EDA, DW, OLAP, ML, Hadoop, Spark e Estatística (Colab)
```

| Etapa | Ferramentas | Onde está |
|---|---|---|
| Infraestrutura | OpenTofu, cloud-init, Ansible, libvirt/KVM | `infraestrutura/` |
| Geração de dados | Python | `simulador/` |
| Monitoramento | node_exporter, Prometheus, Grafana | `infraestrutura/monitor.tf` e `ansible/monitoramento.yml` |
| Limpeza | R (dplyr) | `analise/limpeza_telhas.Rmd` |
| Análise e Big Data | Python no Google Colab (pandas, seaborn, SQLite, scikit-learn, PySpark, SciPy) | `analise/EDA_telhas_queimas.ipynb` |

## 3. Estrutura do repositório

```
telhas-pipeline/
├── infraestrutura/
│   ├── main.tf                  # OpenTofu: VM do gerador (telhas-vm)
│   ├── monitor.tf               # OpenTofu: VM de monitoramento (telhas-monitor)
│   ├── variables.tf             # variáveis das duas VMs
│   ├── cloud_init.cfg           # usuário, chave SSH, hostname e fuso horário
│   └── ansible/
│       ├── inventory.ini        # acesso às duas VMs
│       ├── playbook.yml         # Python e pastas do simulador
│       └── monitoramento.yml    # node_exporter, Prometheus e Grafana
├── simulador/
│   ├── simulador.py             # gerador de dados simulados
│   └── requirements.txt
├── analise/
│   ├── limpeza_telhas.Rmd             # limpeza no R
│   ├── EDA_telhas_queimas.ipynb       # EDA, DW, OLAP, ML, Hadoop, Spark e Estatística
│   ├── complemento_limpeza_dados.md
│   ├── complemento_eda_colab.md
│   └── complemento_pipeline_bigdata.md
├── dados/
│   ├── exemplo_dados.csv        # exemplo de saída do simulador
│   └── telhas_queimas_limpo.csv # base limpa usada na análise
├── .gitignore
└── README.md
```

## 4. Etapas do projeto

### 4.1 Infraestrutura como código

Tudo é criado por código, sem passos manuais na VM:

- **OpenTofu** cria as VMs no libvirt/KVM a partir da imagem cloud do Ubuntu 24.04.
- **cloud-init** configura na primeira inicialização o usuário `aluno`, a chave SSH, o hostname e o fuso horário. O acesso é só por chave (senha desligada).
- **Ansible** prepara as VMs. Os playbooks podem ser rodados de novo sem causar erro.
- Estado do OpenTofu, chaves e senhas não vão para o repositório (`.gitignore`).

### 4.2 Simulador de dados

O `simulador.py` usa só bibliotecas padrão do Python. Cada execução gera, na VM, em `/home/aluno/dados`:

- `telhas_queimas_<data_hora>.csv`: 12 registros, um por forno (F001 a F012), com forno, tipo de lenha, lenha usada (kg), início, fim, tempo, temperatura, responsável, telhas no forno, produzidas e com defeito;
- `telhas_compras_<data_hora>.csv`: de 0 a 4 compras de lenha (fornecedor, m³, valor e umidade).

Os campos, fornos, tipos de lenha e responsáveis seguem a planilha da fábrica usada no projeto. Para a análise foram gerados **52 arquivos (624 queimas)**.

### 4.3 Monitoramento da infraestrutura

Uma segunda VM, a `telhas-monitor`, monitora a VM do gerador de dados:

| Peça | VM | Porta | Função |
|---|---|---|---|
| node_exporter | telhas-vm | 9100 | Expõe CPU, memória, disco e rede da VM |
| Prometheus | telhas-monitor | 9090 | Coleta os números a cada 15 segundos e guarda o histórico |
| Grafana | telhas-monitor | 3000 | Mostra os gráficos de processamento, memória, espaço em disco e rede |

O Ansible instala as três peças, aponta o Prometheus para o IP da `telhas-vm` (lido do `inventory.ini`) e já liga o Grafana ao Prometheus. O painel usado é o **Node Exporter Full** (ID 1860).

### 4.4 Limpeza dos dados (R)

Os 52 CSVs foram juntados e verificados por dimensão de qualidade: completude, validade (faixas de lenha, tempo, temperatura e telhas, listas de tipos), consistência (datas, tempo total, telhas e defeitos), unicidade e valores fora do padrão. Nenhum registro precisou ser removido. Foram criadas as variáveis `telhas_boas`, `taxa_defeito_pct`, `lenha_kg_por_hora`, `lenha_kg_por_mil_telhas` e `queima_sobreposta`. Resultado: `dados/telhas_queimas_limpo.csv` (624 linhas, 22 colunas). Detalhes em `analise/complemento_limpeza_dados.md`.

### 4.5 Análise exploratória (Colab)

Estrutura e qualidade da base, estatística descritiva, gráficos escolhidos pelo tipo de variável (contagem, histograma, densidade, boxplot, barras e mapa de calor) e tabelas-resumo por forno e por tipo de lenha. Detalhes em `analise/complemento_eda_colab.md`.

### 4.6 Big Data, Machine Learning e Estatística (Colab)

- **Data Warehouse (SQLite)** em esquema estrela: `fato_queima` (624 linhas) e as dimensões `dim_forno`, `dim_lenha`, `dim_responsavel` e `dim_tempo`, carregadas por ETL em Python.
- **OLAP:** roll-up, drill-down, slice, dice e pivot sobre a view `vw_cubo`, além de cubo 3D, gráfico 2D e gráfico interativo.
- **Machine Learning:** regressão com Random Forest para prever a lenha de cada queima e apontar as que gastaram acima do esperado.
- **Hadoop:** MapReduce e YARN simulados em Python, com o papel do HDFS e do Hive.
- **Spark:** DataFrames e Spark SQL (seleção, filtro, agrupamento, ordenação e indicadores), com o resultado gravado no DW.
- **Probabilidade e Estatística:** medidas de posição e dispersão, frequências, probabilidades, Bayes, qui-quadrado, normalidade, intervalo de confiança, ANOVA, Kruskal-Wallis, correlações e anomalias.

Detalhes em `analise/complemento_pipeline_bigdata.md`.

## 5. Principais resultados

| Resultado | Valor |
|---|---|
| Lenha média por queima | 1.769 kg (mediana 1.555 kg) |
| Lenha média por mil telhas | 155 kg, variando de 90 a 220 kg |
| Taxa média de defeito | cerca de 6% |
| Correlação lenha x telhas no forno | 0,83 |
| Queimas em alerta (acima de 200 kg por mil telhas) | 84 de 624 (13,5%) |
| Modelo de regressão (teste) | MAE 364 kg, R² 0,70 (erro 45% menor que chutar a média) |
| Diferença entre tipos de lenha e de forno | Não significativa (ANOVA p = 0,20 e 0,955) |
| IC 95% da lenha por mil telhas | 152,3 a 158,1 kg |

**Conclusões:**

1. O total de lenha depende do tamanho do forno. Por isso, a comparação justa entre queimas é a **lenha por mil telhas**.
2. O mesmo forno gasta valores muito diferentes de uma queima para outra (de 90 a 220 kg por mil telhas). O problema não são casos isolados, e sim essa **variação**.
3. Tipo de forno e tipo de lenha não explicam essa variação com significância estatística.
4. Para a fábrica, a proposta é: acompanhar a lenha por mil telhas em cada queima, usar o modelo para calcular a lenha esperada e investigar as queimas acima do limite de alerta (forno, lenha e responsável).

**Sobre os dados:** são simulados. O simulador usa a hora da execução como início da queima, por isso a análise foi feita por forno, lenha e responsável, e não por data. Tempo e temperatura não têm relação com a lenha nestes dados.

## 6. Como reproduzir

**Requisitos (máquina hospedeira):** Linux com virtualização ativada, libvirt/KVM, OpenTofu 1.6+, Ansible e Git; cerca de 4 GB de RAM e 20 GB de disco livres para as duas VMs; chave SSH em `~/.ssh/id_ed25519` (`ssh-keygen -t ed25519`).

**1. Criar as VMs**

```
git clone https://github.com/judocema/telhas-pipeline.git
cd telhas-pipeline/infraestrutura
tofu init
tofu apply
tofu output
```

Se algum IP aparecer vazio, rode `tofu refresh` e `tofu output` de novo.

**2. Atualizar os IPs no inventário**

```
sed -i "s/^telhas-vm ansible_host=.*/telhas-vm ansible_host=$(tofu output -raw ip_da_vm)/" ansible/inventory.ini
sed -i "s/^telhas-monitor ansible_host=.*/telhas-monitor ansible_host=$(tofu output -raw ip_do_monitor)/" ansible/inventory.ini
```

**3. Preparar as VMs com Ansible**

```
cd ansible
ansible -i inventory.ini all -m ping
ansible-playbook -i inventory.ini playbook.yml
ansible-playbook -i inventory.ini monitoramento.yml
cd ../..
```

**4. Enviar e executar o simulador**

```
IP=$(cd infraestrutura && tofu output -raw ip_da_vm)
scp simulador/simulador.py simulador/requirements.txt aluno@$IP:/home/aluno/simulador/
ssh aluno@$IP "python3 /home/aluno/simulador/simulador.py"
ssh aluno@$IP "ls -l /home/aluno/dados"
```

**5. Acessar o monitoramento**

```
MON=$(cd infraestrutura && tofu output -raw ip_do_monitor)
echo "Prometheus: http://$MON:9090/targets"
echo "Grafana:    http://$MON:3000"
```

No Grafana (usuário `admin`, senha `admin` no primeiro acesso): **Dashboards > New > Import**, ID `1860`, fonte **Prometheus**, e escolher o job `simulador`.

**6. Limpeza e análise**

- Copiar os CSVs da VM para uma pasta `brutos` e rodar `analise/limpeza_telhas.Rmd` no RStudio. O resultado vai para `limpos/telhas_queimas_limpo.csv`.
- Colocar o CSV limpo no Google Drive (`MyDrive/Projeto_PI/`) e executar `analise/EDA_telhas_queimas.ipynb` no Google Colab.

**7. Destruir as VMs**

```
cd infraestrutura
tofu destroy
```

**Observações:** se a criação da VM der `Permission denied` (AppArmor do Ubuntu), defina `security_driver = "none"` em `/etc/libvirt/qemu.conf`, reinicie o `libvirtd` e rode `tofu apply` de novo. Se o SSH avisar `REMOTE HOST IDENTIFICATION HAS CHANGED`, a VM foi recriada: rode `ssh-keygen -R <IP>`.
