
/* =====================================================
   SIAAG — VALIDAÇÕES VISUAIS REUTILIZÁVEIS
   Não intercepta o envio dos formulários.
   A validação definitiva deve ser feita pelo backend.
   ===================================================== */

document.addEventListener("DOMContentLoaded", () => {
    inicializarContadores();
    inicializarLimitesDeData();
    inicializarIndicadoresDeCampo();
});

/* =====================================================
   1. CONTADORES DE CARACTERES
   ===================================================== */

function inicializarContadores() {
    const campos = document.querySelectorAll("[data-character-counter]");

    campos.forEach(campo => {
        const contadorId = campo.dataset.characterCounter;
        const contador = document.getElementById(contadorId);

        if (!contador) return;

        const atualizar = () => {
            const limite = campo.maxLength;
            const quantidade = campo.value.length;

            contador.textContent = limite > 0
                ? `${quantidade}/${limite} caracteres`
                : `${quantidade} caracteres`;

            contador.classList.toggle(
                "is-limit-reached",
                limite > 0 && quantidade >= limite
            );
        };

        campo.addEventListener("input", atualizar);
        atualizar();
    });
}

/* =====================================================
   2. LIMITES DE DATA
   ===================================================== */

function inicializarLimitesDeData() {
    const hoje = obterDataLocal();

    document.querySelectorAll('input[type="date"][data-max-today]')
        .forEach(campo => {
            campo.max = hoje;
        });

    document.querySelectorAll('input[type="date"][data-min-today]')
        .forEach(campo => {
            campo.min = hoje;
        });
}

function obterDataLocal() {
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = String(hoje.getMonth() + 1).padStart(2, "0");
    const dia = String(hoje.getDate()).padStart(2, "0");

    return `${ano}-${mes}-${dia}`;
}

/* =====================================================
   3. INDICADORES DE CAMPOS OBRIGATÓRIOS
   ===================================================== */

function inicializarIndicadoresDeCampo() {
    document.querySelectorAll("input, select, textarea")
        .forEach(campo => {
            if (!campo.required) return;

            const rotulo = document.querySelector(
                `label[for="${campo.id}"]`
            );

            if (!rotulo || rotulo.querySelector(".required-indicator")) {
                return;
            }

            const indicador = document.createElement("span");
            indicador.className = "required-indicator";
            indicador.textContent = " *";
            indicador.setAttribute("aria-hidden", "true");

            rotulo.appendChild(indicador);
        });
}
