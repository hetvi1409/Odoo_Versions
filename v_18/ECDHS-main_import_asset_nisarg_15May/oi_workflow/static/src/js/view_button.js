/** @odoo-module */

import { ViewButton } from '@web/views/view_button/view_button';
import { patch } from "@web/core/utils/patch";

patch(ViewButton.prototype, {
	
	get clickParams() {
		const res = this._super();
		if (res.name == "action_approve" && res.confirm === undefined && _.str.contains(this.props.className,"oe_workflow_approve")) {
			const approve_confirm_msg =this.env.model.root.data.approve_confirm_msg;
			if (approve_confirm_msg)
				res.confirm = approve_confirm_msg;
		}
		if (res.name == "action_reject" && res.confirm === undefined && _.str.contains(this.props.className,"oe_workflow_reject")) {
			const reject_confirm_msg =this.env.model.root.data.reject_confirm_msg;
			if (reject_confirm_msg)
				res.confirm = reject_confirm_msg;
		}		
		return res;
			
	}
});