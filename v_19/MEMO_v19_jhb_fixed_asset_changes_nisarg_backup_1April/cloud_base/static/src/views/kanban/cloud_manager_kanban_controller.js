/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Domain } from "@web/core/domain";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { useBus, useService } from "@web/core/utils/hooks";
import { useRef } from "@odoo/owl";

console.log('kanban1234567890-=....')
export class CloudManagerKanbanController extends KanbanController {
    /*
    * Re-write to add input upload
    */
    static template = "cloud_base.CloudManagerKanbanView";
    setup() {
        console.log('inside...kanbna')
        super.setup(...arguments);
        this.orm = useService("orm");
        this.uploadFileInputRef = useRef("uploadFileInput");
        this.fileUploadService = useService("file_upload");
        this.notification = useService("notification");
        useBus(
            this.fileUploadService.bus,
            "FILE_UPLOAD_LOADED",
            async () => {
                await this.model.load();
            },
        );
    }
    /*
    * The method to process chosen files
    */
    async _onAddAttachment(ev) {
        console.log("hi, I'm here.....",this);
        if (!ev.target.files) {
            return this.notification.add(_t("There have been no files selected!"), { type: "danger" });
        };
        if (!this.model.cloudsFolderId) {
            return this.notification.add(_t("Please select a folder for uploaded files!"), { type: "danger" });
        };
        await this.fileUploadService.upload(
            "/cloud_base/upload_attachment",
            ev.target.files,
            {
                buildFormData: (formData) => { formData.append("clouds_folder_id", this.model.cloudsFolderId) },
                displayErrorNotification: true,
            },
        );
        ev.target.value = "";
    }
    /*
    * The method to select all records that satisfy search criteria
    * It requires orm.call since not all records are shown on the view
    */
    async _onSelectAll() {
        console.log('select')
        const kanbanModel = this.model;
        console.log(kanbanModel,'kanban model...')
        var fullDomain = this.env.searchModel._getDomain();
        console.log(fullDomain,'full domain...')
        if (fullDomain.length != 0) {
            console.log('full domain..')
            const selectedRecords = kanbanModel.selectedRecords.map((rec) => rec.id);
            console.log(selectedRecords,'selected rec....')
            fullDomain = Domain.or([fullDomain, [["id", "in", selectedRecords]]]).toList();
            console.log(fullDomain,'full domain...')
        }
        kanbanModel.selectedRecords = await this.orm.searchRead("ir.attachment", fullDomain, ["name"]);
        console.log(kanbanModel,'kanban model....')
        await kanbanModel.root.load();
        console.log(kanbanModel,'kanban model')
        kanbanModel.notify();
        console.log(kanbanModel,'kanban...')
    }

};


