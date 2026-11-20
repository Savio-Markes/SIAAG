
/* =====================================================
   SIAAG — JAVASCRIPT PRINCIPAL
   IFPI — Campus Paulistana
   Navegação e menu lateral
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // ELEMENTOS DO MENU
    const sidebar = document.querySelector(".sidebar");
    const menuToggle = document.querySelector(".menu-toggle");
    const sidebarOverlay = document.querySelector(".sidebar-overlay");

    // VERIFICA SE OS ELEMENTOS EXISTEM
    if (!sidebar || !menuToggle || !sidebarOverlay) {
        return;
    }

    // ABRIR MENU
    function abrirMenu() {
        sidebar.classList.add("open");
        sidebarOverlay.classList.add("active");

        menuToggle.setAttribute("aria-expanded", "true");
        document.body.style.overflow = "hidden";
    }

    // FECHAR MENU
    function fecharMenu() {
        sidebar.classList.remove("open");
        sidebarOverlay.classList.remove("active");

        menuToggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
    }

    // ALTERNAR MENU
    function alternarMenu() {
        const menuAberto = sidebar.classList.contains("open");

        if (menuAberto) {
            fecharMenu();
        } else {
            abrirMenu();
        }
    }

    // BOTÃO DE ABRIR/FECHAR
    menuToggle.addEventListener("click", alternarMenu);

    // FECHAR AO CLICAR NO FUNDO
    sidebarOverlay.addEventListener("click", fecharMenu);

    // FECHAR AO ACESSAR UMA OPÇÃO
    const menuLinks = sidebar.querySelectorAll(".navigation-link");

    menuLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.innerWidth <= 900) {
                fecharMenu();
            }
        });
    });

    // FECHAR COM ESC
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            fecharMenu();
        }
    });

    // FECHAR AO VOLTAR PARA DESKTOP
    window.addEventListener("resize", function () {
        if (window.innerWidth > 900) {
            fecharMenu();
        }
    });

    // ESTADO INICIAL
    menuToggle.setAttribute("aria-expanded", "false");

});
