
/**
 * SIAAG — Confirmações de ações
 * IFPI — Campus Paulistana
 *
 * Para utilizar:
 * Adicione data-confirm="mensagem" ao botão
 * ou formulário que precisa de confirmação.
 */

document.addEventListener("DOMContentLoaded", () => {

    /**
     * Confirma ações em formulários.
     */
    document.addEventListener("submit", (event) => {
        const formulario = event.target;

        if (!(formulario instanceof HTMLFormElement)) {
            return;
        }

        const mensagem = formulario.dataset.confirm;

        if (!mensagem) {
            return;
        }

        const confirmado = window.confirm(mensagem);

        if (!confirmado) {
            event.preventDefault();
        }
    });

    /**
     * Confirma ações em botões e links.
     */
    document.addEventListener("click", (event) => {
        const elemento = event.target.closest("[data-confirm]");

        if (!elemento) {
            return;
        }

        // Formulários são tratados no evento submit.
        if (
            elemento instanceof HTMLFormElement ||
            elemento.type === "submit"
        ) {
            return;
        }

        const mensagem = elemento.dataset.confirm;

        if (!mensagem) {
            return;
        }

        const confirmado = window.confirm(mensagem);

        if (!confirmado) {
            event.preventDefault();
            event.stopPropagation();
        }
    });

});
