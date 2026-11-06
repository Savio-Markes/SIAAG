
/* ==================================================
   SIAAG - JAVASCRIPT PRINCIPAL
   Funcionalidades da tela de login
================================================== */

document.addEventListener("DOMContentLoaded", function () {

    const loginForm = document.getElementById("login-form");
    const loginInput = document.getElementById("login");
    const passwordInput = document.getElementById("senha");

    const togglePassword = document.getElementById("toggle-password");
    const validationMessage = document.getElementById(
        "login-validation-message"
    );

    /* ==============================================
       VALIDAÇÃO VISUAL DO FORMULÁRIO
    ============================================== */

    if (loginForm) {

        loginForm.addEventListener("submit", function (event) {

            const login = loginInput.value.trim();
            const senha = passwordInput.value;

            validationMessage.textContent = "";

            if (login === "" || senha.trim() === "") {

                event.preventDefault();

                validationMessage.textContent =
                    "Informe seu login e sua senha para continuar.";

                if (login === "") {
                    loginInput.focus();
                } else {
                    passwordInput.focus();
                }

                return;
            }

        });

        /* Limpa a mensagem enquanto o usuário corrige os campos */

        loginForm.addEventListener("input", function () {
            validationMessage.textContent = "";
        });

    }

    /* ==============================================
       MOSTRAR / OCULTAR SENHA
    ============================================== */

    if (togglePassword && passwordInput) {

        togglePassword.addEventListener("click", function () {

            const senhaEstaOculta =
                passwordInput.type === "password";

            if (senhaEstaOculta) {

                passwordInput.type = "text";
                togglePassword.textContent = "Ocultar";

                togglePassword.setAttribute(
                    "aria-label",
                    "Ocultar senha"
                );

                togglePassword.setAttribute(
                    "aria-pressed",
                    "true"
                );

            } else {

                passwordInput.type = "password";
                togglePassword.textContent = "Mostrar";

                togglePassword.setAttribute(
                    "aria-label",
                    "Mostrar senha"
                );

                togglePassword.setAttribute(
                    "aria-pressed",
                    "false"
                );

            }

        });

    }

});
