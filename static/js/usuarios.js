//usuarios.html

let idUsuario = null

function novoUsuario() {
    window.location.href = "cadastrarUsuario"; // Altere para a página real de solicitação
}
function editarUsuario(id) {
    window.location.href = `editarUsuario/${id}`;
}

function excluirUsuario() {
    id = idUsuario
    window.location.href = `excluirUsuario/${id}`;
}

function abrirModal(id) {
    idUsuario = id
    document.getElementById('meuModal').style.display = 'flex';
}

function fecharModal() {
    document.getElementById('meuModal').style.display = 'none';
}
