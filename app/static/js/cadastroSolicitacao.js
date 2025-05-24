let contador = 1;

document.addEventListener('DOMContentLoaded', () => {
    aplicarConversaoCampos(); // Aplica aos campos iniciais
});

function adicionarInput() {
    contador = parseInt(getUltimoId()) + 1;

    const container = document.createElement('div');
    container.innerHTML = `
        <label for="produto${contador}">Produto ${contador}:</label>
        <input type="text" id="produto${contador}" name="produto${contador}" class="produto" required>
        <label for="quantidade${contador}">Quantidade:</label>
        <input type="text" id="quantidade${contador}" name="quantidade${contador}" class="quantidade" min="1" required>
        <button type="button" class="btn-remover" onclick="removerInput(this)">❌ Remover</button>
    `;

    document.getElementById('inputsContainer').appendChild(container);
    aplicarConversaoCampos(); // Aplica conversão ao novo campo
}

function removerInput(botao) {
    botao.parentNode.remove();
    contador--;
}

function getUltimoId() {
    const inputs = document.querySelectorAll('#inputsContainer input[type="text"]');
    if (inputs.length > 0) {
        const ultimoInput = inputs[inputs.length - 1];
        const id = ultimoInput.id;
        const numero = id.replace(/\D/g, ''); // Remove tudo que não for número
        return numero;
    }
    return 1;
}

function aplicarConversaoCampos() {
    document.querySelectorAll("input[name^='quantidade']").forEach(campo => {
        campo.removeEventListener('input', tratarVirgula); // Evita duplicação
        campo.addEventListener('input', tratarVirgula);
    });
}

function tratarVirgula(event) {
    const campo = event.target;
    campo.value = campo.value.replace(",", ".");
}
