document.addEventListener("DOMContentLoaded", function () {
    // Variáveis globais
    let contadorProduto = typeof contadorProdutoInicial !== 'undefined' ? contadorProdutoInicial : 0;

    // Preenche data atual
    const hoje = new Date().toISOString().split('T')[0];
    document.querySelector('input[name="data_recebimento"]').value = hoje;

    const freteInput = document.getElementById("valor-frete");
    const totalInput = document.getElementById("valor-total");

    // Função para calcular total
    function calcularTotal() {
        let total = 0;

        const produtoInputs = document.querySelectorAll("input[name^='produto']");
        produtoInputs.forEach(produtoInput => {
            const id = produtoInput.name.replace("produto", "");
            const quantidade = parseFloat(document.querySelector(`input[name='quantidade${id}']`)?.value || 0);
            const preco = parseFloat(document.querySelector(`input[name='preco${id}']`)?.value.replace(",", ".") || 0);
            total += quantidade * preco;
        });

        const frete = parseFloat(freteInput?.value.replace(",", ".") || 0);
        total += frete;

        totalInput.value = total.toFixed(2).replace(".", ",");
    }

    // Aplica cálculo automático em todos os inputs relevantes
    document.querySelectorAll("input[name^='quantidade'], input[name^='preco'], #valor-frete").forEach(input => {
        input.addEventListener("input", calcularTotal);
    });

    // Botão de adicionar novo produto
    document.getElementById("adicionar-produto").addEventListener("click", function () {
        contadorProduto++;

        const tbody = document.getElementById("lista-produtos");
        const novaLinha = document.createElement("tr");

        novaLinha.innerHTML = `
            <td class="px-4 py-2"><input type="text" class="w-full border border-gray-300 rounded px-2 py-1" name="produto${contadorProduto}" placeholder="Nome do Produto"></td>
            <td class="px-4 py-2 w-40"><select
                    id="unidade${contadorProduto}"
                    name="unidade${contadorProduto}"
                    required
                    class="w-full border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                </select></td>
            <td class="px-4 py-2 w-10"><input type="number" class="w-full border border-gray-300 rounded px-2 py-1" name="quantidade${contadorProduto}" value="0" min="0"></td>
            <td class="px-4 py-2 w-40"><input type="text" class="w-full border border-gray-300 rounded px-2 py-1" name="preco${contadorProduto}" placeholder="0.00"></td>
            <td class="px-4 py-2"><button type="button" class="text-red-600 font-bold border border-red-300 rounded px-4 py-1 h-[34px] hover:bg-red-100 transition btn-remover-produto">x</button></td>
        `;

        tbody.appendChild(novaLinha);

        // Reaplica eventos
        novaLinha.querySelectorAll("input").forEach(input => {
            input.addEventListener("input", calcularTotal);
        });

        novaLinha.querySelector(".btn-remover-produto").addEventListener("click", removerLinha);
    });

    // Função para remover produto
    function removerLinha(event) {
        const linha = event.target.closest("tr");
        if (linha) {
            linha.remove();
            calcularTotal();
        }
    }

    // Adiciona eventos aos botões já existentes
    document.querySelectorAll(".btn-remover-produto").forEach(botao => {
        botao.addEventListener("click", removerLinha);
    });

    // Calcula total na primeira carga
    calcularTotal();

    // Confirmação de envio
    document.getElementById("form-recebimento").addEventListener("submit", function (event) {
        const confirmacao = confirm("Deseja realmente gravar o recebimento?");
        if (!confirmacao) {
            event.preventDefault();
        }

        // Converte vírgulas em pontos
        document.querySelectorAll("input[name^='preco'], input[name^='quantidade'], #valor-frete, #valor-total").forEach(campo => {
            campo.value = campo.value.replace(",", ".");
        });
    });
});
