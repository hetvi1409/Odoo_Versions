odoo.define('seta_dashboard.setaSelectMetric', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');

    var setaSelectMetric = Widget.extend({
        template: 'setaSelectMetric',
        events: {
            'click .seta_select_metric_item': '_onSelectMetric',
        },

        /**
         * @override
         */
        init: function (parent) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.fields = [];
        },

        willStart: function () {
            var self = this;

            return this._super.apply(this, arguments).then(function () {
                return self.load();
            });
        },

        load: function () {
            var self = this;
        },

        start: function() {
            var self = this;
            this._super.apply(this, arguments);
            // Add Content
            if (self.parent.selectedAnalysis) {
                self._rpc({
                    model: 'seta.analysis',
                    method: 'ui_get_analysis_info',
                    args: [self.parent.selectedAnalysis],
                }).then(function (result) {
                    // Megha start
                    var collapseMetric = document.querySelector('#collapseMetric');
                    if (collapseMetric.style.display === "none" || collapseMetric.style.display === "") {
                        collapseMetric.style.display = "block";
                    } else {
                        collapseMetric.style.display = "none";
                    }
                    // Megha end
                    self.fields = result.fields_for_metrics;
                    self.fields.forEach(field => {
                        var $content = $(QWeb.render('setaSelectMetricItem', {
                            name: field.name,
                            id: field.id,
                            field_type: field.field_type,
                        }));
                        self.$el.append($content)
                    });
                })
            }
        },

        /**
         * Private Method
         */
         _onSelectMetric: function(ev) {
            var self = this;
            var field_id = $(ev.currentTarget).data('id');
            if (self.parent.selectedAnalysis) {
                self._rpc({
                    model: 'seta.analysis',
                    method: 'ui_add_metric_by_field',
                    args: [self.parent.selectedAnalysis, field_id],
                }).then(function (result) {
                    // console.log('Add Metric', result);
                    self.parent._loadAnalysisInfo();
                    self.parent._onClickAddMetric();
                    self.parent._renderVisual();
                })
            }
        },
    });

    return setaSelectMetric;
});