/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

function animateCount(el) {
    const target = Number(el.dataset.kadCount || 0);
    const suffix = el.dataset.kadSuffix || "";
    const valueEl = el.querySelector(".kad-stat__value");
    if (!valueEl || !target) {
        return;
    }
    const duration = 1400;
    const start = performance.now();

    const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(target * eased);
        valueEl.textContent = `${current}${suffix}`;
        if (progress < 1) {
            requestAnimationFrame(tick);
        }
    };
    requestAnimationFrame(tick);
}

publicWidget.registry.KadWebsite = publicWidget.Widget.extend({
    selector: ".kad-site",

    start() {
        this._setupReveals();
        this._setupSmoothAnchors();
        return this._super(...arguments);
    },

    _setupReveals() {
        const nodes = this.el.querySelectorAll(
            ".kad-section__head, .kad-panel, .kad-service, .kad-product-item, .kad-why-item, .kad-stat, .kad-form, .kad-contact-aside"
        );
        nodes.forEach((node) => node.classList.add("kad-reveal"));

        if (!("IntersectionObserver" in window)) {
            nodes.forEach((node) => {
                node.classList.add("is-visible");
                if (node.classList.contains("kad-stat")) {
                    animateCount(node);
                }
            });
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) {
                        return;
                    }
                    entry.target.classList.add("is-visible");
                    if (entry.target.classList.contains("kad-stat")) {
                        animateCount(entry.target);
                    }
                    observer.unobserve(entry.target);
                });
            },
            { threshold: 0.2, rootMargin: "0px 0px -40px 0px" }
        );

        nodes.forEach((node) => observer.observe(node));
    },

    _setupSmoothAnchors() {
        this.el.querySelectorAll('a[href^="#"]').forEach((anchor) => {
            anchor.addEventListener("click", (event) => {
                const id = anchor.getAttribute("href");
                if (!id || id === "#") {
                    return;
                }
                const target = document.querySelector(id);
                if (!target) {
                    return;
                }
                event.preventDefault();
                const headerOffset = 80;
                const top = target.getBoundingClientRect().top + window.scrollY - headerOffset;
                window.scrollTo({ top, behavior: "smooth" });
            });
        });
    },
});
