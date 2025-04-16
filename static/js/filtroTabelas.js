let ordemCrescenteGlobal = {};

document.querySelectorAll('th.ordenavel').forEach(th => {
    th.style.cursor = 'pointer';
    th.addEventListener('click', function () {
        const tabela = th.closest('table');
        const coluna = parseInt(th.getAttribute('data-coluna'));
        const idTabela = tabela.id;

        if (!ordemCrescenteGlobal[idTabela]) {
            ordemCrescenteGlobal[idTabela] = {};
        }

        const asc = !ordemCrescenteGlobal[idTabela][coluna];
        ordemCrescenteGlobal[idTabela][coluna] = asc;

        const linhas = Array.from(tabela.tBodies[0].rows);

        linhas.sort((a, b) => {
            const aTexto = a.cells[coluna].innerText.toLowerCase();
            const bTexto = b.cells[coluna].innerText.toLowerCase();

            const aVal = isNaN(Date.parse(aTexto)) ? (isNaN(aTexto) ? aTexto : parseFloat(aTexto)) : Date.parse(aTexto);
            const bVal = isNaN(Date.parse(bTexto)) ? (isNaN(bTexto) ? bTexto : parseFloat(bTexto)) : Date.parse(bTexto);

            if (aVal < bVal) return asc ? -1 : 1;
            if (aVal > bVal) return asc ? 1 : -1;
            return 0;
        });

        linhas.forEach(linha => tabela.tBodies[0].appendChild(linha));
    });
});

function filtrarTabela(inputElement) {
    const filtro = inputElement.value.toLowerCase();
    const idTabela = inputElement.getAttribute("data-tabela");
    const tabela = document.getElementById(idTabela);
    const linhas = tabela.getElementsByTagName("tr");

    for (let i = 1; i < linhas.length; i++) {
        let colunas = linhas[i].getElementsByTagName("td");
        let corresponde = false;

        for (let j = 0; j < colunas.length; j++) {
            if (colunas[j]) {
                let texto = colunas[j].textContent || colunas[j].innerText;
                if (texto.toLowerCase().indexOf(filtro) > -1) {
                    corresponde = true;
                    break;
                }
            }
        }

        linhas[i].style.display = corresponde ? "" : "none";
    }
}