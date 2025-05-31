// 🔄 1. Utilitários globais
function debounce(func, delay = 500) {
	let timeout;
	return function (...args) {
		clearTimeout(timeout);
		timeout = setTimeout(() => func.apply(this, args), delay);
	};
}

// 🔘 2. Variáveis globais
let paginaAtual = 1;
const porPagina = 20;
let carregando = false;
let fimDaLista = false;

// 📦 3. Funções principais

function toggleBulkActions() {
	const anyChecked = document.querySelectorAll(".item-checkbox:checked").length > 0;
	document.getElementById("bulk-actions").classList.toggle("hidden", !anyChecked);
}

function novoProduto() {
	window.location.href = "cadastroProduto";
}

function ativarCliqueNasLinhas() {
	const linhas = document.querySelectorAll('#tabelaSolicitacoes tr');
	linhas.forEach(linha => {
		linha.addEventListener('click', () => {
			linhas.forEach(l => l.classList.remove('bg-gray-200'));
			linha.classList.add('bg-gray-200');
		});
	});
}

async function aplicarFiltrosRemotos(reset = false) {
	if (carregando) return;
	if (fimDaLista && !reset) return;

	const textoBusca = document.getElementById("textoBusca").value.toLowerCase();
	const ocultarInativos = document.getElementById("ocultarInativos").checked;

	if (reset) {
		paginaAtual = 1;
		fimDaLista = false;
		document.getElementById("product-table-body").innerHTML = "";
		document.getElementById("spinner-linha")?.classList.remove("hidden");
	}

	const url = `/api/produtos?page=${paginaAtual}&per_page=${porPagina}&busca=${encodeURIComponent(textoBusca)}&ocultar_inativos=${ocultarInativos}`;

	carregando = true;
	document.getElementById("spinner").classList.remove("hidden");

	try {
		const response = await fetch(url);
		if (!response.ok) throw new Error(`Erro na requisição: ${response.status}`);

		const json = await response.json();
		const produtos = json.produtos;

		if (produtos.length < porPagina) {
			fimDaLista = true;
			document.getElementById("spinner-linha")?.classList.add("hidden");
		}

		renderTabelaProdutos(produtos);
		paginaAtual++;
	} catch (erro) {
		console.error("Erro ao buscar produtos:", erro);
	} finally {
		carregando = false;
		document.getElementById("spinner").classList.add("hidden");
	}
}

function renderTabelaProdutos(produtos) {
	const tbody = document.getElementById("product-table-body");

	produtos.forEach(produto => {
		const tr = document.createElement("tr");
		tr.className = "hover:bg-gray-50 transition animate-fade-in";
		tr.innerHTML = `
			<td class="px-4 py-3"><input type="checkbox" class="item-checkbox form-checkbox"></td>
			<td class="px-4 py-3">${produto.id_produto}</td>
			<td class="px-4 py-3">${produto.nome_produto}</td>
			<td class="px-4 py-3">${produto.codigo_interno_produto}</td>
			<td class="px-4 py-3">${produto.estoque_produto}</td>
			<td class="px-4 py-3">${produto.status_produto}</td>
			<td class="px-4 py-3 text-center space-x-2">
				<button onclick="verProduto('${produto.id_produto}')" class="text-blue-500 hover:text-blue-700">👁️</button>
				<button onclick="editarProduto('${produto.id_produto}')" class="text-yellow-500 hover:text-yellow-700">✏️</button>
				<button onclick="inativarProduto('${produto.id_produto}')" class="text-red-500 hover:text-red-700">🚫</button>
			</td>
		`;
		tbody.appendChild(tr);
	});

	document.getElementById("contagemVisivel").innerHTML =
		`Mostrando <strong>${document.querySelectorAll("#product-table-body tr").length}</strong> Produtos`;

	toggleBulkActions();
}

// 📜 4. Scroll infinito
window.addEventListener("scroll", () => {
	const scrollPos = window.innerHeight + window.scrollY;
	const totalHeight = document.body.offsetHeight;

	if (scrollPos >= totalHeight - 100) {
		aplicarFiltrosRemotos();
	}
});

// 🚀 5. Inicialização
document.addEventListener("DOMContentLoaded", () => {
	const checkbox = document.getElementById("ocultarInativos");
	if (checkbox) {
		checkbox.addEventListener("change", () => aplicarFiltrosRemotos(true));
	}

	const inputBusca = document.getElementById("textoBusca");
	if (inputBusca) {
		inputBusca.addEventListener("input", debounce(() => aplicarFiltrosRemotos(true)));
	}

	const selectAll = document.getElementById("select-all");
	if (selectAll) {
		selectAll.addEventListener("change", () => {
			const checkboxes = document.querySelectorAll(".item-checkbox");
			checkboxes.forEach(checkbox => checkbox.checked = selectAll.checked);
			toggleBulkActions();
		});
	}

	const tabela = document.getElementById("product-table-body");
	if (tabela) {
		tabela.addEventListener("change", (event) => {
			if (event.target.classList.contains("item-checkbox")) {
				toggleBulkActions();
			}
		});
	}

	aplicarFiltrosRemotos(true);
});
