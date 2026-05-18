// javascript
odoo.define('law_firm_bits.Dashboard', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;

    var DashBoard = AbstractAction.extend({
        template: 'LegalDashboard',

        events: {
            'click #btn_new_lead': 'btn_new_lead',
            'click #btn_new_consultation': 'btn_new_consultation',
            'click #btn_new_case': 'btn_new_case',
            'click #btn_new_matter': 'btn_new_matter',
            'click #btn_new_contact': 'btn_new_contact',
            'click #btn_new_expense': 'btn_new_expense',
            'click #btn_view_leads': 'btn_view_leads',
            'click #btn_view_case_matter': 'btn_view_case_matter',
            'click #btn_view_payments': 'btn_view_payments',
            'click #btn_view_to_invoice_tasks': 'btn_view_to_invoice_tasks',
            'click #btn_click_reminder': 'btn_click_reminder',
            'change #update_dashboard': function(e) {
                e.stopPropagation();
                var $target = $(e.target);
                this.change_time_frame($target.val());
            },
        },

        init: function(parent, context) {
            this._super(parent, context);
            this.dashboard_data = [];
            this.case_type = '';
            this.sales_chart = '';
            this.client_chart = '';
            this.upcoming_reminders = [];
            this.today_reminders = [];
        },

        willStart: function(){
            var self = this;
            return this._super.apply(this, arguments).then(function() {

                var def0 = self._rpc({
                    model: 'project.project',
                    method: 'get_upcoming_reminders',
                    args: [],
                }).then(function (res) {
                    self.upcoming_reminders = res;
                });

                var def1 = self._rpc({
                    model: 'project.project',
                    method: 'get_today_reminders',
                    args: [],
                }).then(function (res) {
                    self.today_reminders = res;
                });

                self.change_time_frame('this_week');
                return $.when(def0, def1);
            });
        },

        start: function() {
            this.set("title", 'Dashboard');
            return this._super.apply(this, arguments);
        },

        renderElement: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                var $target = $('#update_dashboard');
                self.change_time_frame($target.val());
            });
        },

        change_time_frame: function(time_frame) {
            var self = this;
            return this._rpc({
                model: 'res.users',
                method: 'get_law_dashboard_data',
                args: [session.uid, time_frame],
            })
            .then(function (result) {
                self.update_dashboard_data(result[0]);
                self.dashboard_charts(result[1]);
            });
        },

        update_dashboard_data: function(data) {
            $('#card_new_leads').html(data.card_new_leads.value);
            $('#card_description_lead').html('<span class="text-' + data.card_new_leads.class + ' h4 font-weight-bolder">'+ data.card_new_leads.percentage +'% </span>than last ' + data.card_new_leads.time_frame);

            $('#card_case_matter').html(data.card_case_matter.value);
            $('#card_description_case_matter').html('<span class="text-' + data.card_case_matter.class + ' h4 font-weight-bolder">'+ data.card_case_matter.percentage +'% </span>than last ' + data.card_case_matter.time_frame);

            $('#card_payment').html(data.card_payment.value);
            $('#card_description_payment').html('<span class="text-' + data.card_payment.class + ' h4 font-weight-bolder">'+ data.card_payment.percentage +'% </span>than last ' + data.card_payment.time_frame);

            $('#card_invoice').html(data.card_invoice.value);
            $('#card_description_invoice').html('<span class="text-' + data.card_invoice.class + ' h4 font-weight-bolder">'+ data.card_invoice.percentage +'% </span>than last ' + data.card_invoice.time_frame);
        },

        dashboard_charts: function(data) {
            // Case Type Chart
            $('#chart_case_type').html('<canvas id="chart-case-type" class="chart-canvas" height="170"></canvas>');
            var ctx = document.getElementById("chart-case-type").getContext("2d");
            new Chart(ctx, data.chart_case_type);

            // Client court case Chart
            $('#chart_court_case_growth').html('<canvas id="court-case-growth" class="chart-canvas" height="170"></canvas>');
            var ctx3 = document.getElementById("court-case-growth").getContext("2d");
            new Chart(ctx3, data.chart_court_case_growth);
        },

        btn_new_lead: function(ev) {
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t('Pipeline'),
                res_model: 'crm.lead',
                domain: [['type', '=', 'opportunity']],
                views: [[false, 'form']],
                context: {'default_type': 'opportunity', 'search_default_assigned_to_me': 1}
            });
        },

        btn_new_consultation: function(ev) {
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t('Consultation'),
                res_model: 'calendar.event',
                domain: [['is_consultation', '=', true]],
                views: [[false, 'form']],
                context: {'default_is_consultation': true}
            });
        },

        btn_new_case: function(ev) {
            var self = this;
            this._rpc({
                model: 'res.users',
                method: 'get_case_form_view_id',
                args: [0, ev],
            })
            .then(function (result) {
                self.do_action({
                    type: 'ir.actions.act_window',
                    name: _t('Cases'),
                    res_model: 'project.project',
                    domain: [['is_case', '=', true]],
                    views: [[result, 'form']],
                    context: {'default_is_case': true}
                });
            });
        },

        btn_new_matter: function(ev) {
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t('Matters'),
                res_model: 'project.project',
                domain: [['is_matter', '=', true]],
                views: [[false, 'form']],
                context: {'default_is_matter': true}
            });
        },

        btn_new_contact: function(ev) {
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t('Contact'),
                res_model: 'res.partner',
                domain: [['is_law_client', '=', true]],
                views: [[false, 'form']],
                context: {'default_is_law_client': true}
            });
        },

        btn_new_expense: function(ev) {
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t('Expenses'),
                res_model: 'hr.expense',
                domain: [['is_law_expense', '=', true]],
                views: [[false, 'form']],
                context: {'default_is_law_expense': true}
            });
        },

        btn_click_reminder: function(ev) {
            var model = ev.currentTarget.dataset.model;
            var id = parseInt(ev.currentTarget.dataset.id, 10);
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t('Reminder'),
                res_model: model,
                domain: [['id', '=', id]],
                view_mode: 'list,form',
                views: [[false, 'list'], [false, 'form']],
            });
        },

        btn_view_leads: function(ev) {
            var self = this;
            this._rpc({
                model: 'crm.lead',
                method: 'btn_view_leads',
                args: [$('#update_dashboard').val()],
            }).then(function (res) {
                self.do_action({
                    type: 'ir.actions.act_window',
                    name: _t('Leads'),
                    view_mode: 'list,form',
                    res_model: 'crm.lead',
                    domain: [['id', 'in', res]],
                    views: [[false, 'list'], [false, 'form']],
                });
            });
        },

        btn_view_case_matter: function(ev) {
            var self = this;
            this._rpc({
                model: 'project.project',
                method: 'btn_view_case_matter',
                args: [$('#update_dashboard').val()],
            }).then(function (res) {
                self.do_action({
                    type: 'ir.actions.act_window',
                    name: _t('Case / Matter'),
                    view_mode: 'list,form',
                    res_model: 'project.project',
                    domain: [['id', 'in', res]],
                    views: [[false, 'list'], [false, 'form']],
                });
            });
        },

        btn_view_payments: function(ev) {
            var self = this;
            this._rpc({
                model: 'account.move',
                method: 'btn_view_payments',
                args: [$('#update_dashboard').val()],
            }).then(function (res) {
                self.do_action({
                    type: 'ir.actions.act_window',
                    name: _t('Payment Reminders'),
                    view_mode: 'list,form',
                    res_model: 'account.move',
                    domain: [['id', 'in', res]],
                    views: [[false, 'list'], [false, 'form']],
                });
            });
        },

        btn_view_to_invoice_tasks: function(ev) {
            var self = this;
            this._rpc({
                model: 'project.task',
                method: 'btn_view_to_invoice_tasks',
                args: [$('#update_dashboard').val()],
            }).then(function (res) {
                self.do_action({
                    type: 'ir.actions.act_window',
                    name: _t('Tasks To Invoice'),
                    view_mode: 'list,form',
                    res_model: 'project.task',
                    domain: [['id', 'in', res]],
                    views: [[false, 'list'], [false, 'form']],
                });
            });
        },

    });

    core.action_registry.add('legal_dashboard', DashBoard);
    return DashBoard;
});
