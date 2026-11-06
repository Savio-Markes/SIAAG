
// ========================================
// SIAAG - JAVASCRIPT DA TELA DE LOGIN
// IFPI - Campus Paulistana
// ========================================

document.addEventListener("DOMContentLoaded", function () {

    // Elementos da tela
    const passwordInput = document.getElementById("senha");
    const togglePassword = document.getElementById("togglePassword");

    const loginForm = document.getElementById("loginForm");
    const loginButton = document.getElementById("loginButton");

    const buttonText = loginButton
        ? loginButton.querySelector(".button-text")
        : null;

    const buttonLoading = loginButton
        ? loginButton.querySelector(".button-loading")
        : null;


    // 1. MOSTRAR OU OCULTAR SENHA

    if (passwordInput && togglePassword) {

        togglePassword.addEventListener("click", function () {

            const senhaVisivel =
                passwordInput.type === "text";

            passwordInput.type = senhaVisivel
                ? "password"
                : "text";

            togglePassword.textContent = senhaVisivel
                ? "Mostrar"
                : "Ocultar";

            togglePassword.setAttribute(
                "aria-label",
                senhaVisivel ? "Mostrar senha" : "Ocultar senha"
            );

        });

    }


    // 2. INDICADOR DE ENVIO DO FORMULÁRIO

    if (loginForm && loginButton) {

        loginForm.addEventListener("submit", function () {

            // Evita cliques repetidos durante o envio
            loginButton.disabled = true;

            // Atualiza o texto do botão
            if (buttonText) {
                buttonText.hidden = true;
            }

            if (buttonLoading) {
                buttonLoading.hidden = false;
            }

        });

    }

});
