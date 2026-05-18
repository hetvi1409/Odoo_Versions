/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import {
    inspectorFields,
    DocumentsInspector,
} from "@documents/views/inspector/documents_inspector";

inspectorFields.push("jmc_number");
inspectorFields.push("erf_number");
inspectorFields.push("address");
inspectorFields.push("jmc_property_id");
inspectorFields.push("general_type");
//, "erf_number", "address");
patch(DocumentsInspector.prototype, "documents_update_documents_inspector", {
    /**
     * @override
     */
    setup() {
        this._super(...arguments);
        this.orm = useService("orm");
        this.notification = useService("notification");
    },
    async OnclickJMCNumber() {
        console.log('this', this)
        const record = this.props.selection[0];
            await this.orm.call("documents.document", "update_jmc_number", this.resIds);
            await record.load();
            await record.model.notify();
    },

    show_folder() {
        const folder = this.getCurrentFolder();
        const folders = this.env.searchModel.getFolders();
        const folders_to_hide = [245, 1157, 1692];

        function checkParentRecursively(folder) {
            if (!folder) return false; // Stop if folder is undefined

            // Check if the current folder or its parent is in folders_to_hide
            if (folders_to_hide.includes(folder.id) || folders_to_hide.includes(folder.parentId)) {
                return true;
            }
            // Stop recursion if there's no parent
            if (folder.parentId === (undefined || false) ) {
                return false;
            }
            // Find the parent folder based on parentId
            const parentFolder = folders.find(f => f.id === folder.parentId);
            return checkParentRecursively(parentFolder); // Recursive call
        }
        return checkParentRecursively(folder);
    },
});
