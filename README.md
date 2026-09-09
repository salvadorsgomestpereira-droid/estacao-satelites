# Estação de Rastreio de Satélites — Vilamoura

Projeto Anual de Físico-Química (9.º ano). Mostra que satélites estão
acima do horizonte em Vilamoura neste momento, prevê as próximas
passagens, e regista um histórico de tudo o que já foi observado.

## O que cada ficheiro faz

| Ficheiro | O que faz |
|---|---|
| `config.py` | Coordenadas do observador (Vilamoura), categorias de satélites, modo de demonstração |
| `tle.py` | Descarrega e guarda em cache os TLE (órbitas) de cada categoria |
| `satcat.py` | Descarrega o catálogo de satélites (país, ano de lançamento, tipo) |
| `base_dados.py` | Guarda tudo em SQLite (`satelites.db`) |
| `posicoes.py` | Calcula, a partir dos TLE, quem está acima do horizonte agora |
| `app.py` | Servidor web (Flask) — a página principal e a de histórico |
| `historico.py` | Corre em segundo plano e regista as passagens observadas |
| `gerar_qrcode.py` | Gera um código QR que aponta para a página publicada |
| `templates/`, `static/` | HTML, CSS e JavaScript da página web |
| `reserva/` | Cópia de TLE e satcat para funcionar sem internet (modo de demonstração) |
| `etapa1_iss.py` … `etapa4_base_dados.py` | Os programas de linha de comandos de cada etapa de aprendizagem |

## Instalar

Precisas de Python 3.10 ou mais recente.

```
pip install -r requirements.txt
```

## Correr localmente

**Ver só a posição da ISS (Etapa 1):**
```
python etapa1_iss.py
```

**Tabela de várias categorias de satélites (Etapa 2):**
```
python etapa2_categorias.py
```

**Ver o que passa por cima de Vilamoura agora (Etapa 3):**
```
python etapa3_horizonte.py
```

**Construir a base de dados com país/ano/tipo de cada satélite (Etapa 4):**
```
python etapa4_base_dados.py
```

**A página web completa:**
```
python app.py
```
Depois abre `http://localhost:5000` no browser (ou, no telemóvel, usa o
IP do portátil que aparece no terminal, por exemplo `http://192.168.1.10:5000`,
desde que o telemóvel esteja na mesma rede Wi-Fi).

**Registar o histórico de passagens** (corre à parte, ao mesmo tempo que o `app.py`):
```
python historico.py
```

## Modo de demonstração (sem internet)

Se o Wi-Fi falhar no dia da apresentação, muda em `config.py`:
```python
MODO_DEMONSTRACAO = True
```
O sistema passa a usar sempre os ficheiros guardados em `reserva/`, sem
tentar ligar-se à internet. As posições calculadas usam TLE antigos
(desatualizados), mas o sistema todo continua a funcionar para a
demonstração. Não esquecer de voltar a pôr `False` depois.

## Publicar a página na internet (Etapa 7)

Vamos usar o **Render** (tem um plano gratuito e permite que o programa
se ligue à internet para ir buscar os TLE — atenção, o PythonAnywhere
gratuito não permite isso, só o Render/serviços parecidos).

1. **Criar uma conta no GitHub** (github.com) se ainda não tiveres, e
   criar um repositório novo (por exemplo `estacao-satelites`).

2. **Enviar o projeto para o GitHub**, no terminal, dentro desta pasta:
   ```
   git init
   git add .
   git commit -m "Estacao de rastreio de satelites"
   git branch -M main
   git remote add origin https://github.com/O_TEU_UTILIZADOR/estacao-satelites.git
   git push -u origin main
   ```

3. **Criar uma conta no Render** (render.com), gratuita.

4. No painel do Render: **New +** → **Web Service** → escolher o
   repositório do GitHub que acabaste de criar.

5. Configurar:
   - **Build Command:** `pip install -r requirements.txt && python etapa4_base_dados.py`
     (o segundo comando pré-preenche a base de dados e a cache de TLE
     *durante* a construção, para o primeiro pedido a seguir ao deploy
     já ter tudo pronto, em vez de ter de descarregar tudo na hora)
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --timeout 60 app:app`
     (já está também no ficheiro `Procfile`) — o `$PORT` é obrigatório
     porque é o Render que escolhe a porta, e sem isto o deploy falha
     com "no open ports detected"; o `--timeout 60` dá tempo suficiente
     para o pedido às vezes ter de voltar a descarregar TLE

6. Clicar em **Create Web Service** e esperar alguns minutos. O Render
   dá-te um endereço parecido com `https://estacao-satelites.onrender.com`.

7. **Gerar o código QR** para esse endereço:
   ```
   python gerar_qrcode.py https://estacao-satelites.onrender.com
   ```
   Isto cria `qrcode_estacao.png` — podes imprimir ou mostrar no ecrã.

8. **Sticker NFC:** a maioria dos stickers NFC graváveis usa uma app
   grátis no telemóvel (por exemplo "NFC Tools") para gravar um URL no
   sticker. Grava lá o mesmo endereço do Render.

**Nota:** o plano gratuito do Render "adormece" o servidor depois de
uns minutos sem visitas, e demora uns 30-60 segundos a "acordar" na
próxima vez que alguém abre a página — não é avaria, é normal.
