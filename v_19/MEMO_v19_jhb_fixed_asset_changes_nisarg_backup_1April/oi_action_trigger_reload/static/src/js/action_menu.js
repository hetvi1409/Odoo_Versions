/** @odoo-module */

import { ListController } from '@web/views/list/list_controller';
import { FormController } from '@web/views/form/form_controller';
import { patch } from "@web/core/utils/patch";

const action_menu = {
    getActionMenuItems() {
        const res = this._super();
		const self = this;
		
		res.other.push({
            key: "trigger_reload",
            description: "Refresh",
            callback: () => {
               	self.env.bus.trigger("trigger_reload");				
            },
        });		
		return res;
	}
};

patch(FormController.prototype, action_menu);
patch(ListController.prototype, action_menu);
