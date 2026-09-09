# Notas de estudo — Estação de Rastreio de Satélites

Este ficheiro resume tudo o que precisas de conseguir explicar sobre o
projeto: os conceitos de física por trás do código, e o que faz cada
ficheiro. Usa-o para rever antes da arguição.

---

## 1. O que é um TLE, e porque envelhece

**TLE** = *Two-Line Element set* ("conjunto de elementos em duas
linhas"). É a forma como o NORAD descreve a órbita de um satélite com
poucos números, escritos em duas linhas de texto de ~69 caracteres.

Um TLE contém, entre outras coisas:

- **Número de catálogo NORAD** — identifica o satélite (ex.: 25544 = ISS).
- **Inclinação** — ângulo entre o plano da órbita e o equador.
- **Excentricidade** — quão elíptica (não-circular) é a órbita.
- **Argumento do perigeu** e **ascensão reta do nodo ascendente** — dois
  ângulos que orientam a elipse da órbita no espaço.
- **Anomalia média** — onde está o satélite na sua órbita, na época do TLE.
- **Movimento médio** — quantas voltas dá à Terra por dia.
- **Época** — a data/hora exata a que estes números foram medidos.

**Porque envelhece:** um TLE é uma "fotografia" da órbita, tirada num
certo instante (a época). A órbita real desvia-se ligeiramente dessa
previsão com o tempo, por causas como o atrito com a atmosfera residual
(mesmo a 400 km ainda há moléculas de ar) e pequenas perturbações
gravitacionais. Quanto mais tempo passa desde a época, menos precisa é
a posição calculada a partir do TLE — por isso o projeto só usa uma
cópia local do TLE até esta ter 12 horas, e depois descarrega uma nova
(ver `tle.py`).

## 2. Como se calcula a posição de um satélite

A biblioteca **Skyfield** aplica aos números do TLE um modelo
matemático chamado **SGP4** (*Simplified General Perturbations 4*).
Não precisas de saber deduzir o SGP4 (é bastante complexo), mas sim
saber o que ele faz: recebe a órbita "fotografada" no TLE e o instante
de tempo que queres, e devolve a posição e a velocidade do satélite
nesse instante, já corrigidas para os efeitos que fazem a órbita
desviar-se ligeiramente (atrito atmosférico, achatamento da Terra nos
polos, etc.).

No código, isto acontece na linha `satelite.at(tempo)` — é aí que o
Skyfield corre o SGP4.

A partir dessa posição calculamos duas coisas diferentes:

- **Posição geográfica (subponto)** — `wgs84.subpoint(...)`: a
  latitude/longitude/altitude do ponto da Terra mesmo por baixo do
  satélite. É um facto absoluto, igual para todos.
- **Posição topocêntrica** — `satelite - observador`, depois
  `.altaz()`: a altura (ângulo acima do horizonte) e o azimute (direção
  da bússola) vistos especificamente de Vilamoura. Dois observadores em
  sítios diferentes veem o mesmo satélite com alturas/azimutes
  diferentes — é como duas pessoas em cidades diferentes descreverem de
  forma diferente onde está o mesmo avião no céu.

**Velocidade:** o Skyfield dá a velocidade como um vetor com três
componentes (x, y, z), em km/s. Para obter só "a quantos km/s vai",
juntamos as três com o teorema de Pitágoras generalizado a 3D:
`velocidade = raiz_quadrada(vx² + vy² + vz²)`.

## 3. Porque um satélite só é visível acima do horizonte

A Terra é uma esfera (mais precisamente, o elipsoide WGS84 — ligeiramente
achatado nos polos). Se um satélite estiver "do outro lado do mundo" em
relação a um observador, a própria Terra tapa a linha de vista entre os
dois, tal como uma parede impede duas pessoas de se verem uma à outra.
Só quando o satélite sobe o suficiente na órbita para ficar acima do
plano do horizonte local é que existe uma linha reta desimpedida — esse
instante chama-se **nascer** (*rise*). Quando desce de novo chama-se
**ocaso** (*set*), e o ponto mais alto no meio é a **culminação**.

No projeto, um satélite conta como "visível" quando a sua altura
(ângulo acima do horizonte) é ≥ 10° — não 0°, porque na prática há
sempre árvores, casas ou montanhas a tapar a vista perto do chão (ver
`ALTURA_MINIMA_GRAUS` em `config.py`).

## 4. Porque a órbita geoestacionária fica a 35 786 km

Quanto mais perto da Terra, mais forte a gravidade "puxa", e por isso o
satélite tem de andar mais depressa para não cair — e dá a volta ao
planeta mais depressa. Isto é a **3.ª Lei de Kepler**:

```
T² = (4π² / (G·M)) × r³
```

- `T` = período orbital (tempo a dar uma volta completa)
- `r` = raio da órbita (distância ao centro da Terra)
- `G` = constante gravitacional; `M` = massa da Terra (o produto `G·M` é
  sempre o mesmo, é uma propriedade fixa da Terra)

Esta fórmula diz: quanto maior o raio, maior o período. Um satélite
geoestacionário é colocado à distância exata onde o período orbital é
de **24 horas** (mais precisamente, um dia sideral: 86 164 segundos) —
o mesmo tempo que a Terra demora a rodar sobre si mesma. Resolvendo a
fórmula para `r` com esse `T`, o resultado é sempre o mesmo:
**r ≈ 42 164 km do centro da Terra**. Subtraindo o raio da Terra
(~6 378 km), sobra a altitude acima da superfície: **≈35 786 km**. Não
é uma altura escolhida à mão — é a única onde a órbita "bate certo" com
um dia completo, fazendo o satélite parecer parado no céu.

## 5. Relação entre altitude e velocidade orbital

Quanto mais alta a órbita, **mais devagar** o satélite anda (e mais
tempo demora a dar a volta):

| Satélite/categoria | Altitude aproximada | Velocidade aproximada | Período aproximado |
|---|---|---|---|
| ISS | ~400 km | ~7,7 km/s | ~90 minutos |
| GPS | ~20 200 km | ~3,9 km/s | ~12 horas |
| Geoestacionário | ~35 786 km | ~3,1 km/s | 24 horas |

A razão é a mesma 3.ª Lei de Kepler da secção anterior: perto da Terra
a gravidade é mais forte, exige mais velocidade para "não cair"; longe,
a gravidade é mais fraca, e uma velocidade menor já basta para manter a
órbita.

## 6. O que faz cada ficheiro do projeto

**Programas de aprendizagem (etapas 1 a 4, linha de comandos):**

| Ficheiro | O que faz |
|---|---|
| `etapa1_iss.py` | Descarrega o TLE da ISS e imprime posição/velocidade atuais |
| `etapa2_categorias.py` | Carrega várias categorias e mostra tabela ordenada por altitude |
| `etapa3_horizonte.py` | Calcula quem está acima do horizonte em Vilamoura, e prevê passagens |
| `etapa4_base_dados.py` | Cruza TLE com o satcat pelo NORAD ID e guarda tudo em SQLite |

**Módulos da aplicação real (usados pelo servidor web):**

| Ficheiro | O que faz |
|---|---|
| `config.py` | Coordenadas do observador, categorias de satélites, modo de demonstração, altura mínima |
| `tle.py` | Descarrega/guarda em cache os TLE de cada categoria (regra das 12 horas, tempo-limite de 8s por pedido, fallback para `reserva/`) |
| `satcat.py` | Descarrega/guarda em cache o catálogo de satélites (país, ano, tipo de objeto) |
| `base_dados.py` | Cria e mexe no `satelites.db` (SQLite): tabelas `satelites` e `passagens` |
| `posicoes.py` | Junta TLE + base de dados: calcula quem está visível agora, com todos os dados |
| `app.py` | Servidor Flask: página principal, página de histórico, e as duas rotas de API (`/api/visiveis`, `/api/historico`) |
| `historico.py` | Corre em segundo plano, sonda de 30 em 30 segundos, e regista cada passagem completa na base de dados |
| `gerar_qrcode.py` | Gera uma imagem com um código QR a apontar para a página publicada |

**Frontend (o que corre no browser do telemóvel):**

| Ficheiro | O que faz |
|---|---|
| `templates/index.html` | Estrutura da página principal (mapa + lista de satélites) |
| `templates/historico.html` | Estrutura da página de histórico (gráfico + lista de passagens) |
| `static/style.css` | Aparência, desenhada primeiro para telemóvel (mobile-first) |
| `static/script.js` | Vai buscar `/api/visiveis` a cada 15 segundos e atualiza a lista e o mapa (Leaflet) |
| `static/historico.js` | Vai buscar `/api/historico` e desenha a lista e o gráfico (Chart.js) |

**Outros:**

| Ficheiro | O que faz |
|---|---|
| `requirements.txt` | Lista das bibliotecas Python necessárias |
| `Procfile` | Diz ao serviço de alojamento (Render) como arrancar o servidor em produção (`gunicorn`) |
| `.gitignore` | Ficheiros que não devem ir para o repositório Git (caches, base de dados local) |
| `reserva/` | Cópia de TLE e satcat para o modo de demonstração sem internet |
| `README.md` | Instruções de instalação, execução e publicação |

## 7. Como as peças encaixam (fluxo geral)

1. `tle.py` descarrega as órbitas (TLE) de cada categoria de satélite,
   guardando em cache local (12 horas) para não sobrecarregar o Celestrak.
2. `satcat.py` descarrega o catálogo com país/ano/tipo de cada satélite,
   também em cache.
3. `etapa4_base_dados.py` corre uma vez (ou de vez em quando) para
   cruzar os dois pelo número NORAD e guardar tudo em `satelites.db`.
4. `posicoes.py` é chamado sempre que é preciso saber "quem está
   visível agora": pega nos TLE mais recentes, calcula a posição de
   cada satélite visto de Vilamoura, e junta a informação guardada na
   base de dados.
5. `app.py` usa `posicoes.py` para responder ao pedido `/api/visiveis`
   que o browser faz a cada 15 segundos, e `base_dados.py` para
   responder a `/api/historico`.
6. `historico.py` corre à parte (em segundo plano), chamando também
   `posicoes.py` a cada 30 segundos, e regista em `satelites.db` cada
   passagem que começa e termina.

## 8. Como o sistema avisa (em vez de rebentar)

Cada função que pode falhar por causa da rede devolve, além dos dados,
um "aviso" (`tle.carregar_satelites()` → `(satelites, aviso)`,
`posicoes.calcular_visiveis()` → `(visiveis, aviso)`). `aviso` é `None`
quando está tudo bem, ou um texto em português pronto a mostrar quando
algum grupo de satélites teve de usar dados desatualizados (ou o modo
de demonstração). O `app.py` mete esse aviso dentro da resposta JSON, e
o `script.js` mostra-o numa barra amarela no topo da página — assim o
utilizador *vê* que os dados podem estar desatualizados, em vez de a
página simplesmente falhar ou mostrar dados errados sem avisar.

Isto só funciona porque cada pedido de rede (`urlopen(...)`) tem um
**tempo-limite** (`TEMPO_LIMITE_SEGUNDOS`, 8s para os TLE): sem isso, se
um servidor externo (como o Celestrak) não responder, o Python ficava
bloqueado à espera *para sempre* em vez de desistir e mostrar o aviso.
Foi exatamente isto que aconteceu na primeira publicação no Render: o
servidor gratuito demora a "acordar", os pedidos de TLE sem
tempo-limite ficavam pendurados, e a página dava erro 500 em vez de
mostrar os dados de reserva.

## 9. Perguntas típicas que te podem fazer

- *"Porque é que usaste cache para os TLE?"* → Para não bombardear o
  servidor do Celestrak a cada pedido, e porque um TLE só perde
  precisão ao fim de várias horas, não de segundos.
- *"O que acontece se a internet falhar durante a apresentação?"* → O
  sistema usa a última cópia guardada localmente (ou a de `reserva/`,
  em modo de demonstração) e mostra um aviso, mas não mostra uma
  página de erro.
- *"Porque escolheste SQLite e não outra base de dados?"* → Vem
  incluído no Python (não precisa de instalar nada) e guarda tudo num
  único ficheiro — mais simples para um projeto deste tamanho.
- *"Como sabes que o cálculo está certo?"* → Confirmámos valores
  conhecidos: a ISS a ~400 km e ~7,7 km/s, o GPS a ~20 200 km, os
  geoestacionários a ~35 786 km — todos batem certo com os valores reais.
- *"Porque é que os pedidos de rede têm um tempo-limite (timeout)?"* →
  Sem ele, se o servidor do Celestrak não responder, o programa fica
  bloqueado à espera indefinidamente. Com um tempo-limite curto (8
  segundos), o programa desiste depressa e usa a cópia guardada em vez
  de deixar a página inteira sem resposta — foi um bug real que
  aconteceu na primeira publicação no Render (ver secção 8).
