# Complemento – Limpeza e organização dos dados no R

**Projeto Integrado – Data Science** | Fábrica de telhas de barro
**Tema:** Automação e Escalabilidade de Pipelines de Big Data e Análise de Dados
**Equipe:** Julia Docema de Carvalho e Julia Fernandes de Ovidio
**Etapa:** Limpeza e organização dos dados (R / RStudio)

Este arquivo complementa o repositório e explica o que foi feito nesta etapa do projeto.

## 1. Objetivo da etapa

No Checkpoint 01 criamos a infraestrutura e o simulador, que gera arquivos CSV com os dados da queima de lenha nos fornos. Nesta etapa pegamos esses CSVs, verificamos a qualidade dos dados, corrigimos o que fosse preciso e organizamos tudo para a análise.

O problema que escolhemos resolver é a **falta de controle sobre a queima de lenha em cada forno**. Por isso, depois da limpeza, calculamos o consumo de lenha por forno, por tipo de lenha, por tipo de forno e por responsável.

## 2. Dados de entrada

| Item | Valor |
| --- | --- |
| Origem | Simulador de dados rodando na VM |
| Arquivos CSV | 52 |
| Registros (queimas) | 624, sendo 12 por arquivo (um por forno) |
| Fornos | 12 (F001 a F012) |
| Tipos de forno | 3 (Intermitente, Túnel e Caieira) |
| Tipos de lenha | 5 (Aroeira, Pinus, Angico, Resíduo de Madeira e Eucalipto) |
| Responsáveis | 10 |
| Colunas originais | 14 |

As colunas originais são: `id_queima`, `id_forno`, `tipo_forno`, `tipo_lenha_utilizada`, `quantidade_lenha_utilizada_kg`, `data_inicio_queima`, `data_fim_queima`, `tempo_total_queima_horas`, `temperatura_forno_c`, `quantidade_telhas_no_forno`, `responsavel_queima`, `id_lote`, `quantidade_telhas_produzidas` e `quantidade_telhas_com_defeito`.

## 3. O que foi feito

Usamos o RStudio, com o pacote `dplyr`, no mesmo estilo das aulas (`read.csv`, `select`, `filter`, `mutate`, `group_by`, `summarise` e o operador pipe). O trabalho foi feito em um notebook R Markdown, e o roteiro seguiu as dimensões de qualidade vistas em aula.

1. **Importação:** lemos os 52 CSVs e juntamos numa tabela só. Guardamos o nome do arquivo de origem de cada linha, para poder rastrear de onde veio cada registro.
2. **Conhecendo os dados:** usamos o roteiro da aula (`head`, `dim`, `names`, `str`, `summary`) e fizemos tabelas de frequência das variáveis categóricas.
3. **Completude:** contamos os valores ausentes de cada coluna.
4. **Conversão de tipos:** as datas vinham como texto e foram convertidas para data e hora. Também removemos espaços sobrando nos textos.
5. **Validade:** conferimos se os valores estão dentro do esperado (regras na tabela abaixo).
6. **Consistência:** conferimos se os dados não se contradizem entre as colunas.
7. **Unicidade:** procuramos identificadores e linhas repetidas.
8. **Novas variáveis:** criamos variáveis de validação (verdadeiro ou falso) e variáveis de análise.
9. **Valores fora do padrão:** marcamos os outliers pela regra do boxplot, só para observação.
10. **Relatório resumido de qualidade:** juntamos a contagem de problemas de cada tipo numa tabela só.
11. **Limpeza:** mantivemos só os registros válidos e sem repetição, e ordenamos por data e forno.
12. **Resumos:** calculamos o consumo de lenha por forno, por tipo de lenha, por tipo de forno e por responsável.
13. **Saída:** salvamos o CSV limpo, sem alterar os CSVs brutos.

## 4. Regras de validação usadas

| Dimensão | Regra |
| --- | --- |
| Completude | Nenhuma coluna pode ter valor ausente |
| Validade | Lenha utilizada maior que zero |
| Validade | Tempo total de queima maior que zero e até 120 horas |
| Validade | Temperatura do forno entre 600 e 1100 °C |
| Validade | Quantidades de telhas maiores que zero e defeitos maiores ou iguais a zero |
| Validade | Tipo de forno e tipo de lenha dentro das listas conhecidas |
| Validade | `id_forno` no formato `F` mais três números (exemplo: `F001`) |
| Consistência | Data de fim não pode ser antes da data de início |
| Consistência | O tempo total de queima precisa bater com a diferença entre fim e início (tolerância de 0,2 hora) |
| Consistência | Telhas produzidas não podem ser mais do que as que entraram no forno |
| Consistência | Telhas com defeito não podem ser mais do que as produzidas |
| Consistência | O mesmo forno tem sempre o mesmo tipo |
| Unicidade | `id_queima` e `id_lote` não podem se repetir, e não pode haver linhas totalmente repetidas |

Os limites de temperatura e de tempo foram escolhidos por nós como faixas razoáveis para a queima de cerâmica. Eles ficam no começo do notebook e podem ser mudados.

## 5. Resultado da verificação

| Verificação | Resultado |
| --- | --- |
| Registros lidos | 624 (52 arquivos) |
| Registros com valor ausente | 0 |
| Registros inválidos (todas as regras de validade) | 0 |
| Inconsistências de datas | 0 |
| `id_queima` e `id_lote` repetidos | 0 |
| Registros válidos | 624 |
| Registros removidos na limpeza | 0 |
| CSV limpo | 624 linhas e 22 colunas |

Nenhum registro foi removido porque os dados vêm de um simulador e já saem bem formados. Mesmo assim, a verificação foi feita e o relatório de qualidade ficou registrado, e as regras continuam valendo para dados novos ou para dados reais da fábrica.

Sobre os valores fora do padrão: só a quantidade de lenha usada teve registros marcados (30 queimas). Todos são queimas de 18 mil telhas, que gastam mais lenha. Não é erro. Por isso, para comparar fornos, usamos a lenha por mil telhas, que não teve nenhum valor fora do padrão.

## 6. Variáveis criadas

| Variável | O que é |
| --- | --- |
| `telhas_boas` | Telhas produzidas menos as com defeito |
| `taxa_defeito_pct` | Percentual de telhas com defeito |
| `lenha_kg_por_hora` | Lenha usada por hora de queima |
| `lenha_kg_por_mil_telhas` | Lenha usada a cada mil telhas produzidas |
| `data_queima` e `mes_queima` | Dia e mês do início da queima |
| `queima_sobreposta` | Aviso de que o início da queima é antes do fim da queima anterior no mesmo forno |
| `arquivo_origem` | Nome do CSV de onde veio o registro |

As variáveis de validação (as que terminam em `_ok`) foram usadas só durante a limpeza e não ficam no CSV final.

## 7. Limitação encontrada

Ao conferir a consistência, percebemos que o simulador usa a hora em que ele roda como início da queima. Como geramos vários arquivos em sequência, os dados ficaram com apenas **3 horários de início diferentes**, e **600 das 624 queimas** começam antes de a queima anterior do mesmo forno terminar. Na fábrica real isso não acontece, porque um forno faz uma queima por vez.

O que fizemos com isso:

- Marcamos esses registros na coluna `queima_sobreposta` e mostramos a contagem no relatório de qualidade.
- **Não removemos** os registros, porque a quantidade de lenha, as temperaturas e os defeitos continuam válidos para análise.
- As análises por forno, tipo de lenha, tipo de forno e responsável funcionam normalmente. As análises por data ou por mês **não fazem sentido** com esses dados.

**Melhoria prevista:** ajustar o simulador para gerar as queimas em sequência no tempo, com cada forno começando só depois de terminar a anterior.

## 8. Primeiros resultados (exemplo de saída)

Estes números mostram que o pipeline já responde ao problema do projeto. Como os dados são simulados, eles servem como exemplo do tipo de resultado que a análise vai entregar.

| Pergunta | Resultado |
| --- | --- |
| Qual forno gastou mais lenha no total? | F006 (Caieira), cerca de 151,8 mil kg |
| Qual forno gastou menos lenha no total? | F012 (Túnel), cerca de 63,1 mil kg |
| Qual lenha teve maior consumo total? | Aroeira, cerca de 252 mil kg |
| Qual lenha gastou menos kg por mil telhas, em média? | Pinus (cerca de 151 kg), contra 161 kg da Aroeira |

O total de lenha de um forno depende de quantas telhas ele leva por queima, por isso a comparação justa entre fornos é feita pela lenha por mil telhas. As diferenças entre os tipos de lenha são pequenas nestes dados simulados.

## 9. Arquivos desta etapa

| Arquivo no repositório | O que é |
| --- | --- |
| `analise/limpeza_telhas.Rmd` | Notebook em R Markdown com todo o código da limpeza |
| `analise/complemento_limpeza_dados.md` | Este arquivo |
| `dados/telhas_queimas_limpo.csv` | CSV limpo (624 linhas e 22 colunas) |

Os 52 CSVs brutos não ficam no repositório. Eles são gerados pelo simulador e, por isso, podem ser refeitos quando necessário.

## 10. Ligação com o restante do pipeline

O caminho dos dados fica assim: o simulador na VM gera os CSVs, os CSVs são trazidos para o computador, o R faz a limpeza e a organização, e o resultado é o CSV limpo, pronto para a análise e para as próximas etapas do projeto.
