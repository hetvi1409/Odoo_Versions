odoo.define('seta_dashboard.setaViewAnalysis', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    
    var setaViewVisual = require('seta_dashboard.setaViewVisual');
    var setaSelectFilterTemp = require('seta_dashboard.setaSelectFilterTemp');
    var setaViewAnalysis = Widget.extend({
        template: 'setaViewAnalysis',

        /**
         * @override
         */
        init: function (parent) {
            var self = this;
            this._super.apply(this, arguments);
            
            self.parent = parent;
            self.$visual;
            self.$title;
            self.$filter;
            self.analysis_id;
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

            am4core.useTheme(am4themes_animated);

            self.$title = self.$el.find('.seta_dashboard_block_header .seta_dashboard_block_title');
            
            // Add Component Visual View
            self.$visual = new setaViewVisual(self);
            self.$visual.appendTo(self.$el.find('.seta_dashboard_block_content'));

            // Add Component Filters
            self.$filter = new setaSelectFilterTemp(self, self.$visual);
            self.$filter.appendTo(self.$el.find('.seta_dashboard_block_header'));
        },

        _setAnalysisId: function (analysis_id) {
            var self = this;
            self.analysis_id = analysis_id;
            if (self.$filter) {
                self.$filter.analysis_id = analysis_id;
                self.$filter._loadFilters();
            }
        },
    });

    return setaViewAnalysis;
});