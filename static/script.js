// Vai buscar a lista de satelites visiveis ao servidor e desenha-a no
// ecra. Repete isto de X em X segundos para a pagina se manter
// atualizada sozinha, sem o utilizador ter de a recarregar a mao.

const INTERVALO_MS = 15000;

const mapa = L.map("mapa").setView([37.08, -8.12], 3);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; colaboradores do OpenStreetMap",
}).addTo(mapa);

L.marker([37.08, -8.12]).addTo(mapa).bindPopup("Vilamoura (observador)");

let marcadoresSatelites = [];

function limparMarcadoresSatelites() {
    marcadoresSatelites.forEach((marcador) => mapa.removeLayer(marcador));
    marcadoresSatelites = [];
}

function criarCartao(satelite) {
    const cartao = document.createElement("article");
    cartao.className = "cartao-satelite";
    cartao.innerHTML = `
        <p class="categoria">${satelite.categoria}</p>
        <h2>${satelite.nome}</h2>
        <dl class="grelha-dados">
            <dt>Altura no ceu</dt><dd>${satelite.altura_graus.toFixed(1)} graus</dd>
            <dt>Azimute</dt><dd>${satelite.azimute_graus.toFixed(1)} graus</dd>
            <dt>Altitude</dt><dd>${satelite.altitude_km.toFixed(0)} km</dd>
            <dt>Velocidade</dt><dd>${satelite.velocidade_km_s.toFixed(2)} km/s</dd>
            <dt>Pais / operador</dt><dd>${satelite.pais_operador ?? "desconhecido"}</dd>
            <dt>Lancamento</dt><dd>${satelite.ano_lancamento ?? "desconhecido"}</dd>
            <dt>Idade</dt><dd>${satelite.idade_anos != null ? satelite.idade_anos + " anos" : "desconhecida"}</dd>
        </dl>
    `;
    return cartao;
}

async function atualizar() {
    let dados;
    try {
        const resposta = await fetch("/api/visiveis");
        dados = await resposta.json();
    } catch (erro) {
        // Falha de rede entre o telemovel e o servidor (nao entre o
        // servidor e a internet - essa e tratada do lado do Python).
        mostrarAviso("Sem ligacao ao servidor. A tentar de novo em breve...");
        return;
    }

    if (!dados.ok) {
        mostrarAviso("Nao foi possivel atualizar os dados (" + dados.aviso + "). A mostrar os ultimos dados conhecidos.");
    } else if (dados.aviso) {
        // ok=true mas com aviso: os dados chegaram, mas tle.py teve de
        // usar uma copia desatualizada ou o modo de demonstracao.
        mostrarAviso(dados.aviso);
    } else {
        esconderAviso();
    }

    const lista = document.getElementById("lista-satelites");
    lista.innerHTML = "";
    limparMarcadoresSatelites();

    if (dados.satelites.length === 0) {
        lista.innerHTML = "<p>Nenhum satelite acima do horizonte neste momento.</p>";
    }

    dados.satelites.forEach((satelite) => {
        lista.appendChild(criarCartao(satelite));

        const marcador = L.circleMarker([satelite.latitude, satelite.longitude], {
            radius: 5,
            color: "#4da3ff",
        }).addTo(mapa).bindPopup(satelite.nome);
        marcadoresSatelites.push(marcador);
    });

    document.getElementById("ultima-atualizacao").textContent =
        "Atualizado as " + new Date().toLocaleTimeString("pt-PT");
}

function mostrarAviso(texto) {
    const avisoEl = document.getElementById("aviso");
    avisoEl.textContent = texto;
    avisoEl.hidden = false;
}

function esconderAviso() {
    document.getElementById("aviso").hidden = true;
}

atualizar();
setInterval(atualizar, INTERVALO_MS);
