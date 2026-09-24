"""
Gerador de dados simulados - controle de queima de lenha nos fornos
Roda a cada 12h (via cron) e gera um CSV novo com um registro por forno.

Os campos seguem as tabelas reais da planilha do projeto (fornos,
queimas_fornos e producao_lotes), combinadas numa linha por queima.
"""

import csv
import random
import datetime
import os

# ---- Configuração ----
# Fornos cadastrados na planilha (aba "fornos"): id, tipo, capacidade (telhas)
FORNOS = [
    ('F001', 'Forno Intermitente', 8000),
    ('F002', 'Forno Túnel', 10000),
    ('F003', 'Forno Intermitente', 8000),
    ('F004', 'Forno Intermitente', 8000),
    ('F005', 'Forno Caieira', 8000),
    ('F006', 'Forno Caieira', 18000),
    ('F007', 'Forno Intermitente', 10000),
    ('F008', 'Forno Intermitente', 18000),
    ('F009', 'Forno Túnel', 18000),
    ('F010', 'Forno Caieira', 10000),
    ('F011', 'Forno Túnel', 12000),
    ('F012', 'Forno Túnel', 8000),
]

# Tipos de lenha usados nas compras (aba "compras_lenha")
TIPOS_LENHA = ['Eucalipto', 'Pinus', 'Aroeira', 'Angico', 'Resíduo de Madeira']

# Responsáveis pela queima que aparecem na aba "queimas_fornos"
RESPONSAVEIS = ['Rafael', 'Ravi Lucca', 'Amanda', 'Ana Beatriz', 'Eloá',
                 'Guilherme', 'Davi Miguel', 'Matheus', 'Caleb', 'Emanuel']

# Fornecedores de lenha que aparecem na aba "compras_lenha"
FORNECEDORES = ['Teixeira Fernandes S/A', 'da Cruz', 'Cassiano',
                 'da Conceição Montenegro - EI', 'Garcia S/A', 'Aparecida',
                 'Pastor - ME', 'Abreu', 'Sampaio Lima Ltda.',
                 'Carvalho Sousa S/A', 'Alves e Filhos', 'Alves S/A',
                 'Novais S.A.', 'Câmara', 'Ferreira', 'Nascimento', 'Pastor']

PASTA_SAIDA = os.environ.get(
    'PASTA_SAIDA',
    os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dados'))
)
_contador_id = 0


def _proximo_id(prefixo):
    global _contador_id
    _contador_id += 1
    agora = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{prefixo}{agora}{_contador_id:02d}"


def gerar_registro(forno):
    """Gera um registro de queima + produção para um forno (uma linha)."""
    id_forno, tipo_forno, capacidade = forno
    tipo_lenha = random.choice(TIPOS_LENHA)

    inicio = datetime.datetime.now()
    tempo_queima_horas = round(random.uniform(18, 72), 1)
    fim = inicio + datetime.timedelta(hours=tempo_queima_horas)

    quantidade_telhas_no_forno = capacidade
    kg_por_telha = round(random.uniform(0.09, 0.22), 4)
    quantidade_lenha_kg = round(quantidade_telhas_no_forno * kg_por_telha, 1)

    taxa_defeito = random.uniform(0.005, 0.12)
    quantidade_com_defeito = int(quantidade_telhas_no_forno * taxa_defeito)

    return {
        'id_queima': _proximo_id('Q'),
        'id_forno': id_forno,
        'tipo_forno': tipo_forno,
        'tipo_lenha_utilizada': tipo_lenha,
        'quantidade_lenha_utilizada_kg': quantidade_lenha_kg,
        'data_inicio_queima': inicio.strftime('%Y-%m-%d %H:%M'),
        'data_fim_queima': fim.strftime('%Y-%m-%d %H:%M'),
        'tempo_total_queima_horas': tempo_queima_horas,
        'temperatura_forno_c': random.randint(750, 980),
        'quantidade_telhas_no_forno': quantidade_telhas_no_forno,
        'responsavel_queima': random.choice(RESPONSAVEIS),
        'id_lote': _proximo_id('L'),
        'quantidade_telhas_produzidas': quantidade_telhas_no_forno,
        'quantidade_telhas_com_defeito': quantidade_com_defeito,
    }


def gerar_dados():
    """Gera um registro de queima para cada forno cadastrado."""
    return [gerar_registro(forno) for forno in FORNOS]


def gerar_compra():
    """Gera um registro de compra de lenha (aba 'compras_lenha')."""
    quantidade_m3 = round(random.uniform(5, 40), 2)
    preco_por_m3 = round(random.uniform(120, 220), 2)
    valor_pago = round(quantidade_m3 * preco_por_m3, 2)

    return {
        'id_compra': _proximo_id('C'),
        'data_compra': datetime.date.today().strftime('%Y-%m-%d'),
        'tipo_lenha': random.choice(TIPOS_LENHA),
        'fornecedor': random.choice(FORNECEDORES),
        'quantidade_comprada_m3': quantidade_m3,
        'valor_pago': valor_pago,
        'umidade_lenha_pct': round(random.uniform(12, 45), 1),
    }


def gerar_compras(quantidade=3):
    """Gera algumas compras de lenha nesta rodada (nem toda rodada tem compra)."""
    return [gerar_compra() for _ in range(quantidade)]


def salvar_csv(registros, pasta_saida=PASTA_SAIDA, prefixo='telhas'):
    """Salva os registros em um CSV com nome baseado no prefixo e na data/hora."""
    if not registros:
        print("Nada para salvar (lista vazia).")
        return None

    os.makedirs(pasta_saida, exist_ok=True)
    nome_arquivo = f"{prefixo}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    caminho = os.path.join(pasta_saida, nome_arquivo)

    campos = list(registros[0].keys())
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(registros)

    print(f"Arquivo gerado: {caminho}")
    return caminho


if __name__ == '__main__':
    # Queimas + produção: um registro por forno
    dados_queimas = gerar_dados()
    salvar_csv(dados_queimas, prefixo='telhas_queimas')

    # Compras de lenha: algumas compras nesta rodada
    dados_compras = gerar_compras(quantidade=random.randint(0, 4))
    if dados_compras:
        salvar_csv(dados_compras, prefixo='telhas_compras')
