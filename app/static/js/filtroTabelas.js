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
            let aTexto = a.cells[coluna]?.textContent.trim() || '';
            let bTexto = b.cells[coluna]?.textContent.trim() || '';

            // Se for a coluna Produto (índice 1), removemos "produto" do início para melhorar a ordenação
            if (coluna === 1) {
                aTexto = aTexto.replace(/^produto\s*/i, '').padStart(10, '0'); // "Produto 5" vira "0000000005"
                bTexto = bTexto.replace(/^produto\s*/i, '').padStart(10, '0');
            }

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
	// Normaliza texto: remove espaços, acentos e troca vírgula por ponto
	const texto = valor.trim()
		.replace(',', ' ') // troca vírgula entre data e hora por espaço
		.replace(/\s+/g, ' ') // normaliza múltiplos espaços
		.replace(/\u200B/g, '') // remove caracteres invisíveis
		.normalize("NFD").replace(/[\u0300-\u036f]/g, "") // remove acentos
		.toLowerCase();

	// Verifica se é número (inteiro ou decimal)
	if (/^-?\d+(\.\d+)?$/.test(texto)) {
		return parseFloat(texto);
	}

	// Verifica se é data BR com ou sem hora (dd/mm/yyyy ou dd/mm/yyyy HH:mm:ss)
	const dataBR = texto.match(/^(\d{2})\/(\d{2})\/(\d{4})(?:\s+(\d{2}):(\d{2}):(\d{2}))?$/);
	if (dataBR) {
		const [ , dia, mes, ano, hora = '00', min = '00', seg = '00' ] = dataBR;
		return new Date(`${ano}-${mes}-${dia}T${hora}:${min}:${seg}`).getTime();
	}

	// Tenta interpretar como data ISO (fallback)
	const dataISO = Date.parse(texto);
	if (!isNaN(dataISO)) {
		return dataISO;
	}

	// Se não for número nem data, retorna como texto sem acento
	return texto.toLowerCase();
}

