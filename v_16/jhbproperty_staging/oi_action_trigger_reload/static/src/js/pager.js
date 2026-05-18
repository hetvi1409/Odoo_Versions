/** @odoo-module **/
import { Pager } from "@web/core/pager/pager";
import { patch } from '@web/core/utils/patch';
import { useBus } from "@web/core/utils/hooks";

patch(Pager.prototype, 'oi_action_trigger_reload.pager', {
	
	setup() {
		this._super();
        useBus(this.env.bus, "trigger_reload", () => this.navigate(0));
	}
	
});