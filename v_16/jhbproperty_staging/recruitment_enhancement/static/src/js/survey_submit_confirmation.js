odoo.define('recruitment_enhancement.survey_submit_confirmation', function (require) {
    'use strict';

    const core = require('web.core');
    const Dialog = require('web.Dialog');
    const publicWidget = require('web.public.widget');
    const $ = require('jquery');
    require('survey.form');

    const _t = core._t;

    if (!publicWidget.registry.SurveyFormWidget) {
        return;
    }

    publicWidget.registry.SurveyFormWidget.include({
        /**
         * Ask for confirmation before submitting the last survey page (finish).
         * This is used as a confirmation step for job applications.
         *
         * @override
         */
        _onSubmit: function (event) {
            event.preventDefault();

            const options = {};
            const $target = $(event.currentTarget);

            if ($target.val() === 'previous') {
                options.previousPageId = $target.data('previousPageId');
                this._submitForm(options);
                return;
            }

            if ($target.val() === 'finish' && !this.options.sessionInProgress) {
                Dialog.confirm(this, _t("Are you sure you want to submit the application?"), {
                    title: _t("Submit confirmation"),
                    confirm_callback: () => this._submitForm({ isFinish: true }),
                });
                return;
            }

            if ($target.val() === 'finish') {
                options.isFinish = true;
            }

            this._submitForm(options);
        },
    });
});
