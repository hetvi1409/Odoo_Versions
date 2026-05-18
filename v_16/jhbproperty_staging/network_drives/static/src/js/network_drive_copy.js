/** @odoo-module **/

import { registry } from "@web/core/registry/action";
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";

patch(ListController.prototype, {
    setup() {
        this._super(...arguments);
    },

    async onClickButton(ev) {
        const button = ev.target.closest('.btn_open_file_url');
        console.log("\n\n=====button===",button)
        if (button) {
            const record = this.getSelectedRecords()[0];
            const filePath = record?.data?.file_path;
            if (filePath?.startsWith("file://")) {
                window.open(filePath, "_blank");
            } else {
                this.displayNotification({ type: 'warning', message: "Invalid file path URL." });
            }
            return;
        }

        return this._super(...arguments);
    },
});
