/** @odoo-module */
const { Component } = owl;
import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";
import { useService } from "@web/core/utils/hooks";
import { useRef, onWillStart, useState } from "@odoo/owl";
import { BlockUI } from "@web/core/ui/block_ui";
const actionRegistry = registry.category("actions");
import { uiService } from "@web/core/ui/ui_service";
// Extending components for adding purchase report class
class AssetDisposedReport extends Component {
    async setup() {
        super.setup(...arguments);
        this.uiService = useService('ui');
        this.initial_render = true;
        this.orm = useService('orm');
        this.action = useService('action');
        this.start_date = useRef('date_from');
        this.end_date = useRef('date_to');
        this.end_date = useRef('date_to');
        this.custodian = useRef('custodian');
        this.department = useRef('department');
        this.type = useRef('type');
        this.state = useState({
            assets: [],
            custodian_list: [],
            data: null,
            order_by : 'report_by_order',
            });
        this.load_data();

        onWillStart(async () => {
        // Load all custodians (Many2one field)
        this.state.custodian_list = await this.orm.searchRead(
            "hr.employee",
            [],
            ["name", "id"]
        );
        this.state.department_list = await this.orm.searchRead(
        "hr.department",
        [],
        ["name"]
    );

        this.state.asset_list = [];
        });
    }
    async load_data() {
        /**
        * Loads the data for the purchase report.
        */
        const custodian_id = parseInt(this.custodian.el?.value || 0);
        const department_id = parseInt(this.department.el?.value || 0);
        const type = this.type.el?.value;
        let move_lines = ''
        try {
            let domain = [["state", "=", "asset_disposed"]];

            if (custodian_id) {
                domain.push(["custodian_id", "=", custodian_id]);
            }
            if (department_id) {
                domain.push(["custodian_department_id", "=", department_id]);
            }
            if (type) {
                const threshold = parseFloat(await this.orm.call('ir.config_parameter', 'get_param', ['asset_registry.minor_major_threshold', '1000']));
                if (type == 'minor'){
                    domain.push(["original_value", "<=", threshold]);
                }
                if (type == 'major'){
                    domain.push(["original_value", ">", threshold]);
                }
            }
            const assets = await this.orm.searchRead(
                "account.asset",
                domain,
                [
                "id", "name", "asset_type_id", "disposal_date",
                "disposal_method", "disposal_price", "custodian_department_id",
                "description", "alternative_ref", "original_value",
                "location_id", "current_condition_this_year",
                "custodian_id", "job_location_id", "custodian_department_id",
                "state"
                ]
            );
            this.state.assets = assets
        }
        catch (el) {
            window.location.href;
        }
    }

   async print_xlsx() {
       /**
       * Generates and downloads an XLSX report for the purchase orders.
       */

       const custodian_id = parseInt(this.custodian.el?.value || 0);
       const department_id = parseInt(this.department.el?.value || 0);
       const type = this.type.el?.value
       var data =  {
               'custodian_id': custodian_id,
               'department_id': department_id,
               'type': type,
           }
//       var result = await this.orm.call('assets.register.reports', "action_get_xlsx_report_value", ["", data])
        const action = await this.orm.call(
        "assets.disposal.reports",
        "action_get_xlsx_report_value",
        ["", data]);

        // Let Odoo handle file download
        await this.action.doAction(action);
   }
   async printPdf(ev) {
       /**
       * Generates and displays a PDF report for the purchase orders.
       *
       * @param {Event} ev - The event object triggered by the action.
       * @returns {Promise} - A promise that resolves to the result of the action.
       */
       ev.preventDefault();
       var self = this;
       var action_title = self.props.action.display_name;

        const custodian_id = parseInt(this.custodian.el?.value || 0);
        const department_id = parseInt(this.department.el?.value || 0);
       return self.action.doAction({
           'type': 'ir.actions.report',
           'report_type': 'qweb-pdf',
           'report_name': 'asset_verification_report.asset_disposal_report',
           'report_file': 'asset_verification_report.asset_disposal_report',
           'data': {
               'custodian_id': custodian_id,
               'department_id': department_id,
               'type': false,

           },
           'context': {

            'landscape': 1,
         },
         'display_name': 'Purchase Order',
       });
   }
}
AssetDisposedReport.template = 'AssetDisposedReport';
actionRegistry.add("asset_disposal", AssetDisposedReport);
