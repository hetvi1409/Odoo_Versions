/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { SurveyForm } from "@survey/interactions/survey_form";

patch(SurveyForm.prototype, {
    onSubmit(ev) {
        ev.preventDefault();
        const targetEl = ev.currentTarget;
        if (targetEl.value === "previous") {
            this.submitForm({ previousPageId: parseInt(targetEl.dataset.previousPageId) });
        } else if (targetEl.value === "next_skipped") {
            this.submitForm({ nextSkipped: true });
        } else if (targetEl.value === "finish" && !this.options.sessionInProgress) {
            this.dialog.add(ConfirmationDialog, {
                title: _t("Submit confirmation"),
                body: _t("Are you sure you want to submit the application?"),
                confirmLabel: _t("Submit"),
                confirm: () => {
                    this.waitForTimeout(() => this.submitForm({ isFinish: true }), 0);
                },
                cancel: () => {},
            });
        } else {
            this.submitForm();
        }
    },
});
