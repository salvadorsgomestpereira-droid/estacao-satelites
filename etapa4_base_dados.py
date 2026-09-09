"""
Etapa 4 - Base de dados de informacao

Cruza os TLE (que dao a orbita) com o satcat (que da pais, ano de
lancamento e tipo de objeto), usando o numero de catalogo NORAD como
"chave" comum aos dois ficheiros, e guarda tudo em SQLite.
"""

import sys

import base_dados
import satcat
import tle

sys.stdout.reconfigure(encoding="utf-8")


def main():
    print("A descarregar TLE...")
    satelites = tle.carregar_satelites()

    print("A descarregar satcat...")
    info_satcat = satcat.carregar_satcat()

    base_dados.criar_tabelas()

    guardados = 0
    sem_info = 0
    for categoria, satelite in satelites:
        # O numero de catalogo NORAD esta guardado dentro do modelo
        # orbital que o Skyfield usa (satelite.model, vindo da
        # biblioteca sgp4) - e o mesmo numero que aparece na coluna
        # NORAD_CAT_ID do satcat.
        norad_id = satelite.model.satnum
        info = info_satcat.get(norad_id)

        if info is None:
            # Satelites muito recentes por vezes ainda nao aparecem no
            # satcat (que demora algum tempo a ser atualizado).
            # Guardamos na mesma, so sem essa informacao extra.
            sem_info += 1
            pais_operador, ano_lancamento, tipo_objeto = None, None, None
        else:
            pais_operador = info["pais_operador"]
            ano_lancamento = info["ano_lancamento"]
            tipo_objeto = info["tipo_objeto"]

        base_dados.guardar_satelite(
            norad_id, satelite.name, categoria, pais_operador, ano_lancamento, tipo_objeto
        )
        guardados += 1

    print(f"\nGuardados {guardados} satelites na base de dados "
          f"({sem_info} sem informacao correspondente no satcat).")

    with base_dados.obter_ligacao() as ligacao:
        linhas = ligacao.execute("""
            SELECT nome, categoria, pais_operador, ano_lancamento, tipo_objeto
            FROM satelites
            WHERE pais_operador IS NOT NULL
            ORDER BY RANDOM()
            LIMIT 10
        """).fetchall()

    print("\nExemplos guardados (aleatorios, para conferir):")
    for linha in linhas:
        print(f"  {linha['nome']:<30} {linha['categoria']:<20} "
              f"{str(linha['pais_operador']):<28} {linha['ano_lancamento']}  {linha['tipo_objeto']}")


if __name__ == "__main__":
    main()
