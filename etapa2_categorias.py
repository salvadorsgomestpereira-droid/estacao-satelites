"""
Etapa 2 - Muitos satelites, ordenados por altitude

Descarrega varias categorias de satelites do Celestrak e mostra uma
tabela com todos, ordenada da orbita mais baixa para a mais alta. Serve
para confirmar na pratica os "andares" de que falamos no chat: a ISS
perto dos 400 km, o GPS perto dos 20 200 km, e os geoestacionarios perto
dos 35 786 km.
"""

from skyfield.api import load, wgs84

# Cada "grupo" e uma categoria de satelites no Celestrak. O nome a
# direita e so para aparecer bonito na tabela.
CATEGORIAS = {
    "stations": "Estacao espacial",
    "weather": "Meteorologico",
    "gps-ops": "GPS",
    "geo": "Geoestacionario",
    "resource": "Observacao da Terra",
}

URL_BASE = "https://celestrak.org/NORAD/elements/gp.php?GROUP={grupo}&FORMAT=TLE"


def carregar_satelites():
    """Descarrega cada categoria e devolve uma lista de
    (nome_categoria, satelite) para todos os satelites encontrados."""
    todos = []
    for grupo, nome_categoria in CATEGORIAS.items():
        url = URL_BASE.format(grupo=grupo)
        # Por omissao, o Skyfield guarda a copia local usando so a parte
        # final do URL (aqui seria sempre "gp.php" para todas as
        # categorias, porque ignora o "?GROUP=..."). Isso fazia com que
        # todas as categorias reutilizassem o mesmo ficheiro por engano.
        # Ao indicar um nome proprio para cada grupo, cada categoria fica
        # com a sua propria copia local.
        satelites = load.tle_file(url, filename=f"tle_{grupo}.txt")
        for satelite in satelites:
            todos.append((nome_categoria, satelite))
    return todos


def main():
    satelites = carregar_satelites()
    ts = load.timescale()
    agora = ts.now()

    # Para cada satelite calculamos a altitude atual, tal como na Etapa 1,
    # e guardamos tudo numa lista de linhas da tabela.
    linhas = []
    for categoria, satelite in satelites:
        posicao = satelite.at(agora)
        ponto = wgs84.subpoint(posicao)
        linhas.append((categoria, satelite.name, ponto.elevation.km))

    # sorted() com key=... diz ao Python "ordena por este valor de cada
    # linha" - aqui, o terceiro elemento do tuplo (a altitude, indice 2).
    linhas.sort(key=lambda linha: linha[2])

    print(f"{'Categoria':<20} {'Satelite':<30} {'Altitude (km)':>15}")
    print("-" * 67)
    for categoria, nome, altitude_km in linhas:
        print(f"{categoria:<20} {nome:<30} {altitude_km:>15.1f}")

    print(f"\nTotal de satelites: {len(linhas)}")


if __name__ == "__main__":
    main()
