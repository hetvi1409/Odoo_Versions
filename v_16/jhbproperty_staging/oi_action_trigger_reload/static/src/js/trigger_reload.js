/** @odoo-module **/

import { registry } from "@web/core/registry";
const actionRegistry = registry.category("actions");

const triggerReloadAction = (env, context) => {	
	env.bus.trigger("trigger_reload");
	return {
		type: 'ir.actions.act_window_close'
	}
};

actionRegistry.add("trigger_reload", triggerReloadAction);
