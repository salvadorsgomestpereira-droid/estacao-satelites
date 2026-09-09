"""
Etapa 6 - Historico de passagens

Corre em segundo plano, sem interface, e regista no SQLite todas as
passagens de satelites observadas: quando comecaram, a altura maxima
atingida, e quanto tempo duraram.

Funciona por sondagem (verificacao periodica): de X em X segundos,
verifica que satelites estao acima do horizonte agora. Sempre que um
satelite aparece pela primeira vez, comeca a "vigiar" essa passagem;
enquanto ele continua visivel, vai guardando a altura mais alta vista
ate agora; quando ele deixa de aparecer na lista, a passagem terminou e
grava-se tudo na base de dados.
"""

import sys
import time
from datetime import datetime, timezone

import base_dados
import posicoes

sys.stdout.reconfigure(encoding="utf-8")

INTERVALO_SEGUNDOS = 30


def um_ciclo(em_curso):
    """Faz uma verificacao: atualiza as passagens em curso e regista as
    que acabaram de terminar. Recebe e devolve o dicionario em_curso,
    que guarda o estado entre chamadas (norad_id -> dados da passagem)."""
    try:
        visiveis = posicoes.calcular_visiveis()
    except Exception as erro:
        print(f"Aviso: nao foi possivel calcular os satelites visiveis ({erro}). A tentar de novo no proximo ciclo.")
        return em_curso

    norad_ids_visiveis = {satelite["norad_id"] for satelite in visiveis}
    agora = datetime.now(timezone.utc)

    for satelite in visiveis:
        norad_id = satelite["norad_id"]
        if norad_id not in em_curso:
            em_curso[norad_id] = {
                "nome": satelite["nome"],
                "inicio": agora,
                "altura_maxima": satelite["altura_graus"],
            }
        else:
            em_curso[norad_id]["altura_maxima"] = max(
                em_curso[norad_id]["altura_maxima"], satelite["altura_graus"]
            )

    # Satelites que estavam a ser vigiados mas ja nao aparecem na lista
    # de visiveis: a passagem terminou.
    terminados = [norad_id for norad_id in em_curso if norad_id not in norad_ids_visiveis]
    for norad_id in terminados:
        passagem = em_curso.pop(norad_id)
        duracao_segundos = (agora - passagem["inicio"]).total_seconds()

        base_dados.guardar_passagem(
            norad_id, passagem["nome"], passagem["inicio"],
            passagem["altura_maxima"], duracao_segundos,
        )
        print(f"Passagem registada: {passagem['nome']} "
              f"(altura maxima {passagem['altura_maxima']:.1f} graus, "
              f"{duracao_segundos:.0f} segundos)")

    return em_curso


def main():
    base_dados.criar_tabelas()
    print(f"A vigiar passagens (verificacao a cada {INTERVALO_SEGUNDOS} segundos). Ctrl+C para parar.")

    em_curso = {}
    try:
        while True:
            em_curso = um_ciclo(em_curso)
            time.sleep(INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("\nParado.")


if __name__ == "__main__":
    main()
