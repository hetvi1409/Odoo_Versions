/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
//import ajax from 'web.ajax';
import { rpc } from "@web/core/network/rpc";


publicWidget.registry.HelpdeskCategoryTickets = publicWidget.Widget.extend({
    selector: '#helpdesk_ticket_form',
    events: {
        'change #helpdesk_category': '_onChangeCategory',
    },

    _onChangeCategory: function (ev) {
        const categoryName = ev.target.value;

        rpc('/web/dataset/call_kw/helpdesk.sub.category/action_get_sub_category', {
            model: 'helpdesk.sub.category',
            method: 'action_get_sub_category',
            args: [[], categoryName],
            kwargs: {},
        }).then((result) => {
            const subCategorySelect = document.getElementById('helpdesk_sub_category');
            subCategorySelect.innerHTML = '<option value=""/>';

            if (result && result.length) {
                result.forEach(function (subcategory) {
                    const option = document.createElement('option');
                    option.value = subcategory.id;
                    option.textContent = subcategory.name;
                    subCategorySelect.appendChild(option);
                });
            }
        });
    },
});
