"""
Configuracao da estacao de rastreio.

Separado num ficheiro proprio para ser facil mudar o observador (ou as
categorias de satelites) sem mexer no resto do codigo.
"""

# Se True, o sistema nunca tenta ligar-se a internet: usa sempre os TLE
# de reserva guardados na pasta reserva/. Serve para poder apresentar o
# projeto na aula mesmo que o Wi-Fi da escola falhe.
MODO_DEMONSTRACAO = False

# Satelites so contam como "acima do horizonte" a partir desta altura,
# em graus. Um pouco acima de 0 (o horizonte matematico) porque na
# pratica ha quase sempre arvores, casas ou montanhas a tapar a vista
# perto do chao.
ALTURA_MINIMA_GRAUS = 10.0

# Coordenadas do observador: Vilamoura, Algarve, Portugal.
OBSERVADOR_LATITUDE = 37.08   # graus norte (positivo = hemisferio norte)
OBSERVADOR_LONGITUDE = -8.12  # graus este (negativo = a oeste do meridiano de Greenwich)
OBSERVADOR_ALTITUDE_M = 10    # metros acima do nivel do mar

# Categorias de satelites a descarregar do Celestrak, e o nome bonito de
# cada uma para mostrar na interface. Usado nas Etapas 2 e 3.
CATEGORIAS = {
    "stations": "Estacao espacial",
    "weather": "Meteorologico",
    "gps-ops": "GPS",
    "geo": "Geoestacionario",
    "resource": "Observacao da Terra",
}
