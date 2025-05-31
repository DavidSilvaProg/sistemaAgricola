let contador = 1;

document.addEventListener('DOMContentLoaded', () => {
    aplicarConversaoCampos(); // Aplica aos campos iniciais
});

function adicionarInput() {
	const contador = parseInt(getUltimoId()) + 1;

	const container = document.createElement('div');
	container.classList.add('mb-6');

	container.innerHTML = `
		<div class="flex space-x-4 items-end">
			<div class="flex-1 max-w-full">
				<label for="produto${contador}" class="block text-sm font-medium text-gray-700 mb-1">Produto ${contador}:</label>
				<input
					type="text"
					id="produto${contador}"
					name="produto${contador}"
					required
					class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				>
			</div>

			<div class="w-28">
				<label for="unidade${contador}" class="block text-sm font-medium text-gray-700 mb-1">Unidade:</label>
				<select
					id="unidade${contador}"
					name="unidade${contador}"
					required
					class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				>
					<option value="Unidade">Unidade</option>
					<option value="Quilograma">Quilograma</option>
					<option value="Grama">Grama</option>
					<option value="Litro">Litro</option>
					<option value="Mililitro">Mililitro</option>
					<option value="Metro">Metro</option>
					<option value="Centímetro">Centímetro</option>
					<option value="Caixa">Caixa</option>
					<option value="Pacote">Pacote</option>
				</select>
			</div>

			<div class="w-20">
				<label for="quantidade${contador}" class="block text-sm font-medium text-gray-700 mb-1">Qtd:</label>
				<input
					type="text"
					id="quantidade${contador}"
					name="quantidade${contador}"
					required
					min="1"
					class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				>
			</div>
		</div>

		<div class="mt-2">
			<button
				type="button"
				class="btn-remover text-red-600 text-sm hover:text-red-800"
				onclick="removerInput(this)"
				title="Remover produto"
			>
				❌ Remover
			</button>
		</div>
	`;

	document.getElementById('inputsContainer').appendChild(container);
	aplicarConversaoCampos?.(); // Executa só se existir
}



function removerInput(botao) {
	const grupo = botao.closest('div.mb-6'); // Pega o container externo que envolve tudo
	if (grupo) {
		grupo.remove();
	}
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
