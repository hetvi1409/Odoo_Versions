odoo.define("dashboard_dashboard.DashboardDashboard", function (require) {
   "use strict";
   var AbstractAction = require('web.AbstractAction');
   var core = require('web.core');
   var QWeb = core.qweb;
   var web_client = require('web.web_client');
   var session = require('web.session');
   var ajax = require('web.ajax');
   var _t = core._t;
   var rpc = require('web.rpc');
   var DashBoard = AbstractAction.extend({
       contentTemplate: 'AuditDashboard',
       init: function(parent, context) {
           this._super(parent, context);
           this.dashboard_templates = ['MainSection'];
       },
       start: function() {
           var self = this;
           this.set("title", 'Dashboard');
           return this._super().then(function() {
               self.render_dashboards();
           });
       },
       willStart: function(){
           var self = this;
           return this._super()
       },
       render_dashboards: function() {
           var self = this;
           this.fetch_data_()
           this.render_get_most_rended_cars();
           var templates = []
           var templates = ['MainSection'];
           _.each(templates, function(template) {
               self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: self}))
           });
       },
       fetch_data_: function() {
           var self = this

//          fetch data to the tiles
//           var def1 = this._rpc({
//               model: 'custom.audit.request',
//               method: "get_audit_details",
//               args: []
//           })
           this._rpc({
                model: 'custom.audit.request',
                method: "get_audit_details",
                args: [1]
                }).then(function (result) {
               $('#all_audit_count').append('<span>' + result.all_audit_count + '</span>');
               $('#my_audit_count').append('<span>' + result.my_audit_count + '</span>');
               $('#to_complete_count').append('<span>' + result.to_complete_count + '</span>');
               $('#to_approve_count').append('<span>' + result.to_approve_count + '</span>');
           });
       },
       render_get_most_rended_cars: function() {
        var self = this;

        this._rpc({
                model: 'custom.audit.request',
                method: "get_audit_category_details",
                args: [1]
            })
            .then(function(results) {
                var data = {
                    labels: results.name,
                    datasets: [{
                        data: results.audit,
                        fill: false,
                        backgroundColor: '#003f5c',
                        borderColor: '#003f5c',
                        barPercentage: 0.5,
                        barThickness: 6,
                        maxBarThickness: 8,
                        minBarLength: 0,
                        borderWidth: 1,
                        backgroundColor: [
                            "#665191",
                            "#ff7c43",
                            "#ffa600",
                            "#a05195",
                            "#2f4b7c",
                            "#f95d6a",
                            "#6d5c16",
                            "#003f5c",
                            "#d45087"
                        ],
                        borderColor: [
                            "#003f5c",
                            "#2f4b7c",
                            "#f95d6a",
                            "#665191",
                            "#d45087",
                            "#ff7c43",
                            "#ffa600",
                            "#a05195",
                            "#6d5c16"
                        ],
                        borderWidth: 1
                    }, ]
                };
                //options
                var options = {
                    responsive: true,
                    title: false,
                    legend: {
                        display: false,
                        position: "right",
                        labels: {
                            fontColor: "#333",
                            fontSize: 16
                        }
                    },
                    scales: {
                        yAxes: [{
                            gridLines: {
                                color: "rgba(1, 0, 0, 0)",
                                display: true,
                            },
                            ticks: {
                                min: 0,
                                display: true,
                                stepSize: 1,
                            }
                        }]
                    }
                };
                //create Chart class object

        var ctx = $("#most_rented_cars")
                var chart = new Chart(ctx, {
                    type: "bar",
                    data: data,
                    options: options
                });
                var pie = $('#audit_pie')
                var pie_chart = new Chart(pie, {
                    type: "pie",
                    data: data,
                })
                var line = $('#audit_line')
                var line_chart = new Chart(line, {
                    type: "line",
                    data: data,
                })
            var doughnut = $('#audit_doughnut')
                var doughnut_chart = new Chart(doughnut, {
                    type: "doughnut",
                    data: data,
                })
            })
        },
   });
   core.action_registry.add('audit_dashboard', DashBoard);
   return DashBoard;
});