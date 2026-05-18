/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SignRefusalDialog } from "@sign/dialogs/sign_refusal_dialog";
import { _t } from "@web/core/l10n/translation";

/**
 * Patch SignRefusalDialog to enforce that the refusal reason contains
 * at least one real word (two or more consecutive alphabetic characters).
 * Single characters, punctuation-only input, and whitespace-only input
 * are rejected both in the UI (button stays disabled, hint shown) and
 * as a guard in the refuse() method itself.
 */
const WORD_RE = /[a-zA-Z]{2,}/;

function hasValidReason(value) {
    return WORD_RE.test(value.trim());
}

function getOrCreateHint(textarea) {
    let hint = textarea.nextElementSibling;
    if (!hint || !hint.classList.contains("o_refuse_reason_hint")) {
        hint = document.createElement("div");
        hint.className = "o_refuse_reason_hint small mt-1";
        textarea.insertAdjacentElement("afterend", hint);
    }
    return hint;
}

patch(SignRefusalDialog.prototype, {
    /**
     * Override: disable the Refuse button and show a contextual hint
     * unless the typed reason contains at least one real word.
     */
    checkForChanges() {
        const value = this.refuseReasonEl.el.value.trim();
        const valid = hasValidReason(value);

        this.refuseButton.el.disabled = valid ? "" : "disabled";

        const hint = getOrCreateHint(this.refuseReasonEl.el);
        if (value.length === 0) {
            hint.className = "o_refuse_reason_hint small mt-1 text-muted";
            hint.textContent = _t("A reason is required before you can refuse.");
        } else if (!valid) {
            hint.className = "o_refuse_reason_hint small mt-1 text-danger";
            hint.textContent = _t(
                "Please type an actual reason using real words " +
                "(a single character or punctuation alone is not accepted)."
            );
        } else {
            hint.className = "o_refuse_reason_hint small mt-1 text-success";
            hint.textContent = _t("Reason accepted.");
        }
    },

    /**
     * Override: guard against submission if the reason is still invalid
     * (e.g. if the button state was bypassed).
     */
    async refuse() {
        const value = this.refuseReasonEl.el.value.trim();
        if (!hasValidReason(value)) {
            // Ensure the hint is visible with the error state
            this.checkForChanges();
            return;
        }
        return super.refuse();
    },
});
