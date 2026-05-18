/** @odoo-module **/

import SETAViewAnalysis from "@seta_dashboard/js/component/main/seta_view_analysis";
import SETAConfigAnalysis from "@seta_dashboard/js/component/main/seta_config_analysis";
import { useService } from "@web/core/utils/hooks";
import { Component, useRef, onRendered, onPatched, onMounted } from "@odoo/owl";
export class SETAAnalysisController extends Component {
    setup() {
        self = this;
        self.action = useService('action');
        self.container = useRef('SETAAnalysisContainer');
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
            var $viewAnalysis = new SETAViewAnalysis(self);
            var $configAnalysis = new SETAConfigAnalysis(self, $viewAnalysis);
            $configAnalysis.appendTo(self.$el);
            $viewAnalysis.appendTo(self.$el);
            self.$viewAnalysis = $viewAnalysis;
            self.$configAnalysis = $configAnalysis;
        });
    }
}

SETAAnalysisController.template = "SETAAnalysis";