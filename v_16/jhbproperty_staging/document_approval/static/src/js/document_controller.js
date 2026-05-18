/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DocumentsKanbanController } from "@documents/views/kanban/documents_kanban_controller";
import { DocumentsListController } from "@documents/views/list/documents_list_controller";
import { DocumentsApprovalControllerMixin } from "./document_inspector";

patch(DocumentsKanbanController.prototype, "documents_approval_documents_kanban_controller", DocumentsApprovalControllerMixin);
patch(DocumentsListController.prototype, "documents_approval_documents_list_controller", DocumentsApprovalControllerMixin);
