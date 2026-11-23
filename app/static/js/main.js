
/* =====================================================
   SIAAG — JAVASCRIPT PRINCIPAL
   Navegação e menu lateral
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const appLayout = document.querySelector(".app-layout");
    const sidebar = document.querySelector(".sidebar");
    const menuToggle = document.querySelector(".menu-toggle");
    const sidebarOverlay = document.querySelector(".sidebar-overlay");

    if (!appLayout || !sidebar || !menuToggle || !sidebarOverlay) {
        return;
    }

    const MOBILE_WIDTH = 900;

    function atualizarBotao() {
        const mobile = window.innerWidth <= MOBILE_WIDTH;
        const aberto = mobile
            ? sidebar.classList.contains("open")
            : !appLayout.classList.contains("sidebar-collapsed");

        menuToggle.setAttribute("aria-expanded", String(aberto));
        menuToggle.setAttribute(
            "aria-label",
            aberto ? "Ocultar menu de navegação" : "Mostrar menu de navegação"
        );

        menuToggle.title = aberto
            ? "Ocultar menu"
            : "Mostrar menu";
        
        menuToggle.textContent = aberto ? "☰" : "☰";
    }

    function abrirMenuMobile() {
        sidebar.classList.add("open");
        sidebarOverlay.classList.add("active");
        document.body.style.overflow = "hidden";
        atualizarBotao();
    }

    function fecharMenuMobile() {
        sidebar.classList.remove("open");
        sidebarOverlay.classList.remove("active");
        document.body.style.overflow = "";
        atualizarBotao();
    }

    function alternarMenu() {
        if (window.innerWidth <= MOBILE_WIDTH) {
            if (sidebar.classList.contains("open")) {
                fecharMenuMobile();
            } else {
                abrirMenuMobile();
            }
            return;
        }

        appLayout.classList.toggle("sidebar-collapsed");
        atualizarBotao();
    }

    menuToggle.addEventListener("click", alternarMenu);

    sidebarOverlay.addEventListener("click", fecharMenuMobile);

    sidebar.querySelectorAll(".navigation-link").forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.innerWidth <= MOBILE_WIDTH) {
                fecharMenuMobile();
            }
        });
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            fecharMenuMobile();
        }
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > MOBILE_WIDTH) {
            fecharMenuMobile();
        }

        atualizarBotao();
    });

    atualizarBotao();
});
