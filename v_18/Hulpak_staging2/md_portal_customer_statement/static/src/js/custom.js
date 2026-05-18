/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.StatementApplyButton = publicWidget.Widget.extend({
    selector: '#o_portal_statement_apply_dates',
    events: {
        click: '_onClick'
    },

    init() {
        this._super(...arguments);
    },

    async _onClick(e){
        var $this = $(e.currentTarget);
        var $el = $this.closest('#portal_customer_statement');
        var date_from = $el.find('input[name=date_from]').val();
        var date_to = $el.find('input[name=date_to]').val();

        await rpc("/my/portal/customer/statement", {
                        date_begin: date_from,
                        date_end: date_to,
                         print_report: false,
                    }).then((data) => {
                        $('.o_portal_my_doc_table').replaceWith(data['updated_statement_report']);
                        });
    }
});

publicWidget.registry.StatementPrintButton = publicWidget.Widget.extend({
    selector: '#o_portal_statement_report_print',
    events: {
        click: '_onClick'
    },

    init() {
        this._super(...arguments);
    },

    async _onClick(e){
        var $this = $(e.currentTarget);
        var $el = $('#portal_customer_statement');
        var date_from = $el.find('input[name=date_from]').val();
        var date_to = $el.find('input[name=date_to]').val();

        await rpc("/my/portal/customer/statement", {
                        date_begin: date_from,
                        date_end: date_to,
                        print_report: true,
                    }).then((data) => {
                        window.location.href = `/web/content/${data['attachmentID']}?download=true&access_token=${data['access_token']}`
                        });
    }
});
