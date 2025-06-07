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

async function aplicarFiltrosRemotos(reset = false) {
	if (carregando) return;
	if (fimDaLista && !reset) return;

	const textoBusca = document.getElementById("textoBusca").value.toLowerCase();

	if (reset) {
		paginaAtual = 1;
		fimDaLista = false;
		document.getElementById("product-table-body").innerHTML = "";
		document.getElementById("spinner-linha")?.classList.remove("hidden");
	}

	const url = `/api/movimentacaoProdutos?page=${paginaAtual}&per_page=${porPagina}&busca=${encodeURIComponent(textoBusca)}`;

	carregando = true;
	document.getElementById("spinner").classList.remove("hidden");

	try {
		const response = await fetch(url);
		if (!response.ok) throw new Error(`Erro na requisição: ${response.status}`);

		const json = await response.json();
		const movimentacoes = json.movimentacoes;

		if (movimentacoes.length < porPagina) {
			fimDaLista = true;
			document.getElementById("spinner-linha")?.classList.add("hidden");
		}

		renderTabelaMovimentacoes(movimentacoes);
		paginaAtual++;
	} catch (erro) {
		console.error("Erro ao buscar movimentações:", erro);
	} finally {
		carregando = false;
		document.getElementById("spinner").classList.add("hidden");
	}
}

function renderTabelaMovimentacoes(movimentacoes) {
	const tbody = document.getElementById("product-table-body");

	movimentacoes.forEach(mov => {
		const tr = document.createElement("tr");

		const corFundo = mov.tipo_movimentacao === "Entrada"
			? "bg-green-200"
			: mov.tipo_movimentacao === "Saída"
				? "bg-red-200"
				: "";

		tr.className = `hover:bg-gray-100 transition animate-fade-in ${corFundo}`;
        const data = new Date(mov.data_movimentacao).toLocaleString("pt-BR");
		tr.innerHTML = `
			<td class="px-4 py-3">${mov.id_movimentacao}</td>
			<td class="px-4 py-3">${mov.nome_produto}</td>
			<td class="px-4 py-3">${mov.tipo_movimentacao}</td>
			<td class="px-4 py-3">${mov.quantidade}</td>
			<td class="px-4 py-3">${data}</td>
			<td class="px-4 py-3">${mov.nome_setor}</td>
			<td class="px-4 py-3">${mov.nome_usuario}</td>
			<td class="px-4 py-3 text-center">
				<button onclick="verDetalhes(${mov.id_movimentacao})"
					class="text-blue-600 hover:underline">
					Detalhes
				</button>
			</td>
		`;
		tbody.appendChild(tr);
	});

	document.getElementById("contagemVisivel").innerHTML =
		`Mostrando <strong>${document.querySelectorAll("#product-table-body tr").length}</strong> Movimentações`;
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
	const inputBusca = document.getElementById("textoBusca");
	if (inputBusca) {
		inputBusca.addEventListener("input", debounce(() => aplicarFiltrosRemotos(true)));
	}

	aplicarFiltrosRemotos(true);
});


function verDetalhes(id) {
	window.location.href = `/admin/detalhesMovimentacao/${id}`;
}

function entradaProduto() {
	window.location.href = `entradaProduto`;
}

function saidaProduto() {
	window.location.href = `saidaProduto`;
}

function verDetalhes(id) {
	const modal = document.getElementById("modal-detalhes");
	const conteudo = document.getElementById("modal-conteudo");

	// Exibe o modal com mensagem temporária de carregamento
	conteudo.innerHTML = `<p class="text-gray-500 text-sm">Carregando detalhes...</p>`;
	modal.classList.remove("hidden");
	modal.classList.add("flex");

	fetch(`/api/movimentacaoDetalhes/${id}`)
		.then(res => {
			if (!res.ok) throw new Error("Erro na resposta da API");
			return res.json();
		})
		.then(dados => {
			if (!dados.id_movimentacao) throw new Error("Movimentação não encontrada");

			conteudo.innerHTML = `
				<p><strong>ID:</strong> ${dados.id_movimentacao}</p>
				<p><strong>Produto:</strong> ${dados.nome_produto}</p>
				<p><strong>Tipo:</strong> ${dados.tipo_movimentacao}</p>
				<p><strong>Quantidade:</strong> ${dados.quantidade}</p>
				<p><strong>Data:</strong> ${new Date(dados.data_movimentacao).toLocaleString("pt-BR")}</p>
				<p><strong>Setor:</strong> ${dados.nome_setor || "—"}</p>
				<p><strong>Usuário:</strong> ${dados.nome_usuario || "—"}</p>
				<p><strong>Observação:</strong> ${dados.observacao || "—"}</p>
			`;
		})
		.catch((erro) => {
			console.error(erro);
			conteudo.innerHTML = `<p class="text-red-600">Erro ao carregar os detalhes da movimentação.</p>`;
		});
}

function fecharModal() {
	const modal = document.getElementById("modal-detalhes");
	modal.classList.add("hidden");
	modal.classList.remove("flex");
}

