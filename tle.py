"""
tle.py - Descarrega e mantem em cache os TLE de todas as categorias de
satelites definidas em config.py.

Os TLE descrevem a orbita de um satelite num certo instante (a "epoca")
e vao ficando menos precisos com o tempo, por isso so voltamos a
descarregar um grupo se a copia local tiver mais de 12 horas. Se a rede
falhar (ou demorar demasiado), usamos a copia antiga na mesma, ou a
copia de reserva do repositorio, para o programa nunca parar so por
falta de internet.
"""

import time
from pathlib import Path
from urllib.request import urlopen

from skyfield.api import load, wgs84

import config

URL_BASE = "https://celestrak.org/NORAD/elements/gp.php?GROUP={grupo}&FORMAT=TLE"
IDADE_MAXIMA_SEGUNDOS = 12 * 60 * 60  # 12 horas

# Nao esperamos mais do que isto por uma resposta da rede. Sem um
# tempo-limite, se o servidor do Celestrak nao responder (por exemplo,
# visto de um servidor na internet como o Render, em vez do nosso
# computador), o programa podia ficar bloqueado indefinidamente à
# espera, em vez de usar os dados de reserva.
TEMPO_LIMITE_SEGUNDOS = 8

PASTA_RESERVA = Path("reserva")


def _nome_ficheiro(grupo):
    return Path(f"tle_{grupo}.txt")


def _ficheiro_esta_atualizado(caminho):
    if not caminho.exists():
        return False
    idade_segundos = time.time() - caminho.stat().st_mtime
    return idade_segundos < IDADE_MAXIMA_SEGUNDOS


def _descarregar(url, caminho):
    # Fazemos nos proprios o pedido de rede, em vez de deixar o Skyfield
    # fazê-lo por baixo dos panos, para podermos impor o tempo-limite
    # acima. urlopen faz o pedido HTTP e devolve os bytes da resposta;
    # so depois de os termos todos e que gravamos o ficheiro local.
    with urlopen(url, timeout=TEMPO_LIMITE_SEGUNDOS) as resposta:
        dados = resposta.read()
    caminho.write_bytes(dados)


def _carregar_grupo(grupo, rede_ja_falhou):
    """Devolve (satelites, aviso). "aviso" e None quando os dados estao
    dentro das 12 horas normais; caso contrario e um texto curto a
    explicar porque os dados podem nao estar atualizados.

    "rede_ja_falhou" vem de uma categoria anterior, no mesmo pedido: se
    a rede ja falhou uma vez agora mesmo, nao vale a pena esperar outra
    vez pelo tempo-limite para cada categoria seguinte, uma a seguir a
    outra - isso sozinho podia demorar minutos e fazer o servidor
    "morrer" por demorar demasiado tempo a responder."""
    caminho = _nome_ficheiro(grupo)
    caminho_reserva = PASTA_RESERVA / caminho.name

    if config.MODO_DEMONSTRACAO:
        # Modo demonstracao: nunca tenta a rede, usa sempre a copia de
        # reserva guardada no repositorio. E o que garante que o sistema
        # funciona mesmo sem internet nenhuma, para apresentar na aula.
        return load.tle_file(str(caminho_reserva), reload=False), "demonstracao"

    if _ficheiro_esta_atualizado(caminho):
        return load.tle_file(str(caminho), reload=False), None

    if not rede_ja_falhou:
        try:
            _descarregar(URL_BASE.format(grupo=grupo), caminho)
            return load.tle_file(str(caminho), reload=False), None
        except Exception as erro:
            print(f"Aviso: nao foi possivel atualizar o TLE de '{grupo}' ({erro}).")

    # A descarga falhou (ou nem foi tentada, porque uma categoria
    # anterior ja tinha falhado). Se existir um ficheiro local antigo,
    # usamo-lo na mesma (mais vale um TLE com algumas horas do que
    # nenhum); senao, caimos para a copia de reserva do repositorio.
    if caminho.exists():
        try:
            return load.tle_file(str(caminho), reload=False), "rede"
        except Exception as erro:
            print(f"Aviso: a copia local de '{grupo}' esta corrompida ({erro}).")

    print(f"Aviso: sem copia local valida para '{grupo}'. A usar a copia de reserva.")
    return load.tle_file(str(caminho_reserva), reload=False), "rede"


def carregar_satelites():
    """Devolve (lista, aviso). "lista" tem um (nome_categoria, satelite)
    por satelite de todas as categorias definidas em config.CATEGORIAS.
    "aviso" e None se tudo veio de dados recentes, ou um texto em
    portugues pronto a mostrar na pagina se alguma categoria teve de
    usar dados desatualizados (por falha de rede) ou o modo de
    demonstracao."""
    todos = []
    razoes = set()
    rede_ja_falhou = False
    for grupo, nome_categoria in config.CATEGORIAS.items():
        satelites, razao = _carregar_grupo(grupo, rede_ja_falhou)
        if razao == "rede":
            rede_ja_falhou = True
        if razao:
            razoes.add(razao)
        for satelite in satelites:
            todos.append((nome_categoria, satelite))

    if not razoes:
        aviso = None
    elif "demonstracao" in razoes:
        aviso = "Modo de demonstracao: a mostrar dados de exemplo guardados no projeto, nao a posicao real atual."
    else:
        aviso = "Sem ligacao fiavel ao Celestrak: a mostrar os ultimos dados de orbita guardados, que podem estar desatualizados."

    return todos, aviso


def criar_observador():
    # wgs84.latlon cria um ponto na superficie da Terra (modelo WGS84),
    # a partir do qual medimos altura e azimute dos satelites.
    return wgs84.latlon(
        config.OBSERVADOR_LATITUDE,
        config.OBSERVADOR_LONGITUDE,
        elevation_m=config.OBSERVADOR_ALTITUDE_M,
    )
