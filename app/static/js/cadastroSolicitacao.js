let contador = 1;

function adicionarInput() {
    contador = parseInt(getUltimoId()) + 1;

    const container = document.createElement('div');
    container.innerHTML = `
        <label for="produto${contador}">Produto ${contador}:</label>
		<input type="text" id="produto${contador}" name="produto${contador}" class="produto" required>
        <label for="quantidade${contador}">Quantidade:</label>
        <input type="number" id="quantidade${contador}" name='quantidade${contador}' class="quantidade" min="1" required>
        <button type="button" class="btn-remover" onclick="removerInput(this)">❌ Remover</button>
    `;

    document.getElementById('inputsContainer').appendChild(container);
}
function removerInput(botao){
    botao.parentNode.remove();
    contador--;
}

function getUltimoId() {
    const inputs = document.querySelectorAll('#inputsContainer input[type="text"]');
        if (inputs.length >0) {
            const ultimoInput = inputs[inputs.length - 1];
            let ultimoCaracter = 0;

            if (ultimoInput.id.length <= 8) {
                ultimoCaracter = ultimoInput.id.substr(-1);
            }
            else if (ultimoInput.id.length  == 9){
                ultimoCaracter = ultimoInput.id.substr(-2);
            }
            else if (ultimoInput.id.length  == 10){
                ultimoCaracter = ultimoInput.id.substr(-3);
            }

            return ultimoCaracter;
        }
    return null;
}