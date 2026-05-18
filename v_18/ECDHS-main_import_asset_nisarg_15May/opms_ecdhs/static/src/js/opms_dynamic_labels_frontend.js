(function () {
    "use strict";

    const MAPPING_URL = "/opms/labels/mapping";
    const DEBOUNCE_MS = 140;

    function escapeRegExp(value) {
        return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    function isOpmsPortalPage() {
        const path = window.location.pathname || "";
        return path.startsWith("/my/opms") || path.startsWith("/opms");
    }

    function applyReplacements(replacements) {
        if (!document.body || !isOpmsPortalPage()) {
            return;
        }

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

        const textNodes = [];
        while (walker.nextNode()) {
            textNodes.push(walker.currentNode);
        }

        textNodes.forEach((node) => {
            let value = node.nodeValue;
            replacements.forEach(([source, target]) => {
                if (!source || !target || source === target || value.indexOf(source) === -1) {
                    return;
                }
                value = value.replace(new RegExp(escapeRegExp(source), "g"), target);
            });
            if (value !== node.nodeValue) {
                node.nodeValue = value;
            }
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
        if (!isOpmsPortalPage()) {
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
        } catch (_error) {
            // Keep silent to avoid affecting portal functionality.
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
