//setores.html
let idSetor = null

function novoSetor() {
    window.location.href = "cadastrarSetor"; // Altere para a página real de solicitação
}
function editarSetor(id) {
    window.location.href = `editarSetor/${id}`;
}

function excluirSetor() {
    window.location.href = `excluirSetor/${idSetor}`;
}

function abrirModal(id) {
    idSetor = id
    document.getElementById('meuModal').style.display = 'flex';
}

function fecharModal() {
    document.getElementById('meuModal').style.display = 'none';
}