/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class SaleOrderSystray extends Component {
    static template = "view_customization.SaleOrderSystray";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ count: 0 });

        onWillStart(async () => {
            await this._fetchPendingOrders();
        });
    }

    async _fetchPendingOrders() {
        const today = new Date().toISOString().split("T")[0];

        const count = await this.orm.searchCount("sale.order", [
            ["state", "=", "draft"],
            ["date_order", ">=", today + " 00:00:00"],
        ]);
        console.log('Pending Orders Count:', count);

        this.state.count = count;
    }

    async onClick() {
        await this.action.doAction({
            name: "Pending Sale Orders",
            type: "ir.actions.act_window",
            res_model: "sale.order",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "=", "draft"]],
            target: "current",
        });
    }
}

// Register in systray
registry.category("systray").add(
    "sale_order_systray",
    { Component: SaleOrderSystray },
    { sequence: 1 }
);