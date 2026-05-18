/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { FormViewDialog } from "@web/views/form_view/form_view_dialog";

// Keep the Compliance Check modal open after Save
patch(FormViewDialog.prototype, "sa_government_tender.keep_open_compliance", {
    setup() {
        // call original setup
        const res = this._super(...arguments);
        try {
            // Only affect our compliance check model
            if (this.props && this.props.resModel === "sagovtender.compliance.check") {
                // Prevent closing the dialog after Save
                this.props.closeOnSave = false;
            }
        } catch (e) {
            // Fail-safe: do nothing if structure changes
        }
        return res;
    },
});
