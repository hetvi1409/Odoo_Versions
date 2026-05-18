/** @odoo-module */

import { ListController } from '@web/views/list/list_controller';
import { FormController } from '@web/views/form/form_controller';
import { patch } from "@web/core/utils/patch";
import {ApprovalInfoDialog} from '@oi_workflow/js/approval_info';
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
const { onWillStart } = owl;

const action_menu = {
	
	setup() {
		this._super();

        onWillStart(async () => {
            this.is_approval_model = "button_approve_enabled" in this.props.fields;
            if (this.is_approval_model) {
				this.show_action_approve_all = await this.model.orm.call("approval.settings", "is_show_action_approve_all", [this.props.resModel]);
			}
        });        		
	},
		 		
    getActionMenuItems() {
        const res = this._super();
		const self = this;
						
		if (this.is_approval_model)
		{
			if (this.getSelectedRecordIds().length == 1)
				res.other.push({
					key: "approval_info",
					description: this.env._t("Approval Info"),
					callback: async () => {
							const activeIds = self.getSelectedRecordIds();
							const dialogProps = await self.model.orm.call(self.model.root.resModel, "get_approval_info", activeIds);
					    	await this.model.dialogService.add(ApprovalInfoDialog, dialogProps);
						}
				});
			
			if (this.show_action_approve_all) {
				res.other.push({
					key: "approve",
					description: this.env._t("Approve"),
					callback: async () => {						
							const dialogProps = {
								body: self.env._t("Are you sure you want to approve selected documents?"),
								confirm: async () => {
									const action = await self.model.orm.call(self.model.root.resModel, "action_approve_all", [], {context : self.getActiveContext()});
									if (action)
										self.getActionService().doAction(action);
								},
								cancel: () => {},
							}
							await this.model.dialogService.add(ConfirmationDialog, dialogProps);
						}
				});					
			}		
		}
		
		if ("state" in this.model.root.fields && this.env.services.user.isSystem) {
            res.other.push({
                key: "update_status",
                description: this.env._t("Update Status"),
                callback: () => {										 
					const action = {
					    name: this.env._t('Change Document Status'),
					    res_model: 'approval.state.update',
					    type: 'ir.actions.act_window',
					    views: [[false, 'form']],
					    view_type: 'form',
					    view_mode: 'form',
					    target : 'new',
					    context : self.getActiveContext()
					 };
					
					self.getActionService().doAction(action);
					
                },
            });			
		}	
		return res;
	}
};

patch(FormController.prototype, 'oi_workflow_form_controller_action_menu', action_menu);
patch(ListController.prototype, 'oi_workflow_list_controller_action_menu', action_menu);
