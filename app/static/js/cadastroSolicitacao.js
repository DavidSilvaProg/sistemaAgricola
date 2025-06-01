document.addEventListener("DOMContentLoaded", () => {
	let contador = 1;

	const produtos = window.produtos || [];
	const inputProduto = document.getElementById("produto-input");
	const lista = document.getElementById("autocomplete-list");
	const container = document.getElementById("autocomplete-container");

	if (!inputProduto || !lista || !container) return;

	const fuse = new Fuse(produtos, {
		keys: ["nome"],
		threshold: 0.4,
		includeScore: true,
		ignoreLocation: true
	});

	function debounce(func, delay = 300) {
		let timer;
		return (...args) => {
			clearTimeout(timer);
			timer = setTimeout(() => func.apply(this, args), delay);
		};
	}

	function highlightTerm(texto, termo) {
		const idx = texto.toLowerCase().indexOf(termo.toLowerCase());
		if (idx === -1) return texto;
		return texto.slice(0, idx) + "<strong>" + texto.slice(idx, idx + termo.length) + "</strong>" + texto.slice(idx + termo.length);
	}

	function aplicarMascaraDecimal(input) {
		input.addEventListener('input', () => {
			let valor = input.value;

			valor = valor.replace(',', '.');
			valor = valor.replace(/[^0-9.]/g, '');

			const partes = valor.split('.');
			if (partes.length > 2) {
				valor = partes[0] + '.' + partes.slice(1).join('');
			}

			input.value = valor;
		});
	}

	function inserirLinhaProduto(nome, unidade, quantidade, idProduto, bloquearCampos = false) {
		if (idProduto && document.querySelector(`input[type="hidden"][value="${idProduto}"]`)) {
			alert("Este produto já foi adicionado.");
			return;
		}

		contador++;
		const tbody = document.getElementById('inputsContainer');

		const linha = document.createElement('tr');
		linha.classList.add('border-b');
		linha.innerHTML = `
			<td class="px-3 py-2 w-2/3">
				<input type="hidden" name="id_produto${contador}" value="${idProduto}">
				<input type="text" name="produto${contador}" value="${nome}" required
					class="w-full border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					${bloquearCampos ? 'readonly' : ''}>
			</td>
			<td class="px-3 py-2 w-1/4">
				<select name="unidade${contador}" ${bloquearCampos ? 'disabled' : ''}
                    class="w-full border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onchange="ajustarInputQuantidade(this)"
                    data-contador="${contador}">
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
				${bloquearCampos ? `<input type="hidden" name="unidade${contador}" value="${unidade}">` : ''}
			</td>
			<td class="px-3 py-2 w-1/6">
				<input
					type="text"
					name="quantidade${contador}"
					value="${quantidade}"
					required
					class="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				>
			</td>
			<td class="px-3 py-2">
				<button type="button" onclick="removerLinha(this)"
					class="text-red-600 text-sm hover:text-red-800 flex items-center gap-1">
					❌ <span>Remover</span>
				</button>
			</td>
		`;

		tbody.appendChild(linha);
		ajustarInputQuantidade(linha.querySelector('select'));
	}

	window.ajustarInputQuantidade = function (selectElement) {
		const linha = selectElement.closest('tr');
		const inputQtd = linha.querySelector('input[name^="quantidade"]');

		const novoInput = inputQtd.cloneNode(true);
		inputQtd.parentNode.replaceChild(novoInput, inputQtd);

		aplicarMascaraDecimal(novoInput);

		const unidade = selectElement.value;
		if (["Unidade", "Pacote", "Caixa"].includes(unidade)) {
			novoInput.addEventListener("keydown", (e) => {
				if (e.key === "." || e.key === ",") {
					e.preventDefault();
				}
			});
		}
	};

	window.removerLinha = function (botao) {
		const linha = botao.closest('tr');
		if (linha) linha.remove();
	};

	window.adicionarProdutoAvulso = function () {
		inserirLinhaProduto('', '', '', '', false);
	};

	function mostrarLista(termo = '') {
		const resultados = termo ? fuse.search(termo).map(r => r.item) : produtos.slice(0, 20);
		lista.innerHTML = "";

		resultados.forEach(p => {
			const li = document.createElement("li");
			li.innerHTML = highlightTerm(p.nome, termo);
			li.className = "px-3 py-2 hover:bg-blue-100 cursor-pointer";
			li.setAttribute("role", "option");
			li.setAttribute("tabindex", "-1");
			li.onclick = () => {
				inserirLinhaProduto(p.nome, p.unidade, '', p.id, true); // bloqueia campos
				inputProduto.value = '';
				container.classList.add("hidden");
			};
			lista.appendChild(li);
		});

		container.classList.toggle("hidden", resultados.length === 0);
	}

	inputProduto.addEventListener("input", debounce(() => {
		mostrarLista(inputProduto.value.trim());
	}, 200));

	inputProduto.addEventListener("focus", () => {
		mostrarLista();
	});

	inputProduto.addEventListener("keydown", (e) => {
		if (e.key === "Enter") {
			e.preventDefault();
			const termo = inputProduto.value.trim().toLowerCase();
			const match = produtos.find(p => p.nome.toLowerCase() === termo);
			if (match) {
				inserirLinhaProduto(match.nome, match.unidade, '', match.id, true);
			} else {
				inserirLinhaProduto(inputProduto.value, '', '', '', false);
			}
			inputProduto.value = '';
			container.classList.add("hidden");
		}
	});

	document.addEventListener("click", (e) => {
		if (!container.contains(e.target) && e.target !== inputProduto) {
			container.classList.add("hidden");
		}
	});

	const form = document.getElementById("requestForm");
    const msgErro = document.getElementById("mensagem-erro");

    form.addEventListener("submit", (e) => {
        const linhas = document.querySelectorAll("#inputsContainer tr");

        if (linhas.length === 0) {
            e.preventDefault();
            msgErro.textContent = "⚠ Adicione ao menos um produto antes de enviar a solicitação.";
            msgErro.classList.remove("hidden");

            // Scroll até a mensagem
            msgErro.scrollIntoView({ behavior: "smooth", block: "center" });

            // Oculta depois de 5 segundos
            setTimeout(() => {
                msgErro.classList.add("hidden");
            }, 5000);
        }
    });
});
