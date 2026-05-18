/** @odoo-module **/
alert('File calling-->')

import { _t } from "@web/core/l10n/translation";
import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { loadJS, loadCSS } from "@web/core/assets";
import { loadBundle } from "@web/core/assets";
import { session } from "@web/session";
import { onMounted } from "@odoo/owl";




export class SaleDashboard extends Component {
    static template = "sale_dashboard.sale_dashboard_template";
    static props = { ...standardActionServiceProps };

    setup() {
        super.setup(...arguments);
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.rpc = useService("rpc");

        const currentYear = new Date().getFullYear();
        const startYear = currentYear - 5;
        const endYear = currentYear + 5;

        const yearRange = [];
        for (let year = startYear; year <= endYear; year++) {
            yearRange.push(year);
        }

        this.state = useState({
            year: currentYear,
            year_range: yearRange,
            data: {
                net_profit: "Loading...",
            },
        });
        console.log('this.state--->',this.state);

        onMounted(() => {
            this.loadDashboardData();
        });
    }
}
registry.category("actions").add("sale_dashboard.sale_dashboard", SaleDashboard);
