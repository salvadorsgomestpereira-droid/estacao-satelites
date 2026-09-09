"""
Etapa 3 - O que passa por cima de Vilamoura

Calcula, para o observador definido em config.py, quais os satelites que
estao acima do horizonte neste momento (com altura e azimute vistos
daqui), e preve as proximas passagens de cada satelite: nascer, ponto
mais alto (culminacao) e ocaso.
"""

import sys
from zoneinfo import ZoneInfo

from skyfield.api import load, wgs84

import config

# O terminal do Windows por vezes usa uma codificacao de texto antiga que
# nao conhece o simbolo de grau (deg) e mostra um "?" estranho em vez
# dele. Esta linha diz ao Python para escrever sempre em UTF-8, que
# suporta esse simbolo (e acentos, emojis, etc.).
sys.stdout.reconfigure(encoding="utf-8")

URL_BASE = "https://celestrak.org/NORAD/elements/gp.php?GROUP={grupo}&FORMAT=TLE"

# So contamos um satelite como "visivel" acima desta altura, em graus.
# Um pouco acima de 0 (o horizonte matematico) porque na pratica ha
# quase sempre arvores, casas ou montanhas a tapar a vista perto do chao.
ALTURA_MINIMA_GRAUS = 10.0

FUSO_HORARIO = ZoneInfo("Europe/Lisbon")


def carregar_satelites():
    todos = []
    for grupo, nome_categoria in config.CATEGORIAS.items():
        url = URL_BASE.format(grupo=grupo)
        satelites = load.tle_file(url, filename=f"tle_{grupo}.txt")
        for satelite in satelites:
            todos.append((nome_categoria, satelite))
    return todos


def criar_observador():
    # wgs84.latlon cria um ponto na superficie da Terra, usando o mesmo
    # modelo de elipsoide (WGS84) que ja usamos para o subponto dos
    # satelites. E a partir deste ponto que vamos medir altura e azimute.
    return wgs84.latlon(
        config.OBSERVADOR_LATITUDE,
        config.OBSERVADOR_LONGITUDE,
        elevation_m=config.OBSERVADOR_ALTITUDE_M,
    )


def mostrar_horizonte_agora(satelites, observador, ts):
    agora = ts.now()
    visiveis = []

    for categoria, satelite in satelites:
        # "satelite - observador" cria a posicao relativa entre os dois -
        # e e essa posicao relativa que da a altura e o azimute vistos de
        # Vilamoura, em vez da posicao geografica absoluta do satelite.
        diferenca = satelite - observador
        topocentrica = diferenca.at(agora)
        altura, azimute, distancia = topocentrica.altaz()

        if altura.degrees >= ALTURA_MINIMA_GRAUS:
            visiveis.append(
                (categoria, satelite.name, altura.degrees, azimute.degrees, distancia.km)
            )

    # Do mais alto no ceu para o mais baixo.
    visiveis.sort(key=lambda linha: linha[2], reverse=True)

    print("=" * 85)
    print("SATELITES ACIMA DO HORIZONTE AGORA (Vilamoura)")
    print("=" * 85)

    if not visiveis:
        print(f"Nenhum satelite acima de {ALTURA_MINIMA_GRAUS:.0f} graus neste momento.")
        return

    print(f"{'Categoria':<20} {'Satelite':<28} {'Altura':>8} {'Azimute':>9} {'Distancia (km)':>16}")
    print("-" * 85)
    for categoria, nome, altura_graus, azimute_graus, distancia_km in visiveis:
        print(
            f"{categoria:<20} {nome:<28} {altura_graus:>7.1f}° "
            f"{azimute_graus:>8.1f}° {distancia_km:>16.1f}"
        )


def mostrar_proximas_passagens(satelites, observador, ts, horas=6):
    agora = ts.now()
    # As Time do Skyfield somam-se em dias, por isso dividimos as horas por 24.
    daqui_a_umas_horas = agora + horas / 24

    print()
    print("=" * 85)
    print(f"PROXIMAS PASSAGENS NAS PROXIMAS {horas} HORAS (acima de {ALTURA_MINIMA_GRAUS:.0f} graus)")
    print("=" * 85)

    nomes_eventos = ["nasce", "culmina", "poe-se"]
    encontrou_alguma = False

    for categoria, satelite in satelites:
        diferenca = satelite - observador

        # find_events percorre o intervalo de tempo e encontra os instantes
        # exatos em que a altura do satelite cruza ALTURA_MINIMA_GRAUS a
        # subir (nasce), atinge o maximo local (culmina), ou cruza a descer
        # (poe-se).
        tempos, eventos = satelite.find_events(
            observador, agora, daqui_a_umas_horas, altitude_degrees=ALTURA_MINIMA_GRAUS
        )

        if len(tempos) == 0:
            continue

        encontrou_alguma = True
        print(f"\n{satelite.name} ({categoria})")
        for tempo, evento in zip(tempos, eventos):
            altura, azimute, _ = diferenca.at(tempo).altaz()
            hora_local = tempo.utc_datetime().astimezone(FUSO_HORARIO)
            print(
                f"  {hora_local.strftime('%H:%M:%S')}  {nomes_eventos[evento]:<8} "
                f"altura {altura.degrees:5.1f}°  azimute {azimute.degrees:5.1f}°"
            )

    if not encontrou_alguma:
        print("Nenhuma passagem prevista neste intervalo.")


def main():
    print("A descarregar TLE...")
    satelites = carregar_satelites()
    observador = criar_observador()
    ts = load.timescale()

    mostrar_horizonte_agora(satelites, observador, ts)
    mostrar_proximas_passagens(satelites, observador, ts)


if __name__ == "__main__":
    main()
