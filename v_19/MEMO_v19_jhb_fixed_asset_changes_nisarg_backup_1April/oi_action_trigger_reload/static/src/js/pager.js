/** @odoo-module **/
import { Pager } from "@web/core/pager/pager";
import { patch } from '@web/core/utils/patch';
import { useBus } from "@web/core/utils/hooks";

patch(Pager.prototype, {
	
	setup() {
		super.setup();
        useBus(this.env.bus, "trigger_reload", () => this.navigate(0));
	}
	
});