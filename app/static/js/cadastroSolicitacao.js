let contador = 1;

document.addEventListener('DOMContentLoaded', () => {
    aplicarConversaoCampos(); // Aplica aos campos iniciais
});

function adicionarInput() {
    const contador = parseInt(getUltimoId()) + 1;

    const container = document.createElement('div');
    container.classList.add('flex', 'space-x-4', 'mb-4'); // Espaçamento e margem entre grupos

    container.innerHTML = `
        <div class="flex-1">
            <label for="produto${contador}" class="block text-sm font-medium text-gray-700 mb-1">Produto ${contador}:</label>
            <input
                type="text"
                id="produto${contador}"
                name="produto${contador}"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
        </div>
        <div class="w-28">
            <label for="quantidade${contador}" class="block text-sm font-medium text-gray-700 mb-1">Quantidade:</label>
            <input
                type="text"
                id="quantidade${contador}"
                name="quantidade${contador}"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
            >
        </div>
        <button type="button" class="btn-remover self-end mb-1" onclick="removerInput(this)">❌ Remover</button>
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
