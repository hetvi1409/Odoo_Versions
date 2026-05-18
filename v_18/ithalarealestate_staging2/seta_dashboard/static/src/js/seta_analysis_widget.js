/** @odoo-module **/

import { registry } from "@web/core/registry";
import SETAViewVisual from "@seta_dashboard/js/component/main/seta_view_visual";
import { Component, useRef, onRendered, onPatched, onMounted } from "@odoo/owl";
class SETAAnalysisWidget extends Component {
    setup() {
        self = this;
        self.widgetContainer = useRef('widgetContainer');
        // self.render();
        onPatched(() => {
            self = this;
            console.log('onPatched', self.props.record.data);
            self.analysis_data = self.props.record.data[self.props.name];
            if (self.widgetContainer && self.widgetContainer.el && self.analysis_data) {
                var $el = $(self.widgetContainer.el);
                $el.empty();
                self.$visual = new SETAViewVisual(self, {
                    analysis_data: JSON.parse(self.analysis_data),
                });
                self.$visual.appendTo($el);
            }
        });
        onMounted(() => {
            self = this;
            console.log('onRendered', self.props.record.data);
            self.analysis_data = self.props.record.data[self.props.name];
            if (self.widgetContainer && self.widgetContainer.el && self.analysis_data) {
                var $el = $(self.widgetContainer.el);
                $el.empty();
                self.$visual = new SETAViewVisual(self, {
                    analysis_data: JSON.parse(self.analysis_data),
                });
                self.$visual.appendTo($el);
            }
        });
    }
}
SETAAnalysisWidget.template = 'seta_dashboard.SETAAnalysisWidget';

export const SETAAnalysisField = {
    component: SETAAnalysisWidget,
    supportedTypes: ["text"],
};
registry.category("fields").add("seta_analysis", SETAAnalysisField);