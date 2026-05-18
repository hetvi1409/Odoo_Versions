/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';

registerPatch({
    name: 'ActivityGroup',
    modelMethods: {
        convertData(data) {
            const res = this._super.apply(this, arguments);
            res.main_menu_id = data.main_menu_id;
            return res;
        },
    },    
    fields: {
        main_menu_id: attr({
            default: 0,
        }),       
    },
});
