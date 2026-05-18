odoo.define('seta_dashboard.setaViewDashboardBlock', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var core = require('web.core');
    var _t = core._t;
    var setaViewVisual = require('seta_dashboard.setaViewVisual');
    var setaSelectFilterTemp = require('seta_dashboard.setaSelectFilterTemp');
    var setaViewDashboardBlock = Widget.extend({
        template: 'setaViewDashboardBlock',
        events: {
            'click input': '_onClickInput',
            'click .seta_action_open_analysis': '_openAnalysis',
            'click .seta_action_edit_analysis': '_editAnalysis',
            'click .seta_action_open_list_view': '_openListView',
            'click .seta_action_delete_block': '_onClickDeleteBlock',
            'click .seta_action_export_excel': '_onClickExportExcel',
            'click .seta_action_export_pdf': '_onClickExportPDF',
            'click .seta_dashboard_block_title': '_onClickBlockHeader',
        },

        /**
         * @override
         */
        init: function (parent, args) {
            this._super.apply(this, arguments);

            this.parent = parent;
            this.id = args.id;
            this.analysis_name = args.analysis_name;
            this.analysis_id = args.analysis_id;
            this.animation = args.animation;
            this.refresh_interval = args.refresh_interval;
            this.filters = args.filters;
            this.index = args.index;
            this.args = {}
            this.$visual;
            this.$title;
            this.$filter;
        },

        willStart: function () {
            var self = this;

            return this._super.apply(this, arguments).then(function () {
                return self.load();
            });
        },

        load: function () {
            var self = this;
        },

        start: function () {
            var self = this;
            this._super.apply(this, arguments);
            self.args = {
                'block_id': self.id,
                'analysis_id': self.analysis_id,
                'filters': self.filters,
                'refresh_interval': self.refresh_interval,
                'index': self.index,
            }
            
            if (self.animation) {
                am4core.useTheme(am4themes_animated);
            } else {
                am4core.unuseTheme(am4themes_animated);
            }

            self.$title = self.$el.find('.seta_dashboard_block_header .seta_dashboard_block_title');
            self.$visual = new setaViewVisual(self, self.args);
            self.$visual.appendTo(self.$el.find('.seta_dashboard_block_content'));
            
            // Add Component Filters
            self.$filter = new setaSelectFilterTemp(self, self.$visual);
            self.$filter.appendTo(self.$el.find('.seta_dashboard_block_header'));
            if (self.analysis_id) {
                self.$filter.analysis_id = self.analysis_id;
                self.$filter._loadFilters();
            }
        },

        clearInterval: function() {
            var self = this;
            if (self.$visual && self.$visual.interval) {
                clearInterval(self.$visual.interval);
            }
        },

        destroy: function() {
            var self = this;
            self.$el.remove();
        },

        /**
         * Private Method
         */
        _onClickInput: function (ev) {
            var self = this;
        },

        _onClickBlockHeader: function (ev) {
            var remove = ev.target.innerText
            if (remove != "Remove Analysis"){
                // Megha start
                // var seta_dropdown_analysis = document.querySelector('.seta_dropdown_analysis');
                var seta_dropdown_analysis = ev.target.nextElementSibling;
                if (seta_dropdown_analysis.style.display === "none" || seta_dropdown_analysis.style.display === "") {
                    seta_dropdown_analysis.style.display = "block";
                } else {
                    seta_dropdown_analysis.style.display = "none";
                }
            }
            // Megha end

        },

        _onClickExportExcel: function(ev) {
            var self = this;
            var id = $(ev.currentTarget).data('id');
            if (id) {
                // Megha start
                // var seta_dropdown_analysis = document.querySelector('.seta_dropdown_analysis');
                var seta_dropdown_analysis = ev.target.offsetParent
                seta_dropdown_analysis.style.display = "none"
                // Megha end
                var base_url = window.location.origin;
                var url = `${base_url}/seta/excel/${id.toString()}`;
                window.open(url, '_blank');
            }
        },
_onClickExportPDF: function(ev) {
    const { jsPDF } = window.jspdf;
    console.log('skjdfhkj', ev);
    console.log('skjdfhkj', ev.currentTarget.offsetParent.offsetParent.firstElementChild.innerHTML);
    console.log('parentNode', ev.target.parentNode);
    console.log('parentElement', ev.currentTarget);
    console.log('className', ev.currentTarget.className);
    console.log('className', ev.originalEvent.target.offsetParent.offsetParent.offsetParent);
    const content1 = $(ev.currentTarget).find('.seta_dashboard_block_content')[0];
    console.log('df', ev.originalEvent.target.offsetParent.offsetParent.offsetParent.lastElementChild.lastElementChild.lastElementChild);
    const content = ev.originalEvent.target.offsetParent.offsetParent.offsetParent.lastElementChild.lastElementChild.lastElementChild;

    domtoimage.toPng(content)
        .then(function(dataUrl) {
            const pdf = new jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: 'a4'
            });

            const img = new Image();
            img.src = dataUrl;

            img.onload = function() {
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = pdf.internal.pageSize.getHeight();
                const maxImgWidth = pdfWidth - 20; // Add padding
                const maxImgHeight = pdfHeight - 40; // Add padding and space for the heading

                // Maintain aspect ratio
                const aspectRatio = img.width / img.height;
                let imgWidth = maxImgWidth;
                let imgHeight = maxImgWidth / aspectRatio;

                if (imgHeight > maxImgHeight) {
                    imgHeight = maxImgHeight;
                    imgWidth = maxImgHeight * aspectRatio;
                }

                // Add heading text
                const heading = ev.currentTarget.offsetParent.offsetParent.firstElementChild.innerHTML;
                const headingX = 10; // X position for heading
                const headingY = 20; // Y position for heading
                pdf.setFontSize(16);
                pdf.text(heading, headingX, headingY);

                // Add image below the heading
                const imageY = headingY + 10; // Adjust Y position to add some space below the heading
                pdf.addImage(img, 'PNG', (pdfWidth - imgWidth) / 2, imageY, imgWidth, imgHeight);

                pdf.save('Analysis.pdf');
            };
        })
            .catch(function(error) {
                console.error('oops, something went wrong!', error);
            });
//            var seta_dropdown_analysis = ev.target.offsetParent;
//            seta_dropdown_analysis.style.display = "none";
        },
        _onClickDeleteBlock: function (ev) {
            var self = this;
            var id = $(ev.currentTarget).data('id');
            if (id) {
                new swal({
                    title: "Remove Analysis",
                    text: `
                        Do you confirm to remove the analysis ?
                    `,
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonText: 'Yes',
                    heightAuto : false,
                }).then((result) => {
                    if (result.isConfirmed) {
                        self._rpc({
                            model: 'seta.dashboard.block',
                            method: 'unlink',
                            args: [[id]],
                        }).then(function (res) {
                            self.parent._removeItem(id);
                            new swal('Success', `The analysis has been removed \n from this dashboard successfully`, 'success');
                        })
                    }
                });
            }
        },

        _openAnalysis: function (ev) {
            var self = this;
            if (self.analysis_id) {
                // Megha start
                // var seta_dropdown_analysis = document.querySelector('.seta_dropdown_analysis');
                var seta_dropdown_analysis = ev.target.offsetParent
                seta_dropdown_analysis.style.display = "none"
                // Megha end
                self.do_action({
                    type: 'ir.actions.act_window',
                    name: _t('Analysis'),
                    target: 'current',
                    res_id: self.analysis_id,
                    res_model: 'seta.analysis',
                    views: [[false, 'setaanalysis']],
                    context: {'analysis_id': self.analysis_id},
                });
            }
        },

        _editAnalysis: function (ev) {
            // Megha start
            // var seta_dropdown_analysis = document.querySelector('.seta_dropdown_analysis');
            var seta_dropdown_analysis = ev.target.offsetParent
            seta_dropdown_analysis.style.display = "none"
            // Megha end
            var self = this;
            if (self.analysis_id) {
                self.do_action({
                    type: 'ir.actions.act_window',
                    name: _t('Analysis'),
                    target: 'new',
                    res_id: self.analysis_id,
                    res_model: 'seta.analysis',
                    views: [[false, 'form']],
                    context: { 'active_test': false },
                }, {
                    on_close: function () {
                        self.$visual._renderVisual(self.args)
                    },
                });
            }
        },

        _openListView: function(ev) {
            var self = this;
            if (self.analysis_id) {
                // Megha start
                // var seta_dropdown_analysis = document.querySelector('.seta_dropdown_analysis');
                var seta_dropdown_analysis = ev.target.offsetParent
                seta_dropdown_analysis.style.display = "none"
                // Megha end
                self._rpc({
                    model: 'seta.analysis',
                    method: 'ui_get_view_parameters',
                    args: [[self.analysis_id], self.args],
                }).then(function (res) {
                    if (res) {
                        var data = res;
                        if (data.model) {
                            self.do_action({
                                type: 'ir.actions.act_window',
                                name: data.name,
                                res_model: data.model,
                                views: [[false, "list"], [false, "form"]],
                                view_type: 'list',
                                view_mode: 'list',
                                target: 'current',
                                context: {},
                                domain: data.domain,
                            });
                        } else {
                            new swal('Failed', 'Analysis must have model and domain first to open the list view!', 'error');
                        }
                    }
                })
            }
        }

    });

    return setaViewDashboardBlock;
});