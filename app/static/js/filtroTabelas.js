let ordemCrescenteGlobal = {};

document.querySelectorAll('th.ordenavel').forEach(th => {
	th.style.cursor = 'pointer';
	th.addEventListener('click', function () {
		const tabela = th.closest('table');
		const coluna = parseInt(th.getAttribute('data-coluna'));
		const idTabela = tabela.id;

		// Inicializa o controle da tabela se ainda não existir
		if (!ordemCrescenteGlobal[idTabela]) {
			ordemCrescenteGlobal[idTabela] = {};
		}

		// Resetar ordenações das outras colunas
		for (let key in ordemCrescenteGlobal[idTabela]) {
			if (parseInt(key) !== coluna) {
				delete ordemCrescenteGlobal[idTabela][key];
			}
		}

		// Alternar a direção da ordenação
		const asc = !ordemCrescenteGlobal[idTabela][coluna];
		ordemCrescenteGlobal[idTabela][coluna] = asc;

		// Coleta e filtra apenas as linhas visíveis do tbody
		const tbody = tabela.tBodies[0];
		const linhas = Array.from(tbody.rows).filter(row => row.style.display !== 'none');

		// Ordenar as linhas visíveis com base na coluna clicada
		linhas.sort((a, b) => {
			const aTexto = a.cells[coluna]?.innerText.trim().toLowerCase() || '';
			const bTexto = b.cells[coluna]?.innerText.trim().toLowerCase() || '';

			const valorA = parseValor(aTexto);
			const valorB = parseValor(bTexto);

			if (valorA < valorB) return asc ? -1 : 1;
			if (valorA > valorB) return asc ? 1 : -1;
			return 0;
		});

		// Remove todas as linhas do tbody (inclusive travadas) e reaplica ordenação limpa
		const todasLinhas = Array.from(tbody.rows);
		todasLinhas.forEach(row => tbody.removeChild(row));
		linhas.forEach(row => tbody.appendChild(row));
	});
});

// Função para tentar interpretar como número, data ou string
function parseValor(valor) {
	// Remove espaços e troca vírgula por ponto
	const texto = valor.trim().replace(',', '.');

	// Verifica se é número real ou inteiro
	if (/^-?\d+(\.\d+)?$/.test(texto)) {
		return parseFloat(texto);
	}

	// Tenta reconhecer data no formato BR (dd/mm/yyyy)
	const dataBR = texto.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
	if (dataBR) {
		return new Date(`${dataBR[3]}-${dataBR[2]}-${dataBR[1]}`).getTime();
	}

	// Tenta reconhecer ISO ou outro formato válido de data
	const dataISO = Date.parse(texto);
	if (!isNaN(dataISO)) {
		return dataISO;
	}

	// Por fim, retorna como texto
	return texto.toLowerCase();
}

