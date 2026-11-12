# Complemento – Análise Exploratória de Dados (EDA) no Google Colab

**Projeto Integrado – Data Science** | Fábrica de telhas de barro
**Equipe:** Julia Docema de Carvalho e Julia Fernandes de Ovidio
**Arquivo da etapa:** `analise/EDA_telhas_queimas.ipynb` (seções 1 a 5)

## 1. Objetivo

Responder: **o que faz o consumo de lenha mudar de uma queima para outra?** Olhamos o tamanho do forno, o tipo de lenha, o tipo de forno, o tempo e a temperatura.

**Base:** `dados/telhas_queimas_limpo.csv`, com 624 queimas (52 por forno) e 22 colunas, já limpa no R. Por isso, no Colab só confirmamos que não há nulos nem duplicados e convertemos as datas.

## 2. Ferramentas

| Biblioteca | Uso |
| --- | --- |
| `pandas` | Ler o CSV, filtrar, agrupar e calcular (`read_csv`, `info`, `describe`, `value_counts`, `groupby`, `crosstab`, `corr`) |
| `numpy` | Cálculos numéricos |
| `matplotlib` e `seaborn` | Gráficos |

## 3. Gráficos e o que mostraram

Cada gráfico foi escolhido pelo tipo de variável.

| Gráfico | Pergunta | Resultado |
| --- | --- | --- |
| Contagem por tipo de lenha | Alguma lenha domina? | Não: de 116 a 139 queimas por lenha |
| Contagem por tipo de forno | Quantas queimas por tipo? | Intermitente 260, Túnel 208 e Caieira 156 (5, 4 e 3 fornos) |
| Histograma da lenha | Como a lenha se distribui? | 47% entre 1.000 e 1.700 kg, com cauda até cerca de 4.000 kg |
| Densidade da lenha por mil telhas | Como o gasto por telha se espalha? | De 90 a 220 kg, sem pico claro |
| Boxplot da lenha por carga | O tamanho do forno muda a lenha? | Sim: mediana de 1.260 kg (8 mil telhas) a 2.890 kg (18 mil) |
| Boxplot por tipo de lenha | Alguma lenha rende mais? | Diferença pequena: 151 (Pinus) a 161 kg (Aroeira) |
| Boxplot por tipo de forno | O tipo de forno muda o consumo? | Não: 154,7, 155,4 e 155,7 kg |
| Barras por forno | Algum forno se destaca? | Não: 148 (F010) a 163 kg (F011), com incertezas sobrepostas |
| Mapa de calor das correlações | Quais variáveis andam juntas? | Lenha x telhas no forno: 0,83; lenha x tempo e x temperatura: 0,00 |
| Barras de defeito por lenha | Alguma lenha causa mais defeito? | Não: 5,5% a 6,4% |

## 4. Decisões

1. **Comparar pela lenha por mil telhas**, porque os fornos têm tamanhos diferentes (8, 10, 12 e 18 mil telhas) e o total depende do tamanho.
2. **Manter os valores altos de lenha total**, porque são todos de fornos de 18 mil telhas e não são erro.
3. **Não analisar por data**, porque a base tem só 3 horários de início (limitação do simulador).
4. **Não apontar um "melhor"** onde a diferença fica dentro da variação normal das queimas.

## 5. Principais resultados

| Resultado | Valor |
| --- | --- |
| Lenha média por queima | 1.769 kg (mediana 1.555 kg) |
| Lenha média por mil telhas | 155 kg (de 90 a 220 kg) |
| Taxa média de defeito | cerca de 6% (de 0,55% a 11,9%) |
| Forno com maior / menor total de lenha | F006 (151,8 mil kg) / F012 (63,1 mil kg) |
| Lenha com menor / maior consumo por mil telhas | Pinus (150,7 kg) / Aroeira (160,9 kg) |

**Insight principal:** o mesmo forno gasta de cerca de 90 a 220 kg de lenha por mil telhas de uma queima para outra. É nessa variação que está a oportunidade de controle.
