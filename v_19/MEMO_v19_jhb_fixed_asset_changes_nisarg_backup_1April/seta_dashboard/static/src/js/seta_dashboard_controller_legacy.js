odoo.define('seta_dashboard.SETADashboardController', function (require) {
    "use strict";

    var AbstractController = require('web.AbstractController');
    return AbstractController.extend({
        init: function (parent, model, renderer, params) {
            params.viewType = "setadashboard";
            this._super.apply(this, arguments);
        }
    });

});