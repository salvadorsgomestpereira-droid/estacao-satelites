"""
app.py - Servidor web da estacao de rastreio.

Mostra numa pagina (feita primeiro para telemovel) os satelites que
estao acima do horizonte em Vilamoura agora, e um separador com o
historico de passagens observadas. A pagina principal atualiza-se
sozinha de X em X segundos, indo buscar dados novos ao servidor.
"""

from flask import Flask, jsonify, render_template

import base_dados
import posicoes

app = Flask(__name__)

# Isto tem de correr sempre que o modulo e importado, nao so quando o
# ficheiro e corrido diretamente - em producao (Render) e o gunicorn
# que importa "app", nunca executa o "if __name__" mais abaixo. Sem
# esta linha aqui, as tabelas nunca eram criadas em producao e todos os
# pedidos a base de dados falhavam.
base_dados.criar_tabelas()


@app.route("/")
def pagina_principal():
    return render_template("index.html")


@app.route("/historico")
def pagina_historico():
    return render_template("historico.html")


@app.route("/api/visiveis")
def api_visiveis():
    # Isto vai ser demonstrado ao vivo a uma turma, provavelmente com
    # Wi-Fi fraco - por isso, se alguma coisa correr mal (por exemplo,
    # falha de rede sem nenhuma copia local de TLE), a pagina nunca deve
    # mostrar um erro feio. Devolvemos sempre uma resposta valida, e
    # avisamos o utilizador em vez de rebentar.
    try:
        visiveis, aviso = posicoes.calcular_visiveis()
        return jsonify({"ok": True, "satelites": visiveis, "aviso": aviso})
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
