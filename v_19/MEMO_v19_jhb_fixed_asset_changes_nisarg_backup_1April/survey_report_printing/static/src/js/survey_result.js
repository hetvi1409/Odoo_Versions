odoo.define('survey_report_printing.SurveyResultWidget', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
publicWidget.registry.PrintSurveyResultWidget = publicWidget.Widget.extend({
    selector: '.o_survey_result',
    events: {
        'click .o_survey_results_print': '_onPrintResultsClick',
    },
        /**
         * Call print dialog
         * @private
         */
        _onPrintResultsClick: function () {
        console.log("click----->...")
            window.print();
        },
    });
});
