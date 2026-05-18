odoo.define('seta_dashboard.setaAnalysisRenderer', function (require) {
    "use strict";
    
    var AbstractRenderer = require('web.AbstractRenderer');
    var setaViewAnalysis = require('seta_dashboard.setaViewAnalysis');
    var setaConfigAnalysis = require('seta_dashboard.setaConfigAnalysis');
    return AbstractRenderer.extend({
        template: "setaAnalysis",
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
            var $viewAnalysis = new setaViewAnalysis(self)
            // Analysis Component
            var $configAnalysis = new setaConfigAnalysis(self, $viewAnalysis)

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
