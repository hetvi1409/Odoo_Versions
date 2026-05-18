odoo.define('seta_dashboard.SETAAnalysisController', function (require) {
    "use strict";

    var AbstractController = require('web.AbstractController');
    return AbstractController.extend({
        init: function (parent, model, renderer, params) {
            params.viewType = "setaanalysis";
            this._super.apply(this, arguments);
        }
    });

});