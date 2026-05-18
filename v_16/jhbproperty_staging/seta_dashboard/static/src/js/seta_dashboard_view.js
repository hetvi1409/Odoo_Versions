odoo.define('seta_dashboard.setaDashboardView', function (require) {
    "use strict";
    
    var core = require('web.core');
    var AbstractView = require('web.AbstractView');
    var view_registry = require('web.view_registry');
    var _lt = core._lt;
    var setaDashboardModel = require('seta_dashboard.setaDashboardModel');
    var setaDashboardController = require('seta_dashboard.setaDashboardController');
    var setaDashboardRenderer = require('seta_dashboard.setaDashboardRenderer');
    var setaDashboardView = AbstractView.extend({
        template: "setaDashboard",
        display_name: _lt('setaDashboard'),
        events: {
        },
        icon: 'fa-tachometer',
        config: _.extend({},AbstractView.prototype.config, {
            Model: setaDashboardModel,
            Controller: setaDashboardController,
            Renderer: setaDashboardRenderer,
        }),
        viewType: 'setadashboard',
        withControlPanel: false,
        withSearchPanel: false,
    
        init: function () {
            this._super.apply(this, arguments);
        },
    });
    
    view_registry.add('setadashboard', setaDashboardView);
    
    return setaDashboardView;
});