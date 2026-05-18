/** @odoo-module */

import { ListController } from '@web/views/list/list_controller';
import { FormController } from '@web/views/form/form_controller';
import { patch } from 'web.utils';

const action_menu = {
    getActionMenuItems() {
        const res = this._super();
		const self = this;
		
		res.other.push({
            key: "trigger_reload",
            description: this.env._t("Refresh"),
            callback: () => {
               	self.env.bus.trigger("trigger_reload");				
            },
        });		
		return res;
	}
};

patch(FormController.prototype, 'oi_action_trigger_reload_form_controller', action_menu);
patch(ListController.prototype, 'oi_action_trigger_reload_list_controller', action_menu);
