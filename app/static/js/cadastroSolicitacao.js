let contador = 1;

// Debounce para evitar múltiplas chamadas rápidas
function debounce(func, delay = 300) {
	let timer;
	return (...args) => {
		clearTimeout(timer);
		timer = setTimeout(() => func.apply(this, args), delay);
	};
}

document.addEventListener('DOMContentLoaded', () => {
	aplicarConversaoCampos();
});

function adicionarProdutoCadastrado() {
	const input = document.getElementById('select-produto');
	const valorDigitado = input.value.trim();

	if (!valorDigitado) return;

	const produtoSelecionado = produtosMap[valorDigitado];

	if (!produtoSelecionado) {
		alert('Selecione um produto válido da lista.');
		return;
	}

	const nomeProduto = valorDigitado;
	const unidade = produtoSelecionado.unidade;
	const idProduto = produtoSelecionado.id;

	inserirLinhaProduto(nomeProduto, unidade, '', idProduto);
	input.value = ''; // Limpa o campo
}

function adicionarProdutoAvulso() {
	inserirLinhaProduto('', '', '', '');
}

function inserirLinhaProduto(nome, unidade, quantidade, idProduto) {
	contador++;
	const tbody = document.getElementById('inputsContainer');

	const linha = document.createElement('tr');
	linha.classList.add('border-b');
	linha.innerHTML = `
		<td class="px-3 py-2 w-2/3">
			<input type="hidden" name="id_produto${contador}" value="${idProduto}">
			<input type="text" name="produto${contador}" value="${nome}" required
				class="w-full border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
		</td>
		<td class="px-3 py-2 w-1/4">
			<select name="unidade${contador}" required
				class="w-full border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
				<option ${unidade === 'Unidade' ? 'selected' : ''}>Unidade</option>
				<option ${unidade === 'Quilograma' ? 'selected' : ''}>Quilograma</option>
				<option ${unidade === 'Grama' ? 'selected' : ''}>Grama</option>
				<option ${unidade === 'Litro' ? 'selected' : ''}>Litro</option>
				<option ${unidade === 'Mililitro' ? 'selected' : ''}>Mililitro</option>
				<option ${unidade === 'Metro' ? 'selected' : ''}>Metro</option>
				<option ${unidade === 'Centímetro' ? 'selected' : ''}>Centímetro</option>
				<option ${unidade === 'Caixa' ? 'selected' : ''}>Caixa</option>
				<option ${unidade === 'Pacote' ? 'selected' : ''}>Pacote</option>
			</select>
		</td>
		<td class="px-3 py-2 w-1/6">
			<input type="text" name="quantidade${contador}" value="${quantidade}" required
				class="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
		</td>
		<td class="px-3 py-2">
			<button type="button" onclick="removerLinha(this)"
				class="text-red-600 text-sm hover:text-red-800 flex items-center gap-1">
				❌ <span>Remover</span>
			</button>
		</td>
	`;
	tbody.appendChild(linha);

	aplicarConversaoCampos?.();
}

function removerLinha(botao) {
	const linha = botao.closest('tr');
	if (linha) linha.remove();
}

function aplicarConversaoCampos() {
	document.querySelectorAll("input[name^='quantidade']").forEach(campo => {
		campo.removeEventListener('input', tratarVirgula);
		campo.addEventListener('input', debounce(tratarVirgula));
	});
}

function tratarVirgula(event) {
	event.target.value = event.target.value.replace(",", ".");
}
