odoo.define('seta_dashboard.SETADashboardView', function (require) {
    "use strict";
    
    var core = require('web.core');
    var AbstractView = require('web.AbstractView');
    var view_registry = require('web.view_registry');
    var _lt = core._lt;
    var SETADashboardModel = require('seta_dashboard.SETADashboardModel');
    var SETADashboardController = require('seta_dashboard.SETADashboardController');
    var SETADashboardRenderer = require('seta_dashboard.SETADashboardRenderer');
    var SETADashboardView = AbstractView.extend({
        template: "SETADashboard",
        display_name: _lt('SETADashboard'),
        events: {
        },
        icon: 'fa-tachometer',
        config: _.extend({},AbstractView.prototype.config, {
            Model: SETADashboardModel,
            Controller: SETADashboardController,
            Renderer: SETADashboardRenderer,
        }),
        viewType: 'setadashboard',
        withControlPanel: false,
        withSearchPanel: false,
    
        init: function () {
            this._super.apply(this, arguments);
        },
    });
    
    view_registry.add('setadashboard', SETADashboardView);
    
    return SETADashboardView;
});