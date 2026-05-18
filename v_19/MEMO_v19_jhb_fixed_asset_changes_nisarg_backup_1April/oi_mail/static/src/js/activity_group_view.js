/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

registerPatch({
    name: 'ActivityGroupView',
    recordMethods: {
        /**
         * @override
         */         
        onClickFilterButton(ev) {
			const main_menu_id = this.activityGroup.main_menu_id;
			if (main_menu_id) {
				this.env.services.menu.setCurrentMenu(main_menu_id);
			}			
			return this._super.apply(this, arguments);
		}
    },
});
