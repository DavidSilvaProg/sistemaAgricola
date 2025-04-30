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
    const statusSelecionado = document.getElementById("filtroStatus").value.toLowerCase();

    const tabela = document.getElementById(idTabela);
    const linhas = tabela.getElementsByTagName("tr");

    for (let i = 1; i < linhas.length; i++) {
        const colunas = linhas[i].getElementsByTagName("td");
        const status = colunas[5].innerText.toLowerCase(); // coluna do status
        const ehCancelado = status.includes("cancelado");

        // ❗ Primeira verificação: se o status da linha bate com o do select
        const correspondeAoStatus = statusSelecionado === "" || status === statusSelecionado;

        // ❗ Segunda verificação: se bate com o texto digitado
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

        // Condição final: deve ocultar se NÃO bater com texto, OU se for cancelado e checkbox ativo
        const deveOcultar = !correspondeAoTexto || (ocultarCancelados && ehCancelado);
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

