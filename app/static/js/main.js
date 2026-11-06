
// ========================================
// SIAAG - JAVASCRIPT PRINCIPAL
// IFPI - Campus Paulistana
// ========================================

document.addEventListener("DOMContentLoaded", function () {

    // Elementos do menu lateral
    const sidebar = document.querySelector(".sidebar");
    const menuToggle = document.querySelector(".menu-toggle");
    const sidebarOverlay = document.querySelector(".sidebar-overlay");


    // 1. ABRIR E FECHAR O MENU

    function abrirMenu() {
        if (!sidebar || !sidebarOverlay) return;

        sidebar.classList.add("open");
        sidebarOverlay.classList.add("active");

        document.body.style.overflow = "hidden";
    }

    function fecharMenu() {
        if (!sidebar || !sidebarOverlay) return;

        sidebar.classList.remove("open");
        sidebarOverlay.classList.remove("active");

        document.body.style.overflow = "";
    }


    // 2. BOTÃO DE ABRIR MENU

    if (menuToggle) {
        menuToggle.addEventListener("click", function () {
            abrirMenu();
        });
    }


    // 3. FECHAR AO CLICAR FORA DO MENU

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener("click", function () {
            fecharMenu();
        });
    }


    // 4. FECHAR AO SELECIONAR UMA OPÇÃO

    if (sidebar) {
        const menuLinks = sidebar.querySelectorAll(".menu-link");

        menuLinks.forEach(function (link) {
            link.addEventListener("click", function () {
                fecharMenu();
            });
        });
    }


    // 5. FECHAR COM A TECLA ESC

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {
            fecharMenu();
        }

    });


    // 6. AJUSTE AO VOLTAR PARA DESKTOP

    window.addEventListener("resize", function () {

        if (window.innerWidth > 900) {
            fecharMenu();
        }

    });

});