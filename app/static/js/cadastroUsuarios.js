document.querySelectorAll('.toggle-password').forEach(function(toggle) {
    toggle.addEventListener('click', function() {
        const input = document.querySelector(this.getAttribute('toggle'));
        const img = this.querySelector('img');

        if (input.type === "password") {
            input.type = "text";
            img.src = "/static/invisivel.png"; // troca para o olho fechado
            img.alt = "hidden";
        } else {
            input.type = "password";
            img.src = "/static/visivel.png"; // troca para o olho aberto
            img.alt = "visible";
        }
    });
});

// Função para validar se as senhas são iguais
document.querySelector('form').addEventListener('submit', function(e) {
    const senha = document.getElementById('senha').value;
    const confirmarSenha = document.getElementById('confirmar_senha').value;

    if (senha !== confirmarSenha) {
        e.preventDefault(); // Impede envio do formulário
        alert('As senhas não coincidem!');
    }
});