odoo.define('seta_dashboard.setaAnalysisView', function (require) {
    "use strict";
    
    var core = require('web.core');
    var AbstractView = require('web.AbstractView');
    var view_registry = require('web.view_registry');
    var _lt = core._lt;
    var setaAnalysisModel = require('seta_dashboard.setaAnalysisModel');
    var setaAnalysisController = require('seta_dashboard.setaAnalysisController');
    var setaAnalysisRenderer = require('seta_dashboard.setaAnalysisRenderer');
    var setaAnalysisView = AbstractView.extend({
        template: "setaAnalysis",
        display_name: _lt('setaAnalysis'),
        events: {
        },
        icon: 'fa-tachometer',
        config: _.extend({},AbstractView.prototype.config, {
            Model: setaAnalysisModel,
            Controller: setaAnalysisController,
            Renderer: setaAnalysisRenderer,
        }),
        viewType: 'setaanalysis',
        withControlPanel: false,
        withSearchPanel: false,
    
        init: function () {
            this._super.apply(this, arguments);
        },
    });
    
    view_registry.add('setaanalysis', setaAnalysisView);
    
    return setaAnalysisView;
});