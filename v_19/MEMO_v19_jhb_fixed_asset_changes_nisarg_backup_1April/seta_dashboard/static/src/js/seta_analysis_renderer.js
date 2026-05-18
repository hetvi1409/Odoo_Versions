odoo.define('seta_dashboard.SETAAnalysisRenderer', function (require) {
    "use strict";
    
    var AbstractRenderer = require('web.AbstractRenderer');
    var SETAViewAnalysis = require('seta_dashboard.SETAViewAnalysis');
    var SETAConfigAnalysis = require('seta_dashboard.SETAConfigAnalysis');
    return AbstractRenderer.extend({
        template: "SETAAnalysis",
        events: _.extend({}, AbstractRenderer.prototype.events, {
        }),
        init: function (parent, state, params) {
            var self = this;
            this._super.apply(this, arguments);
            // console.log("Init App Renderer", this, parent, state, params);
            self.parent = parent;
            if (parent.props) self.props = parent.props;
        },
        start: function () {
            var self = this;
            // console.log("Start App Renderer");

            // Dashboard Component
            var $viewAnalysis = new SETAViewAnalysis(self);
            self.$viewAnalysis = $viewAnalysis;
            // Analysis Component
            var $configAnalysis = new SETAConfigAnalysis(self, $viewAnalysis);
            self.$configAnalysis = $configAnalysis;

            // Append
            $configAnalysis.appendTo(self.$el);
            $viewAnalysis.appendTo(self.$el);
        },
        destroy: function() {
            // console.log("Destroy App Renderer");
            this._super.apply(this, arguments);
        },
    });

});
