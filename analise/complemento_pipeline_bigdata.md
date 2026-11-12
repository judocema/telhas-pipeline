# Complemento – Big Data, Machine Learning e Estatística

**Projeto Integrado – Data Science** | Fábrica de telhas de barro
**Equipe:** Julia Docema de Carvalho e Julia Fernandes de Ovidio
**Arquivo da etapa:** `analise/EDA_telhas_queimas.ipynb` (seções 6 a 12)

## 1. Ligação com o problema

Cada etapa ajuda a responder: *quanto de lenha uma queima deveria gastar e quais queimas gastaram demais?*

| Etapa | Como ajuda |
| --- | --- |
| Data Warehouse e ETL | Guardam o histórico de queimas organizado para consulta |
| OLAP e Data Mining | Mostram o consumo por forno, lenha, tipo de forno e responsável |
| Machine Learning | Estima a lenha esperada de cada queima para achar excessos |
| Hadoop e Spark | Mostram como o mesmo cálculo escala com mais dados |
| Probabilidade e Estatística | Confirmam se as diferenças vistas são reais ou acaso |

**5 Vs no projeto:** Volume (624 queimas, crescendo a cada execução), Velocidade (um arquivo novo a cada rodada do simulador), Variedade (12 fornos, 3 tipos de forno, 5 lenhas, 10 responsáveis), Veracidade (verificada na limpeza em R) e Valor (controle da lenha).

## 2. Arquitetura: Data Warehouse

Usamos só o **Data Warehouse (SQLite)**, porque os dados são estruturados (colunas fixas) e já chegam limpos do R. O DW em esquema estrela deixa as consultas simples e serve o OLAP e o Machine Learning. O resultado do Spark também é gravado nele. Um Data Lake só seria necessário com dados sem formato fixo, como leituras de sensores ou fotos.

**ETL:** Extract (ler o CSV limpo), Transform (dimensões com `drop_duplicates` e chave `sk_`, e tabela fato) e Load (`to_sql` e conferência das linhas).

| Tabela | Tipo | Linhas |
| --- | --- | --- |
| `fato_queima` | Fato (medidas de cada queima) | 624 |
| `dim_forno` | Forno, tipo e capacidade | 12 |
| `dim_lenha` | Tipo de lenha | 5 |
| `dim_responsavel` | Responsável | 10 |
| `dim_tempo` | Dia da queima | 2 |
| `ind_por_forno` | Indicadores calculados no Spark | 12 |

## 3. OLAP e Data Mining

O cubo é a view `vw_cubo`, que junta a fato com as dimensões.

| Operação | Exemplo | Resultado |
| --- | --- | --- |
| Roll-up | Forno → tipo de forno | 154,7 a 155,7 kg por mil telhas |
| Drill-down | Tipo de forno → forno | 148,1 (F010) a 163,1 kg (F011) |
| Slice | Só Forno Túnel | Pinus 149,0 kg e Aroeira 162,1 kg |
| Dice | Túnel e Caieira x Pinus e Aroeira | O mesmo padrão nos dois fornos |
| Pivot | Tipo de forno x tipo de lenha (mapa de calor) | Médias todas na mesma faixa |

Também foram feitos o **cubo 3D** (tipo de forno x lenha x responsável, 146 combinações), o **gráfico 2D** e o **gráfico interativo**. Nenhuma dimensão sozinha explica o gasto.

**Data Mining:** queimas de **alerta** (acima de 200 kg por mil telhas) são 84 de 624 (13,5%).

## 4. Machine Learning

| Item | Escolha |
| --- | --- |
| Tarefa | Regressão (prever kg de lenha) |
| Algoritmo | Random Forest Regressor, em `Pipeline` com `StandardScaler` e `OneHotEncoder` |
| Variáveis | Tempo, temperatura, telhas no forno, tipo de forno e tipo de lenha |
| Fora do modelo | Variáveis calculadas a partir da lenha (entregariam a resposta), forno e responsável |
| Divisão | 80% treino e 20% teste (`random_state=42`) |

| Métrica (125 queimas de teste) | Valor |
| --- | --- |
| MAE | 364 kg (contra 663 kg chutando a média) |
| RMSE | 468 kg |
| R² | 0,70 |

A variável mais importante é a quantidade de telhas no forno (cerca de 0,69). O erro fica entre 18% e 22% em todos os tamanhos de carga. **Uso:** a diferença entre a lenha real e a prevista lista as queimas com excesso (até 58% acima do esperado), que seriam investigadas na fábrica.

## 5. Hadoop e Spark

**Hadoop:** com 624 linhas, um cluster não se justifica, então os componentes foram simulados em Python, como na aula. O **MapReduce** (mapper, shuffle e reducer) calculou a lenha total e média por tipo de forno, e o **YARN** simulado executou um job de lenha por mil telhas. O papel do **HDFS** e um exemplo de tabela no **Hive** estão descritos no notebook. O resultado confere com o pandas.

**Spark:** em modo local, com DataFrames (`select`, `filter`, `groupBy`/`agg`, `orderBy`) e Spark SQL (`createOrReplaceTempView`). Encontrou as mesmas 84 queimas em alerta e os indicadores por forno, gravados no DW (`ind_por_forno`). O resultado confere com o pandas. Com mais dados, o mesmo código rodaria em cluster com YARN, mudando só a configuração da sessão.

## 6. Probabilidade e Estatística

| Conteúdo | Resultado |
| --- | --- |
| Posição e dispersão | Lenha por mil telhas: média 155,2 e mediana 157,5 kg; CV de 23,7% (contra 45% da lenha total) |
| Frequência | Distribuição quase plana; 13,5% das queimas entre 200 e 220 kg |
| Probabilidades | P(alerta) = 13,5%; P(alerta \| Túnel) = 15,9% |
| Regra de Bayes | P(Túnel \| alerta) = 39,3%, contra 33,3% de Túnel na base |
| Qui-quadrado | Alerta x tipo de forno p = 0,446; x tipo de lenha p = 0,354 (independentes) |
| Normalidade | Shapiro-Wilk p < 0,05: não é normal |
| IC 95% da média | 152,3 a 158,1 kg por mil telhas |
| ANOVA / Kruskal-Wallis | Lenha p = 0,20 / 0,19; forno p = 0,955 / 0,964 |
| Correlações | Telhas x lenha 0,83 (p ≈ 0); tempo e temperatura x lenha 0,00 |
| Anomalias | Nenhuma pelos critérios de escore z e boxplot |

**Conclusão:** o problema não está em queimas absurdas, e sim na variação do consumo. Uma em cada sete queimas passa de 200 kg por mil telhas, e nem o tipo de forno nem o de lenha explicam isso com significância estatística.
