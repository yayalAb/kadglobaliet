/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

/**
 * Odoo website scrolls inside #wrapwrap, not window.
 * Using window.scrollTo / default IntersectionObserver root breaks
 * both CTA buttons and reveal animations.
 */
function getScrollRoot() {
    return document.getElementById("wrapwrap") || document.scrollingElement || document.documentElement;
}

function scrollToTarget(target, headerOffset = 88) {
    const root = getScrollRoot();
    if (!target || !root) {
        return;
    }

    if (root === document.body || root === document.documentElement || root === document.scrollingElement) {
        const top = target.getBoundingClientRect().top + window.pageYOffset - headerOffset;
        window.scrollTo({ top, behavior: "smooth" });
        return;
    }

    const rootRect = root.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    const top = targetRect.top - rootRect.top + root.scrollTop - headerOffset;
    root.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
}

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
        valueEl.textContent = `${Math.round(target * eased)}${suffix}`;
        if (progress < 1) {
            requestAnimationFrame(tick);
        }
    };
    requestAnimationFrame(tick);
}

publicWidget.registry.KadWebsite = publicWidget.Widget.extend({
    selector: ".kad-site",
    events: {
        "click a[href^='#']": "_onAnchorClick",
    },

    start() {
        this.el.classList.add("kad-js-ready");
        this._setupReveals();
        this._bindGlobalAnchors();
        return this._super(...arguments);
    },

    destroy() {
        if (this._globalClickHandler) {
            document.removeEventListener("click", this._globalClickHandler, true);
            this._globalClickHandler = null;
        }
        return this._super(...arguments);
    },

    _bindGlobalAnchors() {
        // Header / footer menus live outside .kad-site
        this._globalClickHandler = (event) => {
            const anchor = event.target.closest("a[href^='#']");
            if (!anchor || !document.querySelector(".kad-site")) {
                return;
            }
            this._scrollFromAnchor(event, anchor);
        };
        document.addEventListener("click", this._globalClickHandler, true);
    },

    _onAnchorClick(event) {
        this._scrollFromAnchor(event, event.currentTarget);
    },

    _scrollFromAnchor(event, anchor) {
        const id = anchor.getAttribute("href");
        if (!id || id === "#" || !id.startsWith("#")) {
            return;
        }
        const target = document.querySelector(id);
        if (!target) {
            return;
        }
        event.preventDefault();
        event.stopPropagation();
        scrollToTarget(target);
        if (history.replaceState) {
            history.replaceState(null, "", id);
        }
    },

    _setupReveals() {
        const nodes = this.el.querySelectorAll(
            ".kad-section__head, .kad-panel, .kad-service, .kad-product-item, .kad-why-item, .kad-stat, .kad-form, .kad-contact-aside, .kad-hero__copy"
        );
        nodes.forEach((node) => node.classList.add("kad-reveal"));

        const revealNow = (node) => {
            node.classList.add("is-visible");
            if (node.classList.contains("kad-stat")) {
                animateCount(node);
            }
        };

        if (!("IntersectionObserver" in window)) {
            nodes.forEach(revealNow);
            return;
        }

        const scrollRoot = getScrollRoot();
        const observerRoot =
            scrollRoot && scrollRoot !== document.documentElement && scrollRoot !== document.body
                ? scrollRoot
                : null;

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) {
                        return;
                    }
                    revealNow(entry.target);
                    observer.unobserve(entry.target);
                });
            },
            {
                root: observerRoot,
                threshold: 0.12,
                rootMargin: "0px 0px -8% 0px",
            }
        );

        nodes.forEach((node) => observer.observe(node));

        // Reveal anything already in view on first paint
        requestAnimationFrame(() => {
            nodes.forEach((node) => {
                const rect = node.getBoundingClientRect();
                const viewH = (observerRoot || window).clientHeight || window.innerHeight;
                if (rect.top < viewH * 0.92 && rect.bottom > 0) {
                    revealNow(node);
                    observer.unobserve(node);
                }
            });
        });
    },
});
