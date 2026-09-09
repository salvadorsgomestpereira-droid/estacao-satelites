"""
posicoes.py - Calcula tudo o que interessa mostrar sobre cada satelite
que esta acima do horizonte agora: posicao, altura/azimute vistos de
Vilamoura, e a informacao guardada na base de dados (pais, ano, tipo).

Este modulo e usado tanto pela pagina web (app.py) como pelo registo de
historico (historico.py), para os dois nunca calcularem as coisas de
forma diferente uma da outra.
"""

import math

from skyfield.api import load, wgs84

import base_dados
import config
import tle


def calcular_visiveis():
    """Devolve uma lista de dicionarios, um por satelite acima do
    horizonte agora, ordenada do mais alto no ceu para o mais baixo."""
    satelites = tle.carregar_satelites()
    observador = tle.criar_observador()
    ts = load.timescale()
    agora = ts.now()

    info_bd = base_dados.obter_toda_a_informacao()

    visiveis = []
    for categoria, satelite in satelites:
        # "satelite - observador" da a posicao relativa entre os dois:
        # altura (angulo acima do horizonte) e azimute (direcao da
        # bussola), vistos especificamente de Vilamoura.
        diferenca = satelite - observador
        topocentrica = diferenca.at(agora)
        altura, azimute, distancia = topocentrica.altaz()

        if altura.degrees < config.ALTURA_MINIMA_GRAUS:
            continue

        # geocentrica.subpoint() da a posicao geografica absoluta (o
        # ponto da Terra mesmo por baixo do satelite), usada so para o
        # desenhar no mapa e para saber a que altitude voa.
        geocentrica = satelite.at(agora)
        subponto = wgs84.subpoint(geocentrica)

        vx, vy, vz = geocentrica.velocity.km_per_s
        velocidade_km_s = math.sqrt(vx**2 + vy**2 + vz**2)

        norad_id = satelite.model.satnum
        info = info_bd.get(norad_id)

        visiveis.append({
            "norad_id": norad_id,
            "nome": satelite.name,
            "categoria": categoria,
            "pais_operador": info["pais_operador"] if info else None,
            "ano_lancamento": info["ano_lancamento"] if info else None,
            "tipo_objeto": info["tipo_objeto"] if info else None,
            "altura_graus": altura.degrees,
            "azimute_graus": azimute.degrees,
            "distancia_km": distancia.km,
            "altitude_km": subponto.elevation.km,
            "velocidade_km_s": velocidade_km_s,
            "latitude": subponto.latitude.degrees,
            "longitude": subponto.longitude.degrees,
        })

    visiveis.sort(key=lambda satelite: satelite["altura_graus"], reverse=True)
    return visiveis
