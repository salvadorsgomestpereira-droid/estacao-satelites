"""
tle.py - Descarrega e mantem em cache os TLE de todas as categorias de
satelites definidas em config.py.

Os TLE descrevem a orbita de um satelite num certo instante (a "epoca")
e vao ficando menos precisos com o tempo, por isso so voltamos a
descarregar um grupo se a copia local tiver mais de 12 horas. Se a rede
falhar, usamos a copia antiga na mesma, para o programa nunca parar so
por falta de internet.
"""

import time
from pathlib import Path

from skyfield.api import load, wgs84

import config

URL_BASE = "https://celestrak.org/NORAD/elements/gp.php?GROUP={grupo}&FORMAT=TLE"
IDADE_MAXIMA_SEGUNDOS = 12 * 60 * 60  # 12 horas
PASTA_RESERVA = Path("reserva")


def _nome_ficheiro(grupo):
    return Path(f"tle_{grupo}.txt")


def _ficheiro_esta_atualizado(caminho):
    if not caminho.exists():
        return False
    idade_segundos = time.time() - caminho.stat().st_mtime
    return idade_segundos < IDADE_MAXIMA_SEGUNDOS


def _carregar_grupo(grupo):
    caminho = _nome_ficheiro(grupo)
    url = URL_BASE.format(grupo=grupo)

    if config.MODO_DEMONSTRACAO:
        # Modo demonstracao: nunca tenta a rede, usa sempre a copia de
        # reserva guardada no repositorio. E o que garante que o sistema
        # funciona mesmo sem internet nenhuma, para apresentar na aula.
        caminho_reserva = PASTA_RESERVA / caminho.name
        return load.tle_file(str(caminho_reserva), reload=False)

    if _ficheiro_esta_atualizado(caminho):
        return load.tle_file(url, filename=str(caminho), reload=False)

    try:
        return load.tle_file(url, filename=str(caminho), reload=True)
    except Exception as erro:
        if caminho.exists():
            print(f"Aviso: sem rede para atualizar '{grupo}' ({erro}). "
                  "A usar a copia guardada, que pode estar desatualizada.")
            return load.tle_file(url, filename=str(caminho), reload=False)

        caminho_reserva = PASTA_RESERVA / caminho.name
        if caminho_reserva.exists():
            print(f"Aviso: sem rede e sem copia local para '{grupo}'. "
                  "A usar o TLE de reserva do repositorio (pode estar muito desatualizado).")
            return load.tle_file(str(caminho_reserva), reload=False)

        raise


def carregar_satelites():
    """Devolve uma lista de (nome_categoria, satelite) com todas as
    categorias definidas em config.CATEGORIAS."""
    todos = []
    for grupo, nome_categoria in config.CATEGORIAS.items():
        satelites = _carregar_grupo(grupo)
        for satelite in satelites:
            todos.append((nome_categoria, satelite))
    return todos


def criar_observador():
    # wgs84.latlon cria um ponto na superficie da Terra (modelo WGS84),
    # a partir do qual medimos altura e azimute dos satelites.
    return wgs84.latlon(
        config.OBSERVADOR_LATITUDE,
        config.OBSERVADOR_LONGITUDE,
        elevation_m=config.OBSERVADOR_ALTITUDE_M,
    )
