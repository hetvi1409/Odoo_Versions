/** @odoo-module **/

import { registry } from "@web/core/registry";
import { SETADashboardController } from "@seta_dashboard/js/seta_dashboard_controller";

export const SETADashboardView = {
    type: "setadashboard",
    display_name: "SETADashboard",
    icon: "fa-tachometer",
    multiRecord: true,
    Controller: SETADashboardController,
};

registry.category("views").add("setadashboard", SETADashboardView);