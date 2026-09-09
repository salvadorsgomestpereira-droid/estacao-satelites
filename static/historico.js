// Vai buscar as passagens registadas ao servidor, mostra-as numa lista
// e num grafico simples de barras (quantas passagens por dia).

async function carregar() {
    const resposta = await fetch("/api/historico");
    const dados = await resposta.json();
    const passagens = dados.passagens;

    const lista = document.getElementById("lista-historico");
    lista.innerHTML = "";

    if (passagens.length === 0) {
        lista.innerHTML = "<p>Ainda nao ha passagens registadas. " +
            "Deixa o historico.py a correr em segundo plano para comecar a apanhar dados.</p>";
    }

    passagens.forEach((passagem) => {
        const cartao = document.createElement("article");
        cartao.className = "cartao-satelite";
        const data = new Date(passagem.inicio);
        cartao.innerHTML = `
            <h2>${passagem.nome}</h2>
            <dl class="grelha-dados">
                <dt>Data/hora</dt><dd>${data.toLocaleString("pt-PT")}</dd>
                <dt>Altura maxima</dt><dd>${passagem.altura_maxima.toFixed(1)} graus</dd>
                <dt>Duracao</dt><dd>${Math.round(passagem.duracao_segundos)} s</dd>
            </dl>
        `;
        lista.appendChild(cartao);
    });

    desenharGrafico(passagens);
}

function desenharGrafico(passagens) {
    // Agrupa as passagens por dia (so a parte "AAAA-MM-DD" da data).
    const contagemPorDia = {};
    passagens.forEach((passagem) => {
        const dia = passagem.inicio.slice(0, 10);
        contagemPorDia[dia] = (contagemPorDia[dia] || 0) + 1;
    });

    const dias = Object.keys(contagemPorDia).sort();
    const contagens = dias.map((dia) => contagemPorDia[dia]);

    new Chart(document.getElementById("grafico"), {
        type: "bar",
        data: {
            labels: dias,
            datasets: [{
                label: "Passagens observadas",
                data: contagens,
                backgroundColor: "#4da3ff",
            }],
        },
        options: {
            scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
        },
    });
}

carregar();
