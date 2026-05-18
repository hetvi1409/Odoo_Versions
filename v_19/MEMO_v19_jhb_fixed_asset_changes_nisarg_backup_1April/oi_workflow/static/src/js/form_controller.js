/** @odoo-module */

import { FormController } from '@web/views/form/form_controller';
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

const { onMounted, onRendered } = owl;

patch(FormController.prototype, 'oi_workflow_form_controller', {
		
		_approvalFormEditEnabled(record_data, context) {
			
			if (session.uid === 1)
				return true;
			
			if (record_data.x_button_edit_enabled !== undefined)
				return record_data.x_button_edit_enabled;
				
			if (context.button_edit_enabled !== undefined)
				return context.button_edit_enabled;				
								
			if (session.disable_edit_on_non_approval && record_data.button_approve_enabled !== undefined)
				return record_data.button_approve_enabled;
				
			return true;			
		},
		
		_updateApprovalFormView() {
			const $el = $(this.__owl__.refs.root);
			if ($el.length == 0) return;
			const data = this.model.root.data;
			const approve_button_name = data.approve_button_name;
			const reject_button_name = data.reject_button_name;
			
			if (approve_button_name !== undefined) {
				if (approve_button_name) 
					$el.find('button.oe_workflow_approve span').text(approve_button_name);
				else
					$el.find('button.oe_workflow_approve').hide();									
			}
			
			if (reject_button_name !== undefined) {
				if (reject_button_name) 
					$el.find('button.oe_workflow_reject span').text(reject_button_name);
				else
					$el.find('button.oe_workflow_reject').hide();									
			}	
			
			if (this.model.root.mode === 'edit' && !this._approvalFormEditEnabled(data, this.model.root.context)) {
				this.model.root.switchMode("readonly");
			}
		},
		
		setup() {
			this._super();	
			onMounted(() => {
				$.when().then(this._updateApprovalFormView.bind(this));
				
			});
			
	        onRendered(() => {
	            $.when().then(this._updateApprovalFormView.bind(this));
	        });	        
	        			
		}
	}
);