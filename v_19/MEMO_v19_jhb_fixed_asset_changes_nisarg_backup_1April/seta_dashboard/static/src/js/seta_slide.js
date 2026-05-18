/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import SETAViewVisual from "@seta_dashboard/js/component/main/seta_view_visual";

$(document).ready(function () {

    var slide_visuals = []
    $(document).on('click', '.seta_reset_drilldown', function (event) {
        var analysis_element = $(this).parent().parent()
        var analysis_id = parseInt(analysis_element.attr("id"));
        if (slide_visuals.length > 0) {
            var selected_visual = false
            slide_visuals.forEach(vis => {
                if (vis.analysis_id == analysis_id) {
                    selected_visual = vis
                }
            })
            selected_visual.$el = analysis_element.find('.visual-chart')
            selected_visual._onClickResetDrilldown()
            selected_visual.$el.find('.seta_reset_drilldown').remove();
            selected_visual.$el.append(`
                <button class="btn btn-sm btn-primary seta_reset_drilldown">
                <i class="fa fa-chevron-up"></i>
                </button>
                `);
        }
    })
    $(document).on('click', '.seta_drillup', function (event) {
        var analysis_element = $(this).parent().parent()
        var analysis_id = parseInt(analysis_element.attr("id"));
        if (slide_visuals.length > 0) {
            var selected_visual = false
            slide_visuals.forEach(vis => {
                if (vis.analysis_id == analysis_id) {
                    selected_visual = vis
                }
            })
            selected_visual.$el = analysis_element.find('.visual-chart')
            selected_visual._onClickDrillup()
        }
    })
    function hideChatWidget() {
        setTimeout(() => {
            var chatWidget = $('iframe[title="chat widget"]');
            chatWidget.hide();
        }, 200);
    }

    function _getDataAnalysis(args) {
        var dashboardId = $('#dashboard_id').text();
        if (dashboardId) {
            dashboardId = parseInt(dashboardId);
            rpc('/web/dataset/call_kw/seta.dashboard/search_read', {
                model: 'seta.dashboard',
                method: 'search_read',
                args: [[['id', '=', dashboardId]], ['id', 'name', 'theme_id', 'animation']],
                kwargs: {},
            }).then(function (results) {
                if (results) {
                    var res = results[0];
                    if (res.theme_id && res.theme_id.length == 2) {
                        var amChartsColors = amChartsTheme.palette[res.theme_id[1]];
                        var colors = [];
                        amChartsColors.forEach(col => {
                            colors.push(am4core.color(col.hex));
                        })
                        function customTheme(target) {
                            if (target instanceof am4core.ColorSet) {
                                target.list = colors;
                            }
                        }
                        am4core.useTheme(customTheme);
                    }
                    if (res.animation) {
                        am4core.useTheme(am4themes_animated);
                    } else {
                        am4core.unuseTheme(am4themes_animated);
                    }
                    // Load Chart
                    var analysisCharts = $(".analysis_chart")
                    analysisCharts.each(function (index, analysis) {
                        let analysisId = $(analysis).attr("id")
                        if (analysisId > 0) {
                            var visual = new SETAViewVisual()
                            rpc('/web/dataset/call_kw/seta.analysis/try_get_analysis_data_dashboard', {
                                model: 'seta.analysis',
                                method: 'try_get_analysis_data_dashboard',
                                args: [parseInt(analysisId)],
                                kwargs: args || {},
                            }).then(function (result) {
                                visual.analysis_id = parseInt(analysisId)
                                visual.$el = $(analysis).find('.visual-chart')
                                visual.is_slide = true
                                visual._makeChartSlide(result);
                                slide_visuals.push(visual)
                                visual.slide_visuals = slide_visuals
                                visual._setAnalysisVariables(result);
                            })
                        }
                    });

                }
            })
        }
    }
    function checkChatLoaded() {
        if ($('iframe[title="chat widget"]').length) {
            hideChatWidget();
            clearInterval(chatInterval); // Stop checking once the element is found
        }
    }
    // var chatInterval = setInterval(checkChatLoaded, 100);

    function checkRevealLoaded() {
        if ($('.reveal').length) {
            clearInterval(revealInterval); // Stop checking once the element is found
            var args = {
                'filters': {
                    'dynamic': []
                },
                'mode': false
            }
            _getDataAnalysis(args)
        }
    }
    var revealInterval = setInterval(checkRevealLoaded, 100);
})