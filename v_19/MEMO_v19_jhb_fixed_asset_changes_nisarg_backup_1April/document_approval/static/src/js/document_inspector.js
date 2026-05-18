/** @odoo-module **/
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";


export const DocumentsApprovalControllerMixin = () => ({
    setup() {
        super.setup(...arguments);
        this.action = useService("action");
        this.dialogService = useService("dialog");
        this.action = useService("action");
    },
    async onClickCreateRequest(ev) {
        this.action.doAction({
        name: _t("Approval Request"),
            type: 'ir.actions.act_window',
            res_model: 'documents.approval',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new',
            });
    },
    async onClickViewRequest(e) {
    var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Approval Requests"),
            type: 'ir.actions.act_window',
            res_model: 'documents.approval',
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [],
            target: 'current',
        }, options)
//        this.action.doAction({
//            name: _t("Approval Requests"),
//            type: 'ir.actions.act_window',
//            res_model: 'documents.approval',
//            view_mode: 'list,form',
//            views: [[false, 'form']],
//            target: 'current',
//        });
    },
});
