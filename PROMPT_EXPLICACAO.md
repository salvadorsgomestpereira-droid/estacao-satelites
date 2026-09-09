# Prompt para uma sessão de explicação (copia e cola no Claude)

Abre uma conversa nova com o Claude Code nesta pasta do projeto (ou o
Claude normal, colando os ficheiros que pedir) e cola o texto abaixo.

---

```
Sou um aluno do 9.º ano e construí (com ajuda de IA) uma estação de
rastreio de satélites como Projeto Anual de Físico-Química. Vou ser
confrontado com o código depois da apresentação para provar que percebo
o que fiz, por isso preciso que me expliques TODO O SOFTWARE deste
projeto, ficheiro a ficheiro, até eu conseguir explicá-lo por palavras
minhas.

Lê primeiro o ficheiro NOTAS_ESTUDO.md e o README.md desta pasta para
teres o contexto todo, e depois percorre o resto do código.

Modo de trabalho que quero que sigas:

1. Um ficheiro (ou conceito) de cada vez. Não avances para o seguinte
   sem eu confirmar que percebi.
2. Para cada ficheiro, explica em português simples: o que faz, porque
   existe, e como se liga aos outros ficheiros do projeto.
3. Sempre que houver uma fórmula de física ou um conceito de astronomia
   (TLE, SGP4, altura/azimute, órbita geoestacionária, etc.), explica-o
   como se eu não soubesse nada sobre o assunto, com uma analogia se
   ajudar.
4. No fim de cada ficheiro ou conceito, faz-me 1 ou 2 perguntas para
   verificar que percebi. Se eu responder mal ou disser que não sei,
   explica outra vez de forma diferente (não repitas a mesma explicação
   com outras palavras só).
5. Cobre também as perguntas da secção "Perguntas típicas" do
   NOTAS_ESTUDO.md, e mais algumas que aches que me podem fazer.
6. No fim de tudo, faz-me um pequeno "exame simulado": escolhe ao acaso
   5 perguntas sobre partes diferentes do projeto (física e código) e
   corrige as minhas respostas.

Começa pelo NOTAS_ESTUDO.md e pelo README.md, depois segue esta ordem:

1. config.py
2. tle.py e satcat.py (como descarregam e guardam em cache)
3. base_dados.py (as tabelas SQLite)
4. posicoes.py (o cálculo da posição e da visibilidade)
5. app.py (o servidor Flask)
6. historico.py (o registo de passagens em segundo plano)
7. templates/ e static/ (a página web)
8. Os ficheiros etapa1_iss.py a etapa4_base_dados.py (os programas mais
   simples que vieram primeiro, e porque a aplicação final ficou mais
   organizada do que eles)

Não avances de fase enquanto eu não disser "próximo".
```

---

**Nota:** se a sessão de explicação for numa conversa nova sem acesso
aos ficheiros do projeto, diz ao Claude para pedir os ficheiros que
precisar, ou cola tu o conteúdo de `NOTAS_ESTUDO.md` diretamente na
conversa antes deste prompt.
