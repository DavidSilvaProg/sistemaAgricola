document.getElementById("form-recebimento").addEventListener("submit", function(event) {
    const confirmacao = confirm("Deseja realmente gravar o recebimento?");
    if (!confirmacao) {
        event.preventDefault(); // cancela o envio
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const hoje = new Date().toISOString().split('T')[0]; // formato: YYYY-MM-DD
    document.querySelector('input[name="data_recebimento"]').value = hoje;
});

document.getElementById("form-recebimento").addEventListener("submit", function () {
    const camposPreco = document.querySelectorAll("input[name^='preco']");
    camposPreco.forEach(function (campo) {
        campo.value = campo.value.replace(",", ".");
    });
});