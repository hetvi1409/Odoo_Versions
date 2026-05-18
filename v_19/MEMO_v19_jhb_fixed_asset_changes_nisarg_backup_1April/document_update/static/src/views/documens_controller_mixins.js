/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { DocumentsKanbanController } from "@documents/views/kanban/documents_kanban_controller";
import { DocumentsListController } from "@documents/views/list/documents_list_controller";
const { useComponent } = owl;


export const DocumentsUpdateMixin = {

    async onClickCreateDocumentJMC(ev) {
        this.env.services.action.doAction("document_update.jmc_documents_action", {
                additionalContext: {
//                    default_partner_id: props.context.default_partner_id || false,
                    default_folder_id: this.env.model.rootParams.domain[0][2],
//                    default_tag_ids: [x2ManyCommands.replaceWith(env.searchModel.getSelectedTagIds())],
//                    default_res_id: props.context.default_res_id || false,
//                    default_res_model: props.context.default_res_model || false,
                },
                fullscreen: this.env.isSmall,
                onClose: async () => {
                    await this.env.model.load();
                    this.env.model.useSampleModel = this.env.model.root.records.length === 0;
                    this.env.model.notify();
                },
            });
    },
};

patch(DocumentsKanbanController.prototype, "jpc_document_list_kanban_controller", DocumentsUpdateMixin);
patch(DocumentsListController.prototype, "jpc_document_list_list_controller", DocumentsUpdateMixin);
