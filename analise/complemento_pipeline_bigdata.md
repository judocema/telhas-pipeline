# Complemento – Pipeline de Big Data (DW, DL, ETL, OLAP, Machine Learning, Hadoop e Spark)

**Projeto Integrado – Data Science** | Fábrica de telhas de barro
**Tema:** Automação e Escalabilidade de Pipelines de Big Data e Análise de Dados
**Equipe:** Julia Docema de Carvalho e Julia Fernandes de Ovidio
**Etapa:** Arquitetura de dados, Data Mining, Machine Learning, processamento distribuído e Probabilidade e Estatística (Google Colab)

Este arquivo complementa o repositório. Depois da EDA, o professor pediu que o projeto mostrasse todo o fluxo de Big Data, e não só a parte estatística. Aqui explicamos o que foi adicionado ao notebook `EDA_telhas_queimas.ipynb` (seções 6 a 12) e por quê.

## 1. Problema e ligação com cada etapa

O problema é a **falta de controle sobre a queima de lenha em cada forno**. Cada etapa nova ajuda a responder a pergunta: *quanto de lenha uma queima deveria gastar e quais queimas gastaram demais?*

| Etapa | Como ajuda no problema |
| --- | --- |
| Data Lake e Data Warehouse | Guardam o histórico de queimas de forma organizada e rastreável |
| ETL e OLAP | Permitem olhar o consumo por forno, tipo de lenha, tipo de forno e responsável |
| Machine Learning | Estima a lenha esperada de cada queima, para achar excessos |
| Hadoop e Spark | Mostram como o mesmo cálculo escalaria quando houver muito mais dados |

## 2. Os 5 Vs de Big Data no projeto

| V | No projeto |
| --- | --- |
| Volume | 624 queimas (52 arquivos) na base acadêmica. Na fábrica real, os registros crescem todos os dias |
| Velocidade | O simulador gera um arquivo a cada rodada, como uma leitura contínua dos fornos |
| Variedade | 12 fornos, 3 tipos de forno, 5 tipos de lenha, 10 responsáveis. Hoje só CSV, mas poderia receber sensores e fotos |
| Veracidade | Verificada na limpeza em R. Limitação: o simulador sobrepõe queimas do mesmo forno |
| Valor | Controlar a lenha: saber o consumo esperado e achar os desvios |

## 3. Arquitetura escolhida: Data Lake e Data Warehouse integrados

| Escolha | Justificativa |
| --- | --- |
| **Data Warehouse** | Os dados são estruturados (tabela com colunas fixas) e a análise é por dimensões. O DW em esquema estrela deixa as consultas simples e rápidas |
| **Data Lake** | Guarda o histórico em arquivos, em três zonas, e é de onde o Spark e o Hadoop leem. Aceita dados novos de outros formatos sem mudar o DW |

**Zonas do Data Lake**

| Zona | Conteúdo |
| --- | --- |
| `raw` | CSVs como o simulador gerou (52 arquivos, 14 colunas) |
| `trusted` | CSV limpo e validado no R (624 linhas, 22 colunas) |
| `refined` | Resultados processados pelo Spark, em Parquet |

O DW foi feito com SQLite, por ser simples e já vir com o Python (usado na aula de DW e DL).

## 4. ETL

| Passo | O que foi feito |
| --- | --- |
| Extract | Leitura do CSV da zona `trusted` com `pd.read_csv` |
| Transform | Criação das dimensões com `drop_duplicates` e de uma chave numérica (`sk_`) para cada uma. Criação da tabela fato ligando as chaves às medidas |
| Load | Gravação das 5 tabelas no SQLite com `to_sql` e conferência da quantidade de linhas |

**Modelo dimensional (esquema estrela)**

| Tabela | Tipo | Linhas | Conteúdo |
| --- | --- | --- | --- |
| `fato_queima` | Fato | 624 | Uma linha por queima. Medidas: lenha, tempo, temperatura, telhas, defeitos e indicadores |
| `dim_forno` | Dimensão | 12 | Forno, tipo e capacidade de telhas |
| `dim_lenha` | Dimensão | 5 | Tipo de lenha |
| `dim_responsavel` | Dimensão | 10 | Responsável pela queima |
| `dim_tempo` | Dimensão | 2 | Dia da queima (só 2 dias, por causa da limitação do simulador) |

## 5. OLAP e Data Mining

O cubo OLAP é uma *view* do SQL (`vw_cubo`) que junta a fato com as dimensões. As operações feitas:

| Operação | Exemplo no projeto |
| --- | --- |
| Roll-up | Do forno para o tipo de forno |
| Drill-down | Do tipo de forno para cada forno |
| Slice | Só o Forno Túnel, por tipo de lenha |
| Dice | Túnel e Caieira, com Pinus e Aroeira |
| Pivot | Tipo de forno x tipo de lenha (mapa de calor) |

Também fizemos uma mineração simples: as queimas de **alerta** (acima de 200 kg de lenha por mil telhas). Foram 84 de 624 (13,5%).

**Resultado:** o tipo de forno quase não muda a média (de 154,7 a 155,7 kg por mil telhas). Entre os fornos a diferença é um pouco maior (de 148,1 a 163,1 kg). Os dados são simulados, então não tiramos conclusão sobre qual lenha ou forno é melhor.

## 6. Machine Learning

| Item | Escolha | Justificativa |
| --- | --- | --- |
| Tarefa | **Regressão** | Queremos prever um número (kg de lenha) e comparar com o gasto real |
| Algoritmo | **Random Forest Regressor** | Visto na aula de regressão, funciona com poucos dados, aceita relações que não são retas e mostra a importância das variáveis |
| Alvo | `quantidade_lenha_utilizada_kg` | É o que queremos controlar |
| Variáveis | Tempo, temperatura, telhas no forno, tipo de forno e tipo de lenha | Informações disponíveis antes de pesar a lenha |
| Fora do modelo | `lenha_kg_por_hora`, `lenha_kg_por_mil_telhas`, `id_forno` e responsável | As duas primeiras vêm da própria lenha (entregariam a resposta). As outras deixariam o modelo preso a fornos e pessoas específicos |
| Preparação | `StandardScaler` nos números e `OneHotEncoder` nos textos, dentro de um `Pipeline` | Mesmo padrão da aula |
| Divisão | 80% treino e 20% teste (`random_state=42`) | Avaliar em dados que o modelo não viu |

**Resultados no teste (125 queimas)**

| Métrica | Valor |
| --- | --- |
| MAE | 364 kg |
| RMSE | 469 kg |
| R² | 0,70 |
| MAE de quem chutasse sempre a média | 663 kg |

O modelo erra cerca de 45% menos que chutar a média. A variável mais importante é a quantidade de telhas no forno (cerca de 0,69 de importância), o que combina com a correlação de 0,83 da EDA. O erro fica entre 18% e 22% da lenha em todos os tamanhos de carga.

**Uso no problema:** a diferença entre a lenha real e a prevista aponta as queimas com excesso (as 10 maiores passam de 600 kg acima do esperado, a maior com 58% a mais). Esse é o relatório que a fábrica poderia usar para investigar.

**Por que não classificação ou agrupamento:** testamos, e a classificação de queimas em alerta teve recall muito baixo (cerca de 6%) com estes dados. A regressão da lenha por mil telhas também não funcionou (R² negativo), porque essa medida varia sem relação com as variáveis disponíveis. Por isso prevemos a lenha total, onde existe sinal.

## 7. Hadoop

| Componente | Papel no projeto | Como foi feito |
| --- | --- | --- |
| HDFS | Guardar as zonas raw e trusted do Data Lake em blocos, em várias máquinas | Descrito (conceitual) |
| MapReduce | Calcular lenha total e média por tipo de forno em etapas | Simulado em Python (mapper, shuffle e reducer), como na aula |
| YARN | Receber e controlar os jobs | Simulado com a função `enviar_job` da aula |
| Hive | Consultar os arquivos do HDFS com SQL | Exemplo de `CREATE EXTERNAL TABLE` no notebook (não executado) |

**Justificativa:** a base tem 624 linhas, e um cluster Hadoop não se justifica nesse volume. Mantivemos a simulação para mostrar o papel de cada componente e como o cálculo seria dividido. O resultado do MapReduce foi conferido contra o pandas e bateu.

## 8. Spark

Usamos **DataFrames** e **Spark SQL**, como pedem as orientações, em modo local (`local[*]`).

| Operação | Como foi feita |
| --- | --- |
| Leitura | `spark.read.csv(..., header=True, inferSchema=True)` da zona `trusted` |
| Seleção e filtro | `select` e `filter` (queimas acima de 200 kg por mil telhas: 84) |
| Agrupamento e indicadores | `groupBy` e `agg` por forno (queimas, lenha total, lenha por mil telhas e defeito médio) |
| Ordenação | `orderBy` |
| Spark SQL | `createOrReplaceTempView` e `spark.sql` para o consumo por tipo de lenha |
| Saída | Resultado gravado em Parquet na zona `refined` |

O resultado do Spark foi conferido contra o pandas e bateu.

**Como escalaria:** com mais dados, os arquivos iriam para o HDFS ou armazenamento em nuvem, o Spark rodaria em um cluster gerenciado pelo YARN e o código dos DataFrames e do Spark SQL continuaria o mesmo, mudando só a configuração da sessão.

## 9. Probabilidade e Estatística

A unidade de Probabilidade e Estatística pede medidas descritivas, distribuições de frequência, proporções, probabilidades e relações entre variáveis, para apoiar as interpretações. Isso está na seção 11 do notebook.

| Conteúdo | O que foi feito | Resultado principal |
| --- | --- | --- |
| Posição | Média, mediana, moda, mínimo, máximo e quartis | Lenha por mil telhas: média 155,2 e mediana 157,5 kg |
| Dispersão | Amplitude, variância, desvio-padrão, IQR, coeficiente de variação e assimetria | A lenha total varia muito (CV de 45%); a lenha por mil telhas varia menos (CV de 23,7%) |
| Frequência | Faixas de 20 kg, com frequência absoluta, relativa e acumulada | Distribuição quase plana; 13,5% das queimas ficam entre 200 e 220 kg |
| Proporções | Participação de cada tipo de forno e de lenha | Intermitente 41,7%, Túnel 33,3% e Caieira 25% |
| Probabilidades | Probabilidades empíricas e condicionais | P(alerta) = 13,5%; P(alerta \| Túnel) = 15,9% |
| Regra de Bayes | P(Túnel \| alerta) | 39,3%, contra 33,3% de Túnel na base |
| Independência | Qui-quadrado entre alerta e tipo de forno ou de lenha | p = 0,446 e 0,354: sem evidência de relação |
| Distribuição normal | Shapiro-Wilk e comparação com a curva normal | Não é normal; a normal subestima o alerta (11,2% contra 13,5%) |
| Intervalo de confiança | Média com 95% de confiança | 152,3 a 158,1 kg por mil telhas |
| Comparação de grupos | ANOVA e Kruskal-Wallis | p acima de 0,05 para lenha (0,20) e forno (0,955) |
| Relações | Correlação de Pearson e de Spearman, com p-valor | Telhas x lenha: 0,83; tempo e temperatura x lenha: 0,00 |
| Anomalias | Escore z, regra do boxplot e z dentro da mesma carga | Nenhuma anomalia; o risco está na variação grande |

**Conclusão para a empresa:** o problema não está em queimas absurdas, e sim na variação do consumo. Uma em cada sete queimas passa de 200 kg por mil telhas, e nem o tipo de forno nem o de lenha explicam isso com significância estatística.

## 10. Limitações

- **Dados simulados:** o pipeline funciona, mas os valores não representam a fábrica real. Tempo e temperatura não influenciam a lenha, o que não aconteceria em queimas reais.
- **Sobreposição de queimas:** 600 das 624 queimas se sobrepõem no mesmo forno. A dimensão de tempo do DW tem só 2 dias.
- **Volume pequeno:** o Hadoop foi simulado e o Spark rodou em modo local. O ganho de desempenho não aparece com este volume.
- **Modelo de ML:** usa uma única divisão treino/teste, sem validação cruzada.

## 11. Próximos passos

- Ajustar o simulador para gerar queimas em sequência no tempo e em maior volume.
- Treinar o modelo com dados reais da fábrica e testar outros algoritmos.
- Automatizar o pipeline para rodar a cada novo arquivo (tema do projeto: automação e escalabilidade).
- Testar o Spark em cluster e o Hive sobre o HDFS.

## 12. Arquivos desta etapa

| Arquivo no repositório | O que é |
| --- | --- |
| `analise/EDA_telhas_queimas.ipynb` | Notebook completo: EDA, Data Lake, DW, ETL, OLAP, ML, Hadoop e Spark |
| `analise/complemento_pipeline_bigdata.md` | Este arquivo |
| `analise/complemento_eda_colab.md` | Complemento da EDA (atualizado) |
| `dados/telhas_queimas_limpo.csv` | Base de entrada (zona trusted) |

O Data Lake e o Data Warehouse (pasta `/content/datalake`) são criados pelo próprio notebook ao rodar, por isso não ficam no repositório.
