# Complemento – Limpeza e organização dos dados (R)

**Projeto Integrado – Data Science** | Fábrica de telhas de barro
**Equipe:** Julia Docema de Carvalho e Julia Fernandes de Ovidio
**Arquivo da etapa:** `analise/limpeza_telhas.Rmd`

## 1. Objetivo

Pegar os CSVs gerados pelo simulador, verificar a qualidade dos dados e organizar uma base única e limpa para a análise.

## 2. Dados de entrada

| Item | Valor |
| --- | --- |
| Arquivos CSV | 52 (gerados pelo simulador na VM) |
| Registros | 624 queimas (12 por arquivo, uma por forno) |
| Fornos / tipos de forno | 12 (F001 a F012) / 3 (Intermitente, Túnel e Caieira) |
| Tipos de lenha | 5 (Aroeira, Pinus, Angico, Resíduo de Madeira e Eucalipto) |
| Responsáveis | 10 |
| Colunas originais | 14 |

## 3. O que foi feito

Usamos o RStudio com o pacote `dplyr`, no estilo das aulas, seguindo as dimensões de qualidade:

1. **Importação:** os 52 CSVs foram juntados numa tabela só, guardando o nome do arquivo de origem de cada linha.
2. **Conhecendo os dados:** `head`, `dim`, `names`, `str`, `summary` e tabelas de frequência.
3. **Completude:** contagem de valores ausentes por coluna.
4. **Conversão de tipos:** datas de texto para data e hora (fuso `America/Sao_Paulo`) e remoção de espaços nos textos.
5. **Validade, consistência e unicidade:** regras da tabela abaixo.
6. **Valores fora do padrão:** marcados pela regra do boxplot, só para observação.
7. **Relatório de qualidade, limpeza e saída:** contagem dos problemas, filtro dos registros válidos e gravação do CSV limpo, sem alterar os brutos.

| Dimensão | Regra |
| --- | --- |
| Completude | Nenhuma coluna com valor ausente |
| Validade | Lenha > 0; tempo entre 0 e 120 h; temperatura entre 600 e 1100 °C; telhas > 0 e defeitos ≥ 0 |
| Validade | Tipo de forno e de lenha dentro das listas conhecidas; `id_forno` no formato `F000` |
| Consistência | Fim depois do início; tempo total igual a fim – início (tolerância de 0,2 h) |
| Consistência | Produzidas ≤ telhas no forno; defeitos ≤ produzidas; cada forno com um só tipo |
| Unicidade | `id_queima` e `id_lote` sem repetição e sem linhas duplicadas |

## 4. Resultado

| Verificação | Resultado |
| --- | --- |
| Valores ausentes | 0 |
| Registros inválidos ou inconsistentes | 0 |
| Identificadores repetidos | 0 |
| Registros removidos | 0 |
| CSV limpo | 624 linhas e 22 colunas (`dados/telhas_queimas_limpo.csv`) |

Nenhum registro foi removido porque os dados do simulador já saem bem formados. As regras ficam no notebook e valem para dados novos ou reais.

**Fora do padrão:** só a lenha total teve valores marcados (30 queimas), todos de fornos de 18 mil telhas, que naturalmente gastam mais. Não é erro. Por isso, para comparar fornos, usamos a lenha por mil telhas, que não teve nenhum valor fora do padrão.

## 5. Variáveis criadas

| Variável | O que é |
| --- | --- |
| `telhas_boas` | Telhas produzidas menos as com defeito |
| `taxa_defeito_pct` | Percentual de telhas com defeito |
| `lenha_kg_por_hora` | Lenha usada por hora de queima |
| `lenha_kg_por_mil_telhas` | Lenha usada a cada mil telhas produzidas |
| `data_queima` e `mes_queima` | Dia e mês do início da queima |
| `queima_sobreposta` | Indica se a queima começou antes do fim da anterior no mesmo forno |
| `arquivo_origem` | CSV de onde veio o registro |

## 6. Observação sobre as datas

O simulador usa a hora em que roda como início da queima. Como os arquivos foram gerados em sequência, a base tem só 3 horários de início, e 600 das 624 queimas aparecem como sobrepostas no mesmo forno. Esses registros foram **marcados, e não removidos**, porque lenha, temperatura e defeitos continuam válidos. Por isso as análises foram feitas por forno, tipo de lenha, tipo de forno e responsável, e não por data.
