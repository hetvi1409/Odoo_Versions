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
class AssetRegisterReport extends Component {
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
        this.report_type = useRef('report_type');
        this.state = useState({
            assets: [],
            custodian_list: [],
            data: null,
            disposed_asset: 0,
            good_asset: 0,
            total_asset: 0,
            damaged_asset: 0,
            cancelled_asset: 0,
            written_off_asset: 0,
            lost_asset: 0,
            order_by : 'report_by_order',
            original_value : 0,
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
        console.log("Loading data for Asset Register Report...");
        /**
        * Loads the data for the purchase report.
        */
        const custodian_id = parseInt(this.custodian.el?.value || 0);
        const department_id = parseInt(this.department.el?.value || 0);
        const type = this.report_type.el?.value
        console.log('type>>>',type);
        let move_lines = ''
        try {
            let domain = [["state", "=", "open"]];

            if (custodian_id) {
                domain.push(["custodian_id", "=", custodian_id]);
            }
    // Filter by department if selected
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
                "id", "name", "asset_type_id",
                "description", "alternative_ref", "original_value",
                "location_id", "current_condition_this_year",
                "custodian_id", "job_location_id", "custodian_department_id",
                "state"
                ]
            );
            var data = await this.orm.call('assets.register.reports', "get_asset_register", [])
            this.state.assets = assets
            this.state.good_asset = data['good_asset']
            this.state.disposed_asset = data['disposed_asset']
            this.state.damaged_asset = data['damaged_asset']
            this.state.total_asset = data['total_asset']
            this.state.cancelled_asset = data['cancelled_asset']
            this.state.lost_asset = data['lost_asset']
            this.state.written_off_asset = data['written_off_asset']
            this.state.original_value = data['original_value']
            this.state.total_value = data['total_value']
            this.state.total_value = this.state.assets.reduce((sum, asset) => sum + asset.original_value, 0);
            this.state.total_value = this.state.total_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
            this.state.data = data
            console.log("ASSET REGISTER DATA:", this.state.data);
        }
        catch (el) {
            window.location.href;
        }
    }
//   async applyFilter(ev) {
//       let filter_data = {}
//       this.state.order_by = this.order_by.el.value
//       filter_data.date_from = this.start_date.el.value
//       filter_data.date_to = this.end_date.el.value
//       filter_data.report_type = this.order_by.el.value
//       let data = await this.orm.write("dynamic.purchase.report",this.state.wizard_id, filter_data);
//       this.load_data(this.state.wizard_id)
//   }
   viewPurchaseOrder(ev) {
       return this.action.doAction({
           type: "ir.actions.act_window",
           res_model: 'purchase.order',
           res_id: parseInt(ev.target.id),
           views: [[false, "form"]],
           target: "current",
       });
   }
   async print_xlsx() {
        console.log("Generating XLSX report...");
       /**
       * Generates and downloads an XLSX report for the purchase orders.
       */

       const custodian_id = parseInt(this.custodian.el?.value || 0);
       const department_id = parseInt(this.department.el?.value || 0);
       const type = this.report_type.el?.value
       var data =  {
               'custodian_id': custodian_id,
               'department_id': department_id,
               'type': type,
           }
//       var result = await this.orm.call('assets.register.reports', "action_get_xlsx_report_value", ["", data])
        const action = await this.orm.call(
        "assets.register.reports",
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
       var type = this.report_type.el?.value
       return self.action.doAction({
           'type': 'ir.actions.report',
           'report_type': 'qweb-pdf',
           'report_name': 'asset_verification_report.asset_register_report',
           'report_file': 'asset_verification_report.asset_register_report',
           'data': {
               'custodian_id': custodian_id,
               'department_id': department_id,
               'type': type,
           },
           'context': {
            'landscape': 1,
            'purchase_order_report': true
         },
         'display_name': 'Purchase Order',
       });
   }
}
AssetRegisterReport.template = 'AssetRegisterReport';
actionRegistry.add("asset_register", AssetRegisterReport);
