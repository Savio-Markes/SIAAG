
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    const passwordInput = document.getElementById("senha");
    const togglePassword = document.getElementById("togglePassword");
    const submitButton = document.getElementById("loginSubmit");
    const submitText = document.getElementById("loginSubmitText");
    const loading = document.getElementById("loginLoading");

    if (!form) return;

    if (passwordInput && togglePassword) {
        togglePassword.addEventListener("click", () => {
            const mostrar = passwordInput.type === "password";

            passwordInput.type = mostrar ? "text" : "password";
            togglePassword.textContent = mostrar ? "Ocultar" : "Exibir";

            togglePassword.setAttribute(
                "aria-label",
                mostrar ? "Ocultar senha" : "Exibir senha"
            );

            togglePassword.setAttribute(
                "aria-pressed",
                String(mostrar)
            );

            passwordInput.focus();
        });
    }

    form.addEventListener("submit", () => {
        if (!form.checkValidity()) return;

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.setAttribute("aria-busy", "true");
        }

        if (submitText) submitText.hidden = true;
        if (loading) loading.hidden = false;
    });
});
