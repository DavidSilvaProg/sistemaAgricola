window.onload = function () {
    const tabela = document.getElementById("recebidos"); // 👈 Adiciona esta linha
    const linhas = tabela.getElementsByTagName("tr");

    let visiveis = 0;
    for (let i = 1; i < linhas.length; i++) {
        visiveis++;
    }

    const badge = document.getElementById("contagemVisivel");
    if (badge) {
        badge.innerHTML = `Mostrando <strong>${visiveis}</strong> pedidos`;
    }
};


function verDetalhes(id) {
    window.location.href = `detalhesSolicitacaoRecebida/${id}`;
}
