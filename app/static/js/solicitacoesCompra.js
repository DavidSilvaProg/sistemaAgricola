window.onload = function () {
    aplicarFiltrosRemotos();

    // Event listeners
    document.getElementById("dataInicio").addEventListener("change", aplicarFiltrosRemotos);
    document.getElementById("dataFim").addEventListener("change", aplicarFiltrosRemotos);
    document.getElementById("filtroStatus").addEventListener("change", aplicarFiltrosRemotos);
    document.getElementById("ocultarCancelados").addEventListener("change", aplicarFiltrosRemotos);
    document.getElementById("ocultarRecebidos").addEventListener("change", aplicarFiltrosRemotos);

    // Debounce para o campo de texto
    const inputBusca = document.getElementById("textoBusca");
    if (inputBusca) {
        inputBusca.addEventListener("input", debounce(() => {
            aplicarFiltrosRemotos();
        }, 500));
    }
};

function novaSolicitacao() {
    window.location.href = "cadastroSolicitacao";
}

function verDetalhes(id) {
    window.location.href = `detalhesSolicitacao/${id}`;
}

async function aplicarFiltrosRemotos() {
    const dataInicio = document.getElementById("dataInicio").value;
    const dataFim = document.getElementById("dataFim").value;
    const status = document.getElementById("filtroStatus").value;
    const textoBusca = document.getElementById("textoBusca").value.toLowerCase();
    const ocultarCancelados = document.getElementById("ocultarCancelados").checked;
    const ocultarRecebidos = document.getElementById("ocultarRecebidos").checked;

    const url = `/api/solicitacoes?data_inicio=${dataInicio}&data_fim=${dataFim}&status=${status}&ocultar_cancelados=${ocultarCancelados}&ocultar_recebidos=${ocultarRecebidos}&busca=${textoBusca}`;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }
        const dados = await response.json();
        renderTabelaSolicitacoes(dados);
    } catch (erro) {
        console.error("Erro ao buscar dados:", erro);
    }
}

function renderTabelaSolicitacoes(dados) {
    const tbody = document.querySelector("#solicitacoes tbody");
    tbody.innerHTML = "";

    dados.forEach(pedido => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${pedido.id_solicitacao}</td>
            <td>${pedido.nome_usuario}</td>
            <td>${pedido.nome_solicitacao}</td>
            <td>${pedido.nome_setor}</td>
            <td>${pedido.prioridade_solicitacao}</td>
            <td>${pedido.status_solicitacao}</td>
            <td>${pedido.data_solicitacao}</td>
            <td><span class="detalhes" onclick="verDetalhes(${pedido.id_solicitacao})">Detalhes</span></td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById("contagemVisivel").innerHTML = `Mostrando <strong>${dados.length}</strong> solicitações`;
}

function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}
