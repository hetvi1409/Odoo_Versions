/** @odoo-module */

import { StatusBarField } from '@web/views/fields/statusbar/statusbar_field';
import { patch } from "@web/core/utils/patch";

patch(StatusBarField.prototype, {
	
	getVisibleSelection() {		
		if (this.props.daynamicVisibleSelection) {
			const workflow_states = this.env.model.root.data.workflow_states;
			if (workflow_states) {
				this.props.visibleSelection = JSON.parse(workflow_states);
			}			
		}		
		return this._super();
	}
});

const _extractProps = StatusBarField.extractProps;

patch(StatusBarField, {
	
	props: {
    	...StatusBarField.props,
    	daynamicVisibleSelection: { type: Boolean, optional: true }	
	},
	extractProps({ attrs, field }) { 
		const res = _extractProps.apply(this,arguments);
		res.daynamicVisibleSelection = field.name==="state" && (attrs.statusbar_visible === "WORKFLOW" || attrs.statusbar_visible === undefined);		
		return res;	
	}
});
