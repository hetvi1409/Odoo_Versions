odoo.define('seta_dashboard.SETADashboardRenderer', function (require) {
    "use strict";
    
    var AbstractRenderer = require('web.AbstractRenderer');
    var SETAViewDashboard = require('seta_dashboard.SETAViewDashboard');
    var SETAConfigDashboard = require('seta_dashboard.SETAConfigDashboard');
    return AbstractRenderer.extend({
        template: "SETADashboard",
        events: _.extend({}, AbstractRenderer.prototype.events, {
        }),
        init: function (parent, state, params) {
            var self = this;
            this._super.apply(this, arguments);
            // console.log("Init App Renderer", this, parent, state, params);
            self.parent = parent;
            if (parent.props) self.props = parent.props;
            // Define Global Variables
        },
        start: function () {
            var self = this;
            // console.log("Start App Renderer");

            // Dashboard Component
            var $viewDashboard = new SETAViewDashboard(self);
            var $configDashboard = new SETAConfigDashboard(self, $viewDashboard);
            $configDashboard.appendTo(self.$el);
            $viewDashboard.appendTo(self.$el);
        },
        destroy: function() {
            // console.log("Destroy App Renderer");
            this._super.apply(this, arguments);
        },
    });

});
