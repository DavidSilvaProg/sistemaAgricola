document.addEventListener("DOMContentLoaded", () => {
	const produtos = window.produtos || [];

	const inputProduto = document.getElementById("produto-input");
	const hiddenIdProduto = document.createElement("input");
	hiddenIdProduto.type = "hidden";
	hiddenIdProduto.name = "id_produto";
	hiddenIdProduto.id = "id_produto";
	inputProduto.parentNode.appendChild(hiddenIdProduto);

	const lista = document.getElementById("autocomplete-list");
	const container = document.getElementById("autocomplete-container");
	const msgErro = document.getElementById("mensagem-erro");

	if (!inputProduto || !lista || !container || !hiddenIdProduto) return;

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
				inputProduto.value = p.nome;
				hiddenIdProduto.value = p.id;
				container.classList.add("hidden");
				document.getElementById("quantidade").value = "";
				ajustarCampoQuantidade(p.unidade);
			};

			lista.appendChild(li);
		});

		container.classList.toggle("hidden", resultados.length === 0);
	}

	inputProduto.addEventListener("input", debounce(() => {
		const termo = inputProduto.value.trim();
		hiddenIdProduto.value = "";
		mostrarLista(termo);
	}, 200));

	inputProduto.addEventListener("focus", () => {
		if (inputProduto.value.trim() !== '') {
			mostrarLista(inputProduto.value.trim());
		}
	});

	inputProduto.addEventListener("keydown", (e) => {
		if (e.key === "Enter") {
			e.preventDefault();
			const termo = inputProduto.value.trim().toLowerCase();
			const match = produtos.find(p => p.nome.toLowerCase() === termo);
			if (match) {
				inputProduto.value = match.nome;
				hiddenIdProduto.value = match.id;
				ajustarCampoQuantidade(match.unidade);
			}
			container.classList.add("hidden");
		}
	});

	document.addEventListener("click", (e) => {
		if (!container.contains(e.target) && e.target !== inputProduto) {
			container.classList.add("hidden");
		}
	});

	// Validação no submit
	const form = document.getElementById("requestForm");
	form.addEventListener("submit", (e) => {
		if (!hiddenIdProduto.value) {
			e.preventDefault();
			msgErro.textContent = "⚠ Você precisa selecionar um produto válido da lista.";
			msgErro.classList.remove("hidden");
			msgErro.scrollIntoView({ behavior: "smooth", block: "center" });

			setTimeout(() => {
				msgErro.classList.add("hidden");
			}, 5000);
		}
	});

	// Função de ajuste do campo quantidade
    function ajustarCampoQuantidade(unidade) {
        const inputQtd = document.getElementById("quantidade");
        if (!inputQtd) return;

        const novoInput = inputQtd.cloneNode(true);
        inputQtd.parentNode.replaceChild(novoInput, inputQtd);

        // Usamos "text" para controlar melhor a digitação
        novoInput.setAttribute("type", "text");
        novoInput.setAttribute("inputmode", "decimal");

        // Substitui vírgula por ponto automaticamente
        novoInput.addEventListener("input", () => {
            novoInput.value = novoInput.value.replace(",", ".");
        });

        // Se for unidade inteira, bloqueia ponto e vírgula
        if (["Unidade", "Pacote", "Caixa"].includes(unidade)) {
            novoInput.addEventListener("keydown", (e) => {
                if (e.key === "." || e.key === ",") {
                    e.preventDefault();
                }
            });
            // Permite apenas números inteiros
            novoInput.addEventListener("input", () => {
                novoInput.value = novoInput.value.replace(/[^0-9]/g, "");
            });
        } else {
            // Permite apenas números decimais com ponto
            novoInput.addEventListener("input", () => {
                novoInput.value = novoInput.value
                    .replace(",", ".")             // troca vírgula por ponto
                    .replace(/[^0-9.]/g, "")       // remove caracteres inválidos
                    .replace(/(\..*)\./g, '$1');   // impede múltiplos pontos
            });
        }
    }
});
