/** @odoo-module **/

import SETAViewDashboard from "@seta_dashboard/js/component/main/seta_view_dashboard";
import SETAConfigDashboard from "@seta_dashboard/js/component/main/seta_config_dashboard";
import { useService } from "@web/core/utils/hooks";
import { Component, useRef, onRendered, onPatched, onMounted } from "@odoo/owl";
export class SETADashboardController extends Component {
    setup() {
        self = this;
        self.action = useService('action');
        self.container = useRef('SETADashboardContainer');
        self.context = false;
        if (self.props && self.props.context) {
            self.context = self.props.context;
        };
        // self.render();
        onPatched(() => {
            self = this;
        });
        onMounted(() => {
            self = this;
            self.$el = $(self.container.el);
            console.log('onMounted', self.props.value);
            var $viewDashboard = new SETAViewDashboard(self);
            var $configDashboard = new SETAConfigDashboard(self, $viewDashboard);
            $configDashboard.appendTo(self.$el);
            $viewDashboard.appendTo(self.$el);
            self.$viewDashboard = $viewDashboard;
            self.$configDashboard = $configDashboard;
        });
    }


}

SETADashboardController.template = "SETADashboard";