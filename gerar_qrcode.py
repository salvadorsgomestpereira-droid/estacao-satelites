"""
Etapa 7 - Gerar o codigo QR

Depois de publicares a pagina num servico de alojamento gratuito (ver
README.md), corre este programa com o endereco final para gerar uma
imagem com um codigo QR que abre essa pagina. Serve como alternativa ao
sticker NFC - qualquer telemovel consegue ler um QR so com a camara.
"""

import sys

import qrcode


def main():
    if len(sys.argv) != 2:
        print("Uso: python gerar_qrcode.py https://o-teu-endereco.exemplo.com")
        sys.exit(1)

    url = sys.argv[1]

    # qrcode.make() faz todo o trabalho: transforma o texto do endereco
    # num padrao de quadrados preto e branco que qualquer telemovel
    # consegue descodificar de volta para o mesmo texto.
    imagem = qrcode.make(url)
    imagem.save("qrcode_estacao.png")

    print(f"Codigo QR guardado em qrcode_estacao.png, a apontar para:\n{url}")


if __name__ == "__main__":
    main()
