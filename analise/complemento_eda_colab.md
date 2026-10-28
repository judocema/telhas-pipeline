# Complemento – EDA no Google Colab (Python)

**Projeto Integrado – Big Data** | Fábrica de telhas de barro
**Tema:** Automação e Escalabilidade de Pipelines de Big Data e Análise de Dados
**Equipe:** Julia Docema de Carvalho e Julia Fernandes de Ovidio
**Etapa:** Etapa 2 – Análise Exploratória de Dados (EDA) no Google Colab

Este arquivo complementa o notebook `EDA_telhas_queimas.ipynb`. Aqui explicamos **por que** usamos cada biblioteca, cada comando e cada gráfico, e o que cada um mostrou sobre o problema do projeto.

## 1. Objetivo da etapa

As orientações da disciplina pedem que a EDA tenha: carregamento dos dados, identificação de tipos, ausentes e duplicados, estatística descritiva, gráficos adequados ao tipo de variável e interpretação de cada gráfico.

O problema do projeto é a **falta de controle sobre a queima de lenha em cada forno**. Por isso, a pergunta da EDA foi: **o que faz o consumo de lenha mudar de uma queima para outra?** Olhamos o tamanho do forno, o tipo de lenha, o tipo de forno, o tempo e a temperatura.

## 2. Base usada

| Item | Valor |
| --- | --- |
| Arquivo | `telhas_queimas_limpo.csv` (pasta `dados` do repositório) |
| Origem | Simulador de dados na VM, depois limpo no RStudio |
| Registros | 624 queimas (12 fornos, 52 queimas por forno) |
| Colunas | 22 (14 originais, mais as criadas na limpeza) |

A limpeza já foi feita no R e está explicada em `complemento_limpeza_dados.md`. Por isso, **no Colab não repetimos** a validação dos valores, as checagens de consistência nem a criação das variáveis (`telhas_boas`, `taxa_defeito_pct`, `lenha_kg_por_hora` e `lenha_kg_por_mil_telhas`). Repetir isso só duplicaria o trabalho.

## 3. Por que Google Colab, Python e estas bibliotecas

O Colab foi pedido nas orientações da disciplina. Ele roda Python no navegador, já vem com as bibliotecas instaladas e deixa o código, os gráficos e os textos de interpretação no mesmo arquivo.

| Biblioteca | Para que serve | Por que usamos |
| --- | --- | --- |
| `pandas` | Ler e organizar tabelas (`DataFrame`) | É a base da análise: lê o CSV, filtra, agrupa e calcula |
| `numpy` | Contas com números | Fica disponível para cálculos, como nas aulas |
| `matplotlib` | Gráficos básicos | Controla título, eixos, tamanho e exibição dos gráficos |
| `seaborn` | Gráficos estatísticos mais bonitos | Faz boxplot, mapa de calor e densidade com poucas linhas |

Usamos as mesmas funções do notebook de EDA visto em aula. As únicas coisas fora da aula são `to_datetime`, `groupby` com `agg` e `sort_values`, que também são do pandas e foram necessárias para converter datas e montar as tabelas-resumo.

## 4. Por que cada comando

| Comando | Para que serve | Por que usamos aqui |
| --- | --- | --- |
| `drive.mount()` | Conecta o Colab ao Google Drive | O CSV fica na pasta `Big_Data` do Drive, como nas aulas |
| `pd.read_csv()` | Lê o CSV e cria o `df` | É o primeiro passo de toda a análise |
| `df.head()` | Mostra as primeiras linhas | Conferir se o arquivo carregou certo |
| `df.shape` | Mostra (linhas, colunas) | Confirmar 624 linhas e 22 colunas, o mesmo do R |
| `df.info()` | Mostra o tipo de cada coluna | Identificar os tipos de variável, que é um item pedido nas orientações |
| `pd.to_datetime()` | Converte texto em data e hora | O CSV guarda as datas como texto, e sem converter não dá para fazer contas com datas |
| `df.isnull().sum()` | Conta valores nulos por coluna | Confirmar que o CSV chegou sem ausentes |
| `df.duplicated().sum()` | Conta linhas repetidas | Confirmar que não há duplicados |
| `df.describe()` | Resumo estatístico (média, desvio, quartis, mínimo e máximo) | É a estatística descritiva pedida nas orientações |
| `.round(2)` | Arredonda os números | Deixar a tabela fácil de ler |
| `value_counts()` | Conta quantas vezes cada categoria aparece | Variáveis de categoria não têm média, então contamos |
| `nunique()` | Conta valores diferentes | Descobrir que só existem 3 horários de início |
| `groupby().agg()` | Agrupa e calcula totais e médias | Responde ao problema: quanto cada forno e cada lenha consomem |
| `sort_values()` | Ordena a tabela | Mostrar primeiro o que mais gasta ou o que mais rende |
| `pd.crosstab()` | Tabela cruzada de duas categorias | Ver se todo tipo de forno usa todo tipo de lenha |
| `df.corr()` | Correlação entre variáveis numéricas | Descobrir quais variáveis andam juntas |

Duas observações sobre as escolhas:

- Usamos `df.info()` e `df.head()` com parênteses, para o resultado sair como tabela.
- Deixamos a `quantidade_telhas_produzidas` fora da estatística descritiva e do mapa de calor, porque nos dados do simulador ela é sempre igual à `quantidade_telhas_no_forno`. Repetir não traz informação nova.

## 5. Por que cada gráfico

Escolhemos o gráfico conforme o **tipo da variável**, como pedem as orientações.

| Gráfico | Tipo de variável | Pergunta que responde | O que mostrou |
| --- | --- | --- | --- |
| Contagem (`countplot`) por tipo de lenha | Categoria | Alguma lenha é muito mais usada que as outras? | Não. Vai de 116 a 139 queimas por lenha |
| Contagem por tipo de forno | Categoria | Quantas queimas cada tipo de forno tem? | Intermitente 260, Túnel 208 e Caieira 156, porque a fábrica tem 5, 4 e 3 fornos de cada tipo |
| Histograma (`hist`) da lenha | Número contínuo | Como a lenha por queima se distribui? | Concentra-se entre 1.000 e 1.700 kg, com cauda até cerca de 4.000 kg |
| Densidade (`kdeplot`) da lenha por mil telhas | Número contínuo | Como o gasto por mil telhas se espalha? | Vai de 90 a 220 kg e não tem um pico claro |
| Boxplot da lenha por tamanho da carga | Número x categoria | O tamanho do forno muda a lenha? | Sim. A mediana vai de cerca de 1.260 kg (8 mil telhas) a 2.890 kg (18 mil) |
| Boxplot da lenha por mil telhas, por tipo de lenha | Número x categoria | Alguma lenha rende mais? | Diferença pequena (151 a 161 kg), com as caixas quase sobrepostas |
| Boxplot da lenha por mil telhas, por tipo de forno | Número x categoria | O tipo de forno muda o consumo? | Não. As médias são 154,7, 155,4 e 155,7 kg |
| Barras (`barplot`) da média por forno | Número x categoria | Algum forno se destaca? | Não. As médias vão de 148 a 163 kg e as barras de incerteza se sobrepõem |
| Mapa de calor (`heatmap`) das correlações | Vários números | Quais variáveis andam juntas? | Lenha x telhas no forno: 0,83. Lenha x tempo e lenha x temperatura: 0,00 |
| Dispersão (`scatterplot`) tempo x lenha | Número x número | Queima mais longa gasta mais lenha? | Não. Os pontos formam uma nuvem sem direção |
| Dispersão temperatura x taxa de defeito | Número x número | A temperatura explica os defeitos? | Não. Há defeitos de 0,5% a 12% em todas as temperaturas |
| Barras da taxa de defeito por lenha | Número x categoria | Alguma lenha causa mais defeito? | Diferença de menos de 1 ponto percentual, sem destaque |

**Por que o boxplot para comparar grupos:** ele mostra mediana, variação e valores fora do padrão de uma vez, e permite comparar vários grupos lado a lado. Marcamos a média (`showmeans=True`) para ver se ela se afasta da mediana.

**Por que o mapa de calor:** com 8 variáveis numéricas, olhar todos os pares um por um seria demorado. O mapa mostra todas as correlações numa figura só, e as cores ajudam a achar as fortes.

**Por que dispersão em vez de correlação só:** a correlação resume tudo em um número. O gráfico de pontos confirma se a relação realmente não existe ou se é só um número baixo por causa de algum valor estranho.

## 6. Decisões tomadas

1. **Comparar por lenha por mil telhas:** os fornos têm tamanhos diferentes (8, 10, 12 e 18 mil telhas por queima). O total de lenha de um forno depende do tamanho dele, então a comparação justa é a lenha por mil telhas.
2. **Não remover valores fora do padrão:** as 30 queimas com lenha alta são todas de fornos de 18 mil telhas, que gastam mais lenha. Não é erro.
3. **Não fazer análise por data:** só existem 3 horários de início diferentes (explicado na seção 8).
4. **Manter o intervalo de incerteza nas barras:** o `barplot` do seaborn já mostra a linha de incerteza da média, e ela ajuda a não concluir diferenças que na verdade são pequenas.
5. **Não tirar conclusão onde a diferença é pequena:** em tipo de lenha, tipo de forno e forno, as diferenças ficam dentro da variação normal das queimas. Escrevemos isso nas interpretações, em vez de apontar um "melhor".

## 7. Principais resultados

| Resultado | Valor |
| --- | --- |
| Lenha média por queima | 1.769 kg (mediana 1.555 kg) |
| Lenha média por mil telhas | 155 kg (de 90 a 220 kg) |
| Taxa média de defeito | cerca de 6% (de 0,55% a 11,9%) |
| Forno que mais gastou lenha no total | F006 (Caieira), cerca de 151,8 mil kg |
| Forno que menos gastou lenha no total | F012 (Túnel), cerca de 63,1 mil kg |
| Lenha com maior consumo total | Aroeira, cerca de 252 mil kg (também tem mais queimas) |
| Lenha com menor consumo por mil telhas | Pinus, 150,7 kg (contra 160,9 kg da Aroeira) |
| Queimas entre 200 e 220 kg por mil telhas | 85 (cerca de 14%) |

**Insight principal:** o total de lenha depende do tamanho do forno, mas o **mesmo forno** gasta de cerca de 90 a 220 kg por mil telhas de uma queima para outra. Algumas queimas gastam mais que o dobro de lenha que outras para a mesma quantidade de telhas. É nessa variação que está a oportunidade de controle, que é o problema que escolhemos resolver.

## 8. Limitações

- **Dados simulados:** tempo e temperatura não têm relação com a lenha, o que seria esperado numa queima real. Esse resultado vem do simulador e não deve ser lido como regra da fábrica.
- **Datas:** o simulador usa a hora em que roda como início da queima. Os dados têm só 3 horários de início, e 600 das 624 queimas aparecem como sobrepostas no mesmo forno. Por isso não analisamos tendência por data ou mês.
- **Carga fixa por forno:** cada forno sempre leva a mesma quantidade de telhas, e as telhas produzidas são sempre iguais às que entraram no forno.
- **Volume pequeno:** são 624 registros, base acadêmica. A mesma estrutura de análise pode ser aplicada a volumes maiores.

## 9. Relação com as orientações da disciplina

| Item pedido na EDA | Onde está no notebook |
| --- | --- |
| Carregar os dados com Python e pandas | Seção 1 |
| Identificar tipos, ausentes e duplicados | Seção 2 |
| Documentar as decisões de limpeza | Texto "Decisões de limpeza" na seção 2 |
| Estatística descritiva | Seção 3 |
| Visualizações adequadas ao tipo de variável | Seção 4 |
| Interpretação de cada gráfico | Texto abaixo de cada gráfico |
| Tabelas-resumo ligadas ao problema | Seção 5 |
| Insights, limitações e próximos passos | Seção 6 |

## 10. Próximos passos

- Ajustar o simulador para gerar as queimas em sequência no tempo, com cada forno começando só depois de terminar a anterior. Isso permite analisar por data.
- Montar o armazenamento, o ETL e as operações OLAP (Etapa 3).
- Aplicar um modelo de Machine Learning, por exemplo regressão para estimar a lenha de uma queima (Etapa 4).
- Avaliar se Hadoop ou Spark se justificam pelo volume (Etapa 5).

## 11. Arquivos desta etapa

| Arquivo | O que é |
| --- | --- |
| `analise/EDA_telhas_queimas.ipynb` | Notebook da EDA no Colab |
| `analise/complemento_eda_colab.md` | Este arquivo |
| `dados/telhas_queimas_limpo.csv` | Base usada na EDA |
