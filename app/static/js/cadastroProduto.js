document.addEventListener("DOMContentLoaded", function () {
		const precoInput = document.getElementById("preco_unitario_produto");

		precoInput.addEventListener("input", function (e) {
			let value = e.target.value.replace(/\D/g, "");

			// Converte para centavos
			value = (parseInt(value, 10) / 100).toFixed(2);

			// Formata como moeda brasileira
			const formatted = new Intl.NumberFormat("pt-BR", {
				style: "currency",
				currency: "BRL"
			}).format(value);

			e.target.value = formatted;
		});

		// Remove a formatação ao focar para facilitar edição
		precoInput.addEventListener("focus", function (e) {
			const value = e.target.value.replace(/\D/g, "");
			e.target.value = value ? (parseInt(value, 10) / 100).toFixed(2).replace(".", ",") : "";
		});

		// Reaplica a máscara ao sair do campo
		precoInput.addEventListener("blur", function (e) {
			let value = e.target.value.replace(/\D/g, "");
			if (!value) return;

			value = (parseInt(value, 10) / 100).toFixed(2);
			const formatted = new Intl.NumberFormat("pt-BR", {
				style: "currency",
				currency: "BRL"
			}).format(value);

			e.target.value = formatted;
		});
	});