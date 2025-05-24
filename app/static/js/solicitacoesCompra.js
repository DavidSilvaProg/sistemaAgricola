//pedidos.html
window.onload = function () {
    aplicarFiltros('solicitacoes');
};

function novaSolicitacao() {
    window.location.href = "cadastroSolicitacao"; // Altere para a página real de solicitação
}
function verDetalhes(id) {
    window.location.href = `detalhesSolicitacao/${id}`;
}

function aplicarFiltros(idTabela) {
    const input = document.querySelector(`input.filtroTabela[data-tabela="${idTabela}"]`);
    const filtroTexto = input.value.toLowerCase();
    const ocultarCancelados = document.getElementById("ocultarCancelados").checked;
    const ocultarRecebidos = document.getElementById("ocultarRecebidos").checked;
    const statusSelecionado = document.getElementById("filtroStatus").value.toLowerCase();

    const tabela = document.getElementById(idTabela);
    const linhas = tabela.getElementsByTagName("tr");

    for (let i = 1; i < linhas.length; i++) {
        const colunas = linhas[i].getElementsByTagName("td");
        const status = colunas[5].innerText.toLowerCase(); // coluna do status
        const ehCancelado = status.includes("cancelado");
        const ehRecebido = status.includes("recebido");

        const correspondeAoStatus = statusSelecionado === "" || status === statusSelecionado;

        let correspondeAoTexto = false;
        if (correspondeAoStatus) {
            for (let j = 0; j < colunas.length; j++) {
                const texto = colunas[j].textContent || colunas[j].innerText;
                if (texto.toLowerCase().indexOf(filtroTexto) > -1) {
                    correspondeAoTexto = true;
                    break;
                }
            }
        }

        const deveOcultar =
            !correspondeAoTexto ||
            (ocultarCancelados && ehCancelado) ||
            (ocultarRecebidos && ehRecebido);

        linhas[i].style.display = deveOcultar ? "none" : "";
    }

    // Atualiza a contagem de itens visíveis
    let visiveis = 0;
    for (let i = 1; i < linhas.length; i++) {
        if (linhas[i].style.display !== "none") {
            visiveis++;
        }
    }
    const badge = document.getElementById("contagemVisivel");
    if (badge) {
        badge.innerHTML = `Mostrando <strong>${visiveis}</strong> solicitações`;
    }
}


function filtrarTabelaGeral(inputElement) {
    const idTabela = inputElement.getAttribute("data-tabela");
    aplicarFiltros(idTabela);
}

function filtrarTabelaGeralPorId(idTabela) {
    aplicarFiltros(idTabela);
}

async function filtrarTabelaGeralPorId() {
    const dataInicio = document.getElementById("dataInicio").value;
    const dataFim = document.getElementById("dataFim").value;
    const status = document.getElementById("filtroStatus").value;
    const textoBusca = document.getElementById("textoBusca").value.toLowerCase();
    const ocultarCancelados = document.getElementById("ocultarCancelados").checked;
    const ocultarRecebidos = document.getElementById("ocultarRecebidos").checked;

    const url = `/api/solicitacoes?data_inicio=${dataInicio}&data_fim=${dataFim}&status=${status}&ocultar_cancelados=${ocultarCancelados}&ocultar_recebidos=${ocultarRecebidos}&busca=${textoBusca}`;

    const response = await fetch(url);
    const dados = await response.json();

    renderTabelaSolicitacoes(dados);
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

