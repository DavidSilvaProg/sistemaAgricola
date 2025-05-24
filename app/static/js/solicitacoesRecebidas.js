window.onload = function () {
    aplicarFiltroInicial();
};

function aplicarFiltroInicial() {
    filtrarRecebidosPorData(); // Busca os últimos 30 dias por padrão
}

function verDetalhes(id) {
    window.location.href = `detalhesSolicitacaoRecebida/${id}`;
}

// Debounce para evitar múltiplas requisições rápidas
let debounceTimer;
function debounce(func, delay = 500) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(func, delay);
}

function filtrarRecebidosPorData() {
    const dataInicioInput = document.getElementById("dataInicio");
    const dataFimInput = document.getElementById("dataFim");

    let dataInicio = dataInicioInput?.value;
    let dataFim = dataFimInput?.value;

    // Se nenhuma data for fornecida, busca últimos 30 dias
    if (!dataInicio) {
        const hoje = new Date();
        const mesPassado = new Date();
        mesPassado.setDate(hoje.getDate() - 30);
        dataInicio = mesPassado.toISOString().split("T")[0];
    }
    if (!dataFim) {
        dataFim = new Date().toISOString().split("T")[0];
    }

    const url = `/api/recebidos?data_inicio=${dataInicio}&data_fim=${dataFim}`;

    fetch(url)
        .then(response => response.json())
        .then(dados => renderTabelaRecebidos(dados))
        .catch(error => console.error('Erro ao buscar dados:', error));
}

function renderTabelaRecebidos(dados) {
    const tbody = document.querySelector("#recebidos tbody");
    tbody.innerHTML = "";

    dados.forEach(pedido => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${pedido.id_solicitacao}</td>
            <td>${pedido.nome_usuario}</td>
            <td>${pedido.nome_solicitacao}</td>
            <td>${pedido.nome_setor}</td>
            <td>${pedido.data_solicitacao}</td>
            <td>${pedido.data_recebido}</td>
            <td>${pedido.total_recebido}</td>
            <td><span class="detalhes" onclick="verDetalhes(${pedido.id_recebido})">Detalhes</span></td>
        `;
        tbody.appendChild(tr);
    });

    const badge = document.getElementById("contagemVisivel");
    badge.innerHTML = `Mostrando <strong>${dados.length}</strong> pedidos`;
}
