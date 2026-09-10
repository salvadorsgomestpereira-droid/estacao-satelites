"""
app.py - Servidor web da estacao de rastreio.

Mostra numa pagina (feita primeiro para telemovel) os satelites que
estao acima do horizonte em Vilamoura agora, e um separador com o
historico de passagens observadas. A pagina principal atualiza-se
sozinha de X em X segundos, indo buscar dados novos ao servidor.
"""

from flask import Flask, jsonify, render_template, request

import base_dados
import config
import etapa4_base_dados
import posicoes

app = Flask(__name__)

# Isto tem de correr sempre que o modulo e importado, nao so quando o
# ficheiro e corrido diretamente - em producao (Render) e o gunicorn
# que importa "app", nunca executa o "if __name__" mais abaixo. Sem
# esta linha aqui, as tabelas nunca eram criadas em producao e todos os
# pedidos a base de dados falhavam.
base_dados.criar_tabelas()

# Se a base de dados ainda nao tem nenhum satelite guardado (por
# exemplo, na primeira vez que o servidor arranca num alojamento novo,
# onde nunca correu a Etapa 4 a mao), populamo-la sozinhos agora. Isto
# usa o tle.py/satcat.py ja preparados para falhar depressa e cair para
# a copia de reserva, por isso nao bloqueia o arranque do servidor por
# muito tempo mesmo sem rede nenhuma.
if base_dados.total_satelites() == 0:
    print("Base de dados vazia - a popular pela primeira vez...")
    try:
        guardados, sem_info = etapa4_base_dados.popular_base_dados()
        print(f"Base de dados populada com {guardados} satelites.")
    except Exception as erro:
        print(f"Aviso: nao foi possivel popular a base de dados agora ({erro}). "
              "Pais/ano/tipo vao aparecer desconhecidos ate a proxima tentativa.")


@app.route("/")
def pagina_principal():
    return render_template("index.html")


@app.route("/historico")
def pagina_historico():
    return render_template("historico.html")


def _ler_coordenada(nome, minimo, maximo):
    # request.args.get(..., type=float) ja devolve None se o valor nao
    # vier no pedido ou nao for um numero valido. Se vier um numero fora
    # do intervalo possivel (por exemplo, uma latitude de 200 graus),
    # tratamos como se nao tivesse vindo nada, em vez de deixar o calculo
    # rebentar com coordenadas sem sentido.
    valor = request.args.get(nome, type=float)
    if valor is None or not (minimo <= valor <= maximo):
        return None
    return valor


@app.route("/api/visiveis")
def api_visiveis():
    # A pagina pede ao browser a localizacao de quem a esta a ver, e
    # manda-a aqui em ?lat=...&lon=.... Se nao vier nenhuma (o visitante
    # nao autorizou, ou o browser nao suporta), usamos Vilamoura.
    latitude = _ler_coordenada("lat", -90, 90)
    longitude = _ler_coordenada("lon", -180, 180)
    personalizado = latitude is not None and longitude is not None

    # Isto vai ser demonstrado ao vivo a uma turma, provavelmente com
    # Wi-Fi fraco - por isso, se alguma coisa correr mal (por exemplo,
    # falha de rede sem nenhuma copia local de TLE), a pagina nunca deve
    # mostrar um erro feio. Devolvemos sempre uma resposta valida, e
    # avisamos o utilizador em vez de rebentar.
    try:
        visiveis, aviso = posicoes.calcular_visiveis(latitude, longitude)
        return jsonify({
            "ok": True,
            "satelites": visiveis,
            "aviso": aviso,
            "observador": {
                "latitude": latitude if personalizado else config.OBSERVADOR_LATITUDE,
                "longitude": longitude if personalizado else config.OBSERVADOR_LONGITUDE,
                "personalizado": personalizado,
            },
        })
    except Exception as erro:
        return jsonify({"ok": False, "satelites": [], "aviso": str(erro)})


@app.route("/api/historico")
def api_historico():
    try:
        passagens = base_dados.listar_passagens(limite=100)
        return jsonify({"ok": True, "passagens": passagens})
    except Exception as erro:
        return jsonify({"ok": False, "passagens": [], "aviso": str(erro)})


if __name__ == "__main__":
    # host="0.0.0.0" permite abrir a pagina a partir de outro telemovel
    # na mesma rede Wi-Fi (usando o IP do portatil), nao so no proprio
    # computador.
    app.run(host="0.0.0.0", port=5000, debug=True)
