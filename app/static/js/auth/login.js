
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    const passwordInput = document.getElementById("senha");
    const togglePassword = document.getElementById("togglePassword");
    const submitButton = document.getElementById("loginSubmit");

    if (!form) return;

    // Exibir ou ocultar a senha
    if (passwordInput && togglePassword) {
        togglePassword.addEventListener("click", () => {
            const senhaVisivel = passwordInput.type === "text";

            passwordInput.type = senhaVisivel ? "password" : "text";
            togglePassword.textContent = senhaVisivel ? "Exibir" : "Ocultar";

            togglePassword.setAttribute(
                "aria-label",
                senhaVisivel ? "Exibir senha" : "Ocultar senha"
            );

            passwordInput.focus();
        });
    }

    // Estado de carregamento durante o envio ao backend
    form.addEventListener("submit", (event) => {
        if (!form.checkValidity()) {
            return;
        }

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.setAttribute("aria-busy", "true");
            submitButton.textContent = "Entrando...";
        }
    });
});
