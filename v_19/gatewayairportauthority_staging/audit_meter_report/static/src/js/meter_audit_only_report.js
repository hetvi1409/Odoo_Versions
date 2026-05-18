/** @odoo-module */
const { Component } = owl;
import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";
import { useService } from "@web/core/utils/hooks";
import { useRef, useState } from "@odoo/owl";
import { BlockUI } from "@web/core/ui/block_ui";

const actionRegistry = registry.category("actions");
import { uiService } from "@web/core/ui/ui_service";

class AuditMeterOnlyDashboard extends Component {
    async setup() {
        super.setup(...arguments);
        this.uiService = useService('ui');
        this.initial_render = true;
        this.orm = useService('orm');
        this.action = useService('action');

        this.date_from = useRef('date_from');
        this.date_to = useRef('date_to');
        this.order_by = useRef('order_by');
        this.exception = useRef('exception');

        const today = new Date().toISOString().split('T')[0]; // Get today's date in YYYY-MM-DD format
        console.log(this.date_from, 'date_from')
        this.state = useState({
            order_line: [],
            data: null,
            exception: '',
            wizard_id: [],
            date_from: today, // Auto-fill with today's date
        });

        this.load_data();
    }

    async load_data(wizard_id = null) {
        let move_lines = '';
        try {
            if (wizard_id == null) {
                this.state.wizard_id = await this.orm.create("audit.meter.only.report", [{}]);
            }
            this.state.data = await this.orm.call("audit.meter.only.report", "get_audit_meter_only_details", [this.state.wizard_id]);
            $.each(this.state.data, function (index, value) {
                move_lines = value;
            });
            this.state.order_line = move_lines;
        } catch (el) {
            window.location.href;
        }
    }

    async applyFilter(ev) {
        let filter_data = {};
//        this.state.order_by = this.order_by.el.value;
        filter_data.date_from = this.date_from.el.value;
//        filter_data.date_to = this.date_to.el.value;
//        filter_data.report_type = this.order_by.el.value;
        this.state.date_from = this.date_from.el.value;
        let data = await this.orm.write("audit.meter.only.report", this.state.wizard_id, filter_data);
        this.load_data(this.state.wizard_id);
    }
    async printPdf(ev) {
        /**
        * Generates and displays a PDF report for the Audit meter.
        */
        ev.preventDefault();
        var self = this;
        var action_title = self.props.action.display_name;
        return self.action.doAction({
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': 'audit_meter_report.audit_meter_report_only_action',
            'report_file': 'audit_meter_report.audit_meter_report_only_action',
            'print_report_name': "Audit Meter Report",
            'data': {
            'report_data': this.state.data
            },
            'context': {
                'active_model': 'audit.meter.only.report',
            },
                'display_name': 'Audit Meter',
        });
    }
    ViewAuditDetails(ev){
        return this.action.doAction({
            type: "ir.actions.act_window",
            res_model: 'res.partner',
            res_id: parseInt(ev.target.id),
            views: [[false, "form"]],
            target: "current",
        });
    }
    async print_xlsx() {
        /**
        * Generates and downloads an XLSX report for the purchase orders.
        */
        var data = this.state.data
        var action = {
        'data': {
            'model': 'audit.meter.report',
            'options': JSON.stringify(data['orders']),
            'output_format': 'xlsx',
            'report_type': data['orders']['report_type'],
            'report_data': JSON.stringify(data['report_lines']),
            'report_name': 'Meter Audit Report',
            'dfr_data': JSON.stringify(data),
            },
        };
        this.uiService.block();
        await download({
            url: '/audit_meter_report',
            data: action.data,
            complete: this.uiService.unblock(),
            error: (error) => this.call('crash_manager', 'rpc_error', error),
        });
    }

    // Other methods remain unchanged...
}

AuditMeterOnlyDashboard.template = 'AuditMeterOnlyDashboard';
actionRegistry.add("audit_meter_only_dashboard", AuditMeterOnlyDashboard);
