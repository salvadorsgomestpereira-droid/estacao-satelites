"""
base_dados.py - Guarda em SQLite a informacao de cada satelite e o
historico de passagens observadas.

Usamos SQLite porque vem incluido no Python (nao e preciso instalar
nada) e guarda tudo num unico ficheiro (satelites.db) - nao e preciso
correr um servidor de base de dados a parte.
"""

import sqlite3
from pathlib import Path

CAMINHO_BD = Path("satelites.db")


def obter_ligacao():
    # timeout=10: se outro processo (por exemplo, o historico.py a
    # correr em segundo plano) estiver a escrever na base de dados
    # mesmo nesse instante, espera ate 10 segundos antes de desistir,
    # em vez de falhar logo com "database is locked".
    ligacao = sqlite3.connect(CAMINHO_BD, timeout=10)
    # Assim conseguimos aceder as colunas pelo nome (linha["nome"]) em
    # vez de so pela posicao (linha[0], linha[1], ...).
    ligacao.row_factory = sqlite3.Row
    return ligacao


def criar_tabelas():
    with obter_ligacao() as ligacao:
        ligacao.execute("""
            CREATE TABLE IF NOT EXISTS satelites (
                norad_id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                pais_operador TEXT,
                ano_lancamento INTEGER,
                tipo_objeto TEXT
            )
        """)
        ligacao.execute("""
            CREATE TABLE IF NOT EXISTS passagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                norad_id INTEGER,
                nome TEXT NOT NULL,
                inicio TEXT NOT NULL,
                altura_maxima REAL NOT NULL,
                duracao_segundos REAL NOT NULL
            )
        """)


def guardar_satelite(norad_id, nome, categoria, pais_operador, ano_lancamento, tipo_objeto):
    # INSERT ... ON CONFLICT: se o norad_id ja existir, atualiza a linha
    # em vez de dar erro por chave duplicada. Assim podemos correr isto
    # varias vezes (por exemplo, todos os dias) sem criar duplicados.
    with obter_ligacao() as ligacao:
        ligacao.execute("""
            INSERT INTO satelites (norad_id, nome, categoria, pais_operador, ano_lancamento, tipo_objeto)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(norad_id) DO UPDATE SET
                nome = excluded.nome,
                categoria = excluded.categoria,
                pais_operador = excluded.pais_operador,
                ano_lancamento = excluded.ano_lancamento,
                tipo_objeto = excluded.tipo_objeto
        """, (norad_id, nome, categoria, pais_operador, ano_lancamento, tipo_objeto))


def obter_toda_a_informacao():
    """Devolve um dicionario {norad_id: linha} com a informacao guardada
    de todos os satelites, para juntar rapidamente aos dados do TLE."""
    with obter_ligacao() as ligacao:
        linhas = ligacao.execute("SELECT * FROM satelites").fetchall()
    return {linha["norad_id"]: linha for linha in linhas}


def guardar_passagem(norad_id, nome, inicio, altura_maxima, duracao_segundos):
    with obter_ligacao() as ligacao:
        ligacao.execute("""
            INSERT INTO passagens (norad_id, nome, inicio, altura_maxima, duracao_segundos)
            VALUES (?, ?, ?, ?, ?)
        """, (norad_id, nome, inicio.isoformat(), altura_maxima, duracao_segundos))


def listar_passagens(limite=50):
    with obter_ligacao() as ligacao:
        linhas = ligacao.execute("""
            SELECT nome, inicio, altura_maxima, duracao_segundos
            FROM passagens
            ORDER BY inicio DESC
            LIMIT ?
        """, (limite,)).fetchall()
    return [dict(linha) for linha in linhas]
