/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

class FleetDashboard extends Component {
    static template = "enhanced_fleet_management.FleetDashboard";

    setup() {
        this.state = useState({
            selection: [],
            activeTrips: 0,
            pendingRequests: 0,
            totalVehicles: 0,
            incidents: 0,
        });
    }

    getAllItems() {
        const selection = this.state?.selection || [];
        if (!Array.isArray(selection)) {
            return [];
        }
        return selection.filter(item => item != null);
    }

    getSortedItems() {
        const allItems = this.getAllItems();
        if (!Array.isArray(allItems)) {
            return [];
        }
        return allItems.sort((a, b) => {
            if (a.name && b.name) {
                return a.name.localeCompare(b.name);
            }
            return 0;
        });
    }
}

registry.category("actions").add("fleet_dashboard", FleetDashboard);
