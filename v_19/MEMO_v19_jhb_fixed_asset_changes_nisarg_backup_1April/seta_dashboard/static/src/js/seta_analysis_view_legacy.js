odoo.define('seta_dashboard.SETAAnalysisView', function (require) {
    "use strict";
    
    var core = require('web.core');
    var AbstractView = require('web.AbstractView');
    var view_registry = require('web.view_registry');
    var _lt = core._lt;
    var SETAAnalysisModel = require('seta_dashboard.SETAAnalysisModel');
    var SETAAnalysisController = require('seta_dashboard.SETAAnalysisController');
    var SETAAnalysisRenderer = require('seta_dashboard.SETAAnalysisRenderer');
    var SETAAnalysisView = AbstractView.extend({
        template: "SETAAnalysis",
        display_name: _lt('SETAAnalysis'),
        events: {
        },
        icon: 'fa-tachometer',
        config: _.extend({},AbstractView.prototype.config, {
            Model: SETAAnalysisModel,
            Controller: SETAAnalysisController,
            Renderer: SETAAnalysisRenderer,
        }),
        viewType: 'setaanalysis',
        withControlPanel: false,
        withSearchPanel: false,
    
        init: function () {
            this._super.apply(this, arguments);
        },
    });
    
    view_registry.add('setaanalysis', SETAAnalysisView);
    
    return SETAAnalysisView;
});