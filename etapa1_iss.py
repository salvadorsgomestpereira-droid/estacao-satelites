"""
Etapa 1 - Onde esta a ISS agora?

Descarrega o TLE (ver explicacao no chat) da Estacao Espacial Internacional
a partir do Celestrak, e usa a biblioteca Skyfield para calcular a posicao
e a velocidade da ISS neste preciso instante.
"""

import math

from skyfield.api import load, wgs84

# Numero de catalogo NORAD da ISS. E o "numero de identificacao" do
# satelite - cada objeto rastreado tem um numero unico, e e assim que
# dizemos ao Celestrak qual satelite queremos.
NORAD_ISS = 25544

# O Celestrak tem um endereco que devolve o TLE de um satelite, se lhe
# dermos o numero de catalogo (CATNR) dele.
URL_TLE = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={NORAD_ISS}&FORMAT=TLE"


def main():
    # load.tle_file descarrega o TLE e guarda uma copia local em disco
    # (um ficheiro com o nome do URL, na mesma pasta do programa). Se essa
    # copia ja existir, o Skyfield usa-a em vez de voltar a descarregar -
    # isto evita bombardear o servidor do Celestrak sempre que corremos o
    # programa. Mais tarde vamos afinar esta regra para "so usar a copia
    # se tiver menos de 12 horas".
    satelites = load.tle_file(URL_TLE)
    iss = satelites[0]

    print(f"Satelite: {iss.name}")

    # O Skyfield usa a sua propria "escala de tempo" (ts) porque calcular
    # a posicao de um satelite exige ter em conta pequenas diferencas
    # entre varios tipos de tempo astronomico. Para ja, basta saber que
    # ts.now() nos da o instante atual.
    ts = load.timescale()
    agora = ts.now()

    # iss.at(agora) aplica o modelo SGP4 aos numeros do TLE e devolve a
    # posicao e a velocidade da ISS nesse instante.
    posicao = iss.at(agora)

    # wgs84 e o modelo matematico da forma da Terra (um elipsoide
    # ligeiramente achatado nos polos, nao uma esfera perfeita).
    # subpoint() converte a posicao da ISS no espaco para latitude,
    # longitude e altitude acima da superficie da Terra.
    ponto = wgs84.subpoint(posicao)

    latitude = ponto.latitude.degrees
    longitude = ponto.longitude.degrees
    altitude_km = ponto.elevation.km

    # A velocidade vem como um vetor com tres componentes (x, y, z), em
    # km por segundo. Para saber so "a quantos km/s vai", calculamos o
    # comprimento desse vetor com o teorema de Pitagoras em 3 dimensoes:
    # comprimento = raiz quadrada de (x^2 + y^2 + z^2).
    vx, vy, vz = posicao.velocity.km_per_s
    velocidade_km_s = math.sqrt(vx**2 + vy**2 + vz**2)

    print(f"Latitude:   {latitude:.2f} graus")
    print(f"Longitude:  {longitude:.2f} graus")
    print(f"Altitude:   {altitude_km:.1f} km")
    print(f"Velocidade: {velocidade_km_s:.2f} km/s")


if __name__ == "__main__":
    main()
