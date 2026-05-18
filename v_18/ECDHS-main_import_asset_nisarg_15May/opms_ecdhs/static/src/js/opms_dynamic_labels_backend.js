/** @odoo-module **/

(function () {
    "use strict";

    const MAPPING_URL = "/opms/labels/mapping";
    const DEBOUNCE_MS = 120;

    function escapeRegExp(value) {
        return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    function shouldRunOnThisPage() {
        const hash = window.location.hash || "";
        const path = window.location.pathname || "";
        const opmsInHash = hash.includes("opms.") || hash.includes("opms_") || hash.includes("opms_ecdhs");
        const opmsInPath = path.includes("/odoo/opms") || path.includes("/web#action=opms");
        const hasOpmsBrand = !!document.querySelector(".o_app[data-menu-xmlid*='opms_ecdhs'], .o_menu_brand");
        return opmsInHash || opmsInPath || hasOpmsBrand;
    }

    function replaceAttributes(element, replacements) {
        ["placeholder", "title", "aria-label"].forEach((attr) => {
            const current = element.getAttribute(attr);
            if (!current) {
                return;
            }
            let updated = current;
            replacements.forEach(([source, target]) => {
                if (!source || !target || source === target || updated.indexOf(source) === -1) {
                    return;
                }
                updated = updated.replace(new RegExp(escapeRegExp(source), "g"), target);
            });
            if (updated !== current) {
                element.setAttribute(attr, updated);
            }
        });
    }

    function applyReplacements(replacements) {
        if (!shouldRunOnThisPage()) {
            return;
        }

        const textNodes = [];
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
            acceptNode(node) {
                if (!node || !node.nodeValue || !node.nodeValue.trim()) {
                    return NodeFilter.FILTER_REJECT;
                }
                const parentTag = node.parentElement && node.parentElement.tagName;
                if (["SCRIPT", "STYLE", "NOSCRIPT", "TEXTAREA"].includes(parentTag)) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            },
        });

        while (walker.nextNode()) {
            textNodes.push(walker.currentNode);
        }

        textNodes.forEach((node) => {
            let nextValue = node.nodeValue;
            replacements.forEach(([source, target]) => {
                if (!source || !target || source === target || nextValue.indexOf(source) === -1) {
                    return;
                }
                nextValue = nextValue.replace(new RegExp(escapeRegExp(source), "g"), target);
            });
            if (nextValue !== node.nodeValue) {
                node.nodeValue = nextValue;
            }
        });

        document.querySelectorAll("input, textarea, button, a, label, span, div, th, td, option").forEach((element) => {
            replaceAttributes(element, replacements);
        });
    }

    function debounce(fn, wait) {
        let timeoutId = null;
        return function debounced() {
            window.clearTimeout(timeoutId);
            timeoutId = window.setTimeout(() => fn(), wait);
        };
    }

    async function boot() {
        if (!document.body || !shouldRunOnThisPage()) {
            return;
        }

        try {
            const response = await fetch(MAPPING_URL, { credentials: "same-origin" });
            if (!response.ok) {
                return;
            }
            const payload = await response.json();
            const replacements = Object.entries((payload && payload.replacements) || {})
                .filter(([source, target]) => source && target && source !== target)
                .sort((a, b) => b[0].length - a[0].length);

            if (!replacements.length) {
                return;
            }

            const run = () => applyReplacements(replacements);
            run();

            const observer = new MutationObserver(debounce(run, DEBOUNCE_MS));
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                characterData: true,
            });

            window.addEventListener("hashchange", run);
        } catch (_error) {
            // Keep silent to avoid breaking OPMS pages if mapping is temporarily unavailable.
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
