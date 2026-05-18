/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

patch(ListController.prototype, {

    setup() {
        super.setup(...arguments);
        this.dialog = useService("dialog");
    },

    async onDeleteSelectedRecords() {
        // Only for sale.order
        if (this.model.root.resModel !== "sale.order") {
            return super.onDeleteSelectedRecords(...arguments);
        }

        const selectedRecords = this.model.root.selection;
        const names = selectedRecords
            .map((r) => r.data.name)
            .join(", ");

        // Show custom confirm dialog
        return new Promise((resolve) => {
            this.dialog.add(
                ConfirmationDialog,
                {
                    title: _t("Delete Sale Orders?"),
                    body: _t(
                        `Are you sure you want to delete: ${names}?
                         This cannot be undone!`
                    ),
                    confirm: async () => {
                        await super.onDeleteSelectedRecords(...arguments);
                        resolve();
                    },
                    cancel: () => resolve(),
                }
            );
        });
    },
});