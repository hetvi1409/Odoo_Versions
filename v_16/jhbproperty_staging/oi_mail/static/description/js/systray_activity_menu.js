/** @odoo-module **/

import ActivityMenu from '@mail/js/systray/systray_activity_menu';
import { useService } from "@web/core/utils/hooks";

ActivityMenu.include({

	start: function () {
		this._super.apply(this, arguments);
		this.menuService = useService("menu");
	},
		
	
	/**
	 * Redirect to particular model view
	 * @private
	 * @param {MouseEvent} event
	 */
	_onActivityFilterClick: function(event) {
		this._super.apply(this, arguments);

		var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
		var main_menu_id = 0;

		_.each(this._activities, function(activity_data) {
			if (activity_data.model == data.res_model)
				main_menu_id = activity_data.main_menu_id;
		});

		if (main_menu_id) {
			this.menuService.setCurrentMenu(main_menu_id);			
		}

	},


});