/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { Many2ManyBinaryField } from "@web/views/fields/many2many_binary/many2many_binary_field";

patch(Many2ManyBinaryField.prototype, {
    getUrl(id) {
        // Safely check if element exists before reading classList
        const hasNoDownloadClass = this.el && (
            this.el.classList.contains("no-download") ||
            this.el.closest(".no-download")
        );
        console.log(hasNoDownloadClass, 'hasNoDownloadClass')

//        if ( not hasNoDownloadClass) {
//        }
        return hasNoDownloadClass
            ? `/web/content/${id}`  // open preview
            : `/web/content/${id}?download=true`;  // default download
    },
});
