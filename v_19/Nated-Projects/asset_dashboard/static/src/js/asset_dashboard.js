odoo.define("asset_dashboard.dashboard", function (require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var ajax = require('web.ajax');
    var web_client = require('web.web_client');
    var _t = core._t;
    var framework = require('web.framework');
    var session = require('web.session');
    var AssetDashBoard = AbstractAction.extend({
        contentTemplate: 'Dashboard',
        events: {
        },
        init: function(parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['AssetTable'];
        },
        willStart: function() {
            var self = this;
            return $.when(this._super()).then(function() {
                return;
            });
        },
        start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.render_dashboards();
                self.render_graphs();
                self.$el.parent().addClass('oe_background_grey');
            });
        },
        render_dashboards: function() {
            var self = this;
                _.each(this.dashboards_templates, function(template) {
                    self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: self}));
                });
        },
        render_graphs: function(){
            var self = this;
            this.render_movable_asset();
            this.render_graph_movable_asset();
            this.render_overall_verification();
            this.render_asset_verification_number();
            this.render_asset_verification_carrying_value();
            this.render_condition_asset();
            this.render_asset_verified();
            this.render_asset_verified_condition();
            this.render_asset_verification_progress();
            this.render_asset_verification_location();
        },
        render_movable_asset: function(){
            rpc.query({
                    model: "account.asset",
                    method: "get_movable_asset_details",
                    args: {}
                }).then(function (result) {
                    for (let res = 0; res < result.length; res++) {
                        $('#movable_asset').append('<tr><td>'+result[res][0]+'</td><td class="location_table_value">'+result[res][1]+'</td><td class="location_table_value">'+result[res][2]+'</td></tr>')
                    }
            });
        },
        render_graph_movable_asset: function(){
            var self = this
            rpc.query({
                model: "account.asset",
                method: "get_movable_asset_graph_details",
            }).then(function (result) {
                var ctx = self.$("#canvas_movable");
                // Define the data
                var category = result.category // Add data values to array
                var sum = result.sum;
                var j = 0;
                $('#pro_info td').remove();
                Object.entries(result.sum).forEach(([key, value]) => {
                    $('#pro_info').append('<tr><td>'+category[j]+'</td><td>'+value+'</td></tr>')
                    j++;
                    });
                $('#pro_info').hide();
                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: category,//x axis
                        datasets: [{
                            label: 'Count', // Name the series
                            data: sum, // Specify the data values array
                            backgroundColor: [
                                "#003f5c",
                                "#2f4b7c",
                                "#f95d6a",
                                "#665191",
                                "#d45087",
                                "#ff7c43",
                                "#ffa600",
                                "#a05195",
                                "#6d5c16",
                                "#CCCCFF"
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
                                "#6d5c16",
                                "#CCCCFF"
                            ],
                            barPercentage: 0.5,
                            barThickness: 6,
                            maxBarThickness: 8,
                            minBarLength: 0,
                            borderWidth: 1, // Specify bar border width
                            type: 'bar', // Set this data to a line chart
                            fill: false
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                    }
                    });
                });
        },
        render_overall_verification: function(){
            rpc.query({
                    model: "account.asset",
                    method: "get_overall_movable_asset_details",
                    args: {}
                }).then(function (result) {
                    for (let res = 0; res < result.length; res++) {
                        $('#overall_verification').append('<tr><td>'+result[res][0]+'</td><td>'+result[res][1]+'</td><td>'+result[res][2]+'</td><td>'+result[res][3]+'</td><td>'+result[res][4]+'</td><td>'+result[res][5]+'</td><td>'+result[res][6]+'</td></tr>')
                    }
            });
        },
        render_asset_verification_number : function(){
            rpc.query({
                    model: "account.asset",
                    method: "get_asset_verification_number",
                }).then(function(result) {
                    var ctx = self.$("#asset_verification_number");
                    var key_ = ['Verified', 'Not Verified'];
                    var value = result.value;
                    $('#table_asset_verification_number td').remove();
                    var j = 0;
                    Object.entries(result.value).forEach(([key, value]) => {

                        $('#table_asset_verification_number').append('<tr><td>'+key_[j]+'</td><td>'+value+'</td></tr>')
                        j++;
                        });
                    $('#table_asset_verification_number').hide();
                    var myChart = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: key_,//x axis
                            datasets: [{
                                label: 'Count', // Name the series
                                data: value, // Specify the data values array
                                backgroundColor: [
                                    "#d45087",
                                    "#2f4b7c",
                                    "#a05195",
                                    "#ff7c43",
                                    "#ffa600",
                                    "#f95d6a",
                                    "#665191",
                                    "#6d5c16",
                                    "#CCCCFF",
                                    "#003f5c"
                                ],
                                borderColor: [
                                    "#d45087",
                                    "#a05195",
                                    "#ff7c43",
                                    "#ffa600",
                                    "#f95d6a",
                                    "#665191",
                                    "#6d5c16",
                                    "#CCCCFF",
                                    "#003f5c",
                                    "#2f4b7c"
                                ],
                                barPercentage: 0.5,
                                barThickness: 6,
                                maxBarThickness: 8,
                                minBarLength: 0,
                                borderWidth: 1, // Specify bar border width
                                type: 'pie', // Set this data to a line chart
                                fill: false
                            }]
                        },
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true
                                },
                            },
                            responsive: true, // Instruct chart js to respond nicely.
                            maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                        }
                    });
                });
        },
        render_asset_verification_carrying_value : function(){
            rpc.query({
                    model: "account.asset",
                    method: "get_asset_verification_carrying_value",
                }).then(function(result) {
                    var ctx = self.$("#asset_verification_carrying_value");
                    var key_ = ['Verified', 'Not Verified'];
                    var value = result.value;
                    $('#table_asset_verification_carrying_value td').remove();
                    var j = 0;
                    Object.entries(result.value).forEach(([key, value]) => {

                        $('#table_asset_verification_carrying_value').append('<tr><td>'+key_[j]+'</td><td>'+value+'</td></tr>')
                        j++;
                        });
                    $('#table_asset_verification_carrying_value').hide();
                    var myChart = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: key_,//x axis
                            datasets: [{
                                label: 'Count', // Name the series
                                data: value, // Specify the data values array
                                backgroundColor: [
                                    "#d45087",
                                    "#2f4b7c",
                                    "#a05195",
                                    "#ff7c43",
                                    "#ffa600",
                                    "#f95d6a",
                                    "#665191",
                                    "#6d5c16",
                                    "#CCCCFF",
                                    "#003f5c"
                                ],
                                borderColor: [
                                    "#d45087",
                                    "#a05195",
                                    "#ff7c43",
                                    "#ffa600",
                                    "#f95d6a",
                                    "#665191",
                                    "#6d5c16",
                                    "#CCCCFF",
                                    "#003f5c",
                                    "#2f4b7c"
                                ],
                                barPercentage: 0.5,
                                barThickness: 6,
                                maxBarThickness: 8,
                                minBarLength: 0,
                                borderWidth: 1, // Specify bar border width
                                type: 'pie', // Set this data to a line chart
                                fill: false
                            }]
                        },
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true
                                },
                            },
                            responsive: true, // Instruct chart js to respond nicely.
                            maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                        }
                    });
                });
        },
        render_condition_asset : function(){
            rpc.query({
                    model: "account.asset",
                    method: "get_graph_condition_asset",
                }).then(function(result) {
                    var ctx = self.$("#condition_asset");
                    var key_ = result.condition;
                    var value = result.count;
                    $('#table_condition_asset td').remove();
                    var j = 0;
                    Object.entries(result.count).forEach(([key, value]) => {

                        $('#table_condition_asset').append('<tr><td>'+key_[j]+'</td><td>'+value+'</td></tr>')
                        j++;
                        });
                    $('#table_asset_verification_carrying_value').hide();
                    var myChart = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: key_,//x axis
                            datasets: [{
                                label: 'Count', // Name the series
                                data: value, // Specify the data values array
                                backgroundColor: [
                                    "#d45087",
                                    "#2f4b7c",
                                    "#a05195",
                                    "#ff7c43",
                                    "#ffa600",
                                    "#f95d6a",
                                    "#665191",
                                    "#6d5c16",
                                    "#CCCCFF",
                                    "#003f5c"
                                ],
                                borderColor: [
                                    "#d45087",
                                    "#a05195",
                                    "#ff7c43",
                                    "#ffa600",
                                    "#f95d6a",
                                    "#665191",
                                    "#6d5c16",
                                    "#CCCCFF",
                                    "#003f5c",
                                    "#2f4b7c"
                                ],
                                barPercentage: 0.5,
                                barThickness: 6,
                                maxBarThickness: 8,
                                minBarLength: 0,
                                borderWidth: 1, // Specify bar border width
                                type: 'pie', // Set this data to a line chart
                                fill: false
                            }]
                        },
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true
                                },
                            },
                            responsive: true, // Instruct chart js to respond nicely.
                            maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                        }
                    });
                });
        },
        render_asset_verified : function(){
            rpc.query({
                model: "account.asset",
                method: "get_asset_not_verified",
            }).then(function (result) {
                var ctx = self.$("#graph_asset_verified");
                // Define the data
                var category = result.categ // Add data values to array
                var count = result.count;
                var j = 0;
                $('#table_asset_verified td').remove();
                Object.entries(result.count).forEach(([key, value]) => {
                    $('#table_asset_verified').append('<tr><td>'+category[j]+'</td><td>'+value+'</td></tr>')
                    j++;
                    });
                $('#table_asset_verified').hide();

                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: category,//x axis
                        datasets: [{
                            label: 'Count', // Name the series
                            data: count, // Specify the data values array
                            backgroundColor: [
                                "#003f5c",
                                "#2f4b7c",
                                "#f95d6a",
                                "#665191",
                                "#d45087",
                                "#ff7c43",
                                "#ffa600",
                                "#a05195",
                                "#6d5c16",
                                "#CCCCFF"
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
                                "#6d5c16",
                                "#CCCCFF"
                            ],
                            barPercentage: 0.5,
                            barThickness: 6,
                            maxBarThickness: 8,
                            minBarLength: 0,
                            borderWidth: 1, // Specify bar border width
                            type: 'bar', // Set this data to a line chart
                            fill: false
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                    }
                    });
                });
        },
        render_asset_verified_condition : function(){
            rpc.query({
                model: "account.asset",
                method: "get_asset_verified_condition",
            }).then(function (result) {
                var ctx = self.$("#graph_asset_verified_condition");
                // Define the data
                var condition = result.condition // Add data values to array
                var count = result.count;
                var j = 0;
                $('#table_asset_verified_condition td').remove();
                Object.entries(result.count).forEach(([key, value]) => {
                    $('#table_asset_verified_condition').append('<tr><td>'+condition[j]+'</td><td>'+value+'</td></tr>')
                        j++;
                    });
                $('#table_asset_verified_condition').hide();

                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: condition,//x axis
                        datasets: [{
                            label: 'Count' , // Name the series
                            data: count, // Specify the data values array
                            backgroundColor: [
                                "#003f5c",
                                "#2f4b7c",
                                "#f95d6a",
                                "#665191",
                                "#d45087",
                                "#ff7c43",
                                "#ffa600",
                                "#a05195",
                                "#6d5c16",
                                "#CCCCFF"
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
                                "#6d5c16",
                                "#CCCCFF"
                            ],
                            barPercentage: 0.5,
                            barThickness: 6,
                            maxBarThickness: 8,
                            minBarLength: 0,
                            borderWidth: 1, // Specify bar border width
                            type: 'bar', // Set this data to a line chart
                            fill: false
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                    }
                    });
                });
        },
        render_asset_verification_progress : function(){
            rpc.query({
                model: "account.asset",
                method: "get_asset_verification_progress",
            }).then(function (result) {
                var ctx = self.$("#graph_asset_verification_progress");
                // Define the data
                var condition = result.condition // Add data values to array
                var count = result.count;
                var count_verified = result.count_verified
                var j = 0;
                $('#table_asset_verification_progress td').remove();
                Object.entries(result.count).forEach(([key, value]) => {
                    $('#table_asset_verification_progress').append('<tr><td>'+condition[j]+'</td><td>'+value+'</td><td>'+count_verified[j]+'</td></tr>')
                        j++;
                    });
                $('#table_asset_verification_progress').hide();
                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: condition,//x axis
                        datasets: [
                        {
                            label: 'Not Verified' , // Name the series
                            data: count, // Specify the data values array
                            backgroundColor: [
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",

                            ],
                            borderColor: [
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",

                            ],
                            barPercentage: 0.5,
                            barThickness: 6,
                            maxBarThickness: 8,
                            minBarLength: 0,
                            borderWidth: 1, // Specify bar border width
                            type: 'bar', // Set this data to a line chart
                            fill: false
                        },
                        {
                            label: 'Verified' , // Name the series
                            data: count_verified, // Specify the data values array
                            backgroundColor: [
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                            ],
                            borderColor: [
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                            ],
                            barPercentage: 0.5,
                            barThickness: 6,
                            maxBarThickness: 8,
                            minBarLength: 0,
                            borderWidth: 1, // Specify bar border width
                            type: 'bar', // Set this data to a line chart
                            fill: false
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                    }
                    });
                });
        },
        render_asset_verification_location : function(){
            rpc.query({
                model: "account.asset",
                method: "get_asset_verification_location",
            }).then(function (result) {
                var ctx = self.$("#graph_asset_verification_location");
                // Define the data
                var location = result.location // Add data values to array
                var count = result.count;
                var count_verified = result.count_verified
                var j = 0;
                $('#table_asset_verification_location td').remove();
                Object.entries(result.count).forEach(([key, value]) => {
                    $('#table_asset_verification_location').append('<tr><td>'+location[j]+'</td><td>'+value+'</td><td>'+count_verified[j]+'</td></tr>')
                        j++;
                    });
                $('#table_asset_verification_location').hide();
                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: location,//x axis
                        datasets: [
                        {
                            label: 'Not Verified' , // Name the series
                            data: count, // Specify the data values array
                            backgroundColor: [
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",

                            ],
                            borderColor: [
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",
                                "#2f4b7c",

                            ],
                            barPercentage: 0.5,
                            barThickness: 6,
                            maxBarThickness: 8,
                            minBarLength: 0,
                            borderWidth: 1, // Specify bar border width
                            type: 'bar', // Set this data to a line chart
                            fill: false
                        },
                        {
                            label: 'Verified' , // Name the series
                            data: count_verified, // Specify the data values array
                            backgroundColor: [
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                            ],
                            borderColor: [
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                                "#f95d6a",
                            ],
                            barPercentage: 0.5,
                            barThickness: 6,
                            maxBarThickness: 8,
                            minBarLength: 0,
                            borderWidth: 1, // Specify bar border width
                            type: 'bar', // Set this data to a line chart
                            fill: false
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                    }
                    });
                });
        }
    });
    core.action_registry.add('asset_dashboard', AssetDashBoard);
    return;
});