/** @odoo-module **/

import { registry } from "@web/core/registry";
import { SETAAnalysisController } from "@seta_dashboard/js/seta_analysis_controller";

export const SETAAnalysisView = {
    type: "setaanalysis",
    display_name: "SETAAnalysis",
    icon: "fa-tachometer",
    multiRecord: true,
    Controller: SETAAnalysisController,
};

registry.category("views").add("setaanalysis", SETAAnalysisView);