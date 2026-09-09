"""
satcat.py - Liga cada satelite (pelo numero NORAD) a informacao sobre
ele: pais/operador, ano de lancamento e tipo de objeto.

Fonte: o "satcat" (catalogo de satelites) do Celestrak, um ficheiro CSV
com um resumo de todos os objetos catalogados desde o Sputnik 1. Cada
linha tem, entre outras colunas, o NORAD_CAT_ID - o mesmo numero que
identifica o satelite no TLE - e e por esse numero que cruzamos os dois
ficheiros.
"""

import csv
import io
import time
from pathlib import Path
from urllib.request import urlopen

import config

URL_SATCAT = "https://celestrak.org/pub/satcat.csv"
FICHEIRO_CACHE = Path("satcat_cache.csv")
FICHEIRO_RESERVA = Path("reserva") / "satcat_cache.csv"
IDADE_MAXIMA_SEGUNDOS = 12 * 60 * 60  # a mesma regra de 12 horas que usamos para os TLE

# Traducao dos codigos de pais/operador mais comuns que aparecem no
# satcat. Um satelite cujo codigo nao esteja aqui mostra so o codigo -
# a lista nao precisa de ser perfeita, so util.
PAISES_OPERADORES = {
    "US": "Estados Unidos",
    "CIS": "Russia / antiga URSS",
    "PRC": "China",
    "IND": "India",
    "JPN": "Japao",
    "ESA": "Agencia Espacial Europeia",
    "FR": "Franca",
    "UK": "Reino Unido",
    "GER": "Alemanha",
    "ITSO": "Intelsat (organizacao internacional)",
    "SES": "SES (Luxemburgo)",
    "EUTE": "Eutelsat (Franca)",
    "CA": "Canada",
    "IT": "Italia",
    "SPN": "Espanha",
    "BRAZ": "Brasil",
    "ISRA": "Israel",
    "SKOR": "Coreia do Sul",
    "NKOR": "Coreia do Norte",
    "IRAN": "Irao",
    "UAE": "Emirados Arabes Unidos",
    "LUXE": "Luxemburgo",
    "ARGN": "Argentina",
    "AUS": "Australia",
    "NETH": "Holanda",
    "IO": "Organizacao internacional",
    "PL": "Polonia",
}

TIPOS_OBJETO = {
    "PAY": "Satelite (carga util)",
    "R/B": "Parte de foguetao",
    "DEB": "Detrito espacial",
    "UNK": "Desconhecido",
}


def _ficheiro_esta_atualizado():
    if not FICHEIRO_CACHE.exists():
        return False
    idade_segundos = time.time() - FICHEIRO_CACHE.stat().st_mtime
    return idade_segundos < IDADE_MAXIMA_SEGUNDOS


def _descarregar():
    with urlopen(URL_SATCAT, timeout=30) as resposta:
        dados = resposta.read()
    FICHEIRO_CACHE.write_bytes(dados)


def _analisar(texto_csv):
    informacao = {}
    leitor = csv.DictReader(io.StringIO(texto_csv))
    for linha in leitor:
        texto_norad = linha["NORAD_CAT_ID"]
        if not texto_norad:
            continue

        codigo_pais = linha["OWNER"]
        ano_texto = linha["LAUNCH_DATE"][:4] if linha["LAUNCH_DATE"] else None
        tipo_objeto = linha["OBJECT_TYPE"]

        informacao[int(texto_norad)] = {
            "pais_operador": PAISES_OPERADORES.get(codigo_pais, codigo_pais),
            "ano_lancamento": int(ano_texto) if ano_texto else None,
            "tipo_objeto": TIPOS_OBJETO.get(tipo_objeto, tipo_objeto),
        }
    return informacao


def carregar_satcat():
    """Devolve um dicionario {norad_id: informacao} com todos os
    satelites do satcat."""
    if config.MODO_DEMONSTRACAO:
        return _analisar(FICHEIRO_RESERVA.read_text(encoding="utf-8"))

    if not _ficheiro_esta_atualizado():
        try:
            _descarregar()
        except Exception as erro:
            if FICHEIRO_CACHE.exists():
                print(f"Aviso: nao foi possivel atualizar o satcat ({erro}). "
                      "A usar a copia guardada, que pode estar desatualizada.")
            elif FICHEIRO_RESERVA.exists():
                print("Aviso: sem rede e sem copia local do satcat. A usar a copia de reserva.")
                return _analisar(FICHEIRO_RESERVA.read_text(encoding="utf-8"))
            else:
                raise

    return _analisar(FICHEIRO_CACHE.read_text(encoding="utf-8"))
