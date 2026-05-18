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

class AssetMovementReport extends Component {
    async setup() {
        super.setup(...arguments);
        this.uiService = useService('ui');
        this.initial_render = true;
        this.orm = useService('orm');
        this.action = useService('action');
        this.start_date = useRef('date_from');
        this.end_date = useRef('date_to');
        this.end_date = useRef('date_to');
        this.selected_asset = useRef('selected_asset');
        this.state = useState({
            assets: [],
            asset_list: [],
            data: null,
            order_by : 'report_by_order',
            });
        this.load_data();

        onWillStart(async () => {
        // Load all custodians (Many2one field)
        this.state.asset_list = await this.orm.searchRead(
            "account.asset",
            [['job_location_id', '!=', false], ],
            ["name", "id"]
        );
        console.log('asset_list', this.state.asset_list)

        });
    }
    async load_data() {
        /**
        * Loads the data for the purchase report.
        */
        const selected_asset = parseInt(this.selected_asset.el?.value || 0);
        let move_lines = ''
        try {
            var domain = [];

            if (selected_asset) {
                domain = [["asset_id", "=", selected_asset]];
            }
            const assets = await this.orm.searchRead(
                "asset.location.history",
                domain,
                [
                "id", "asset_id", "old_location_id", "new_location_id",
                "changed_by", "date"
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
       const selected_asset = parseInt(this.selected_asset.el?.value || 0);
       var data =  {
           'asset_id': selected_asset,
       }
        const action = await this.orm.call(
        "asset.location.history",
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

        const selected_asset = parseInt(this.selected_asset.el?.value || 0);
       return self.action.doAction({
           'type': 'ir.actions.report',
           'report_type': 'qweb-pdf',
           'report_name': 'asset_verification_report.asset_movement_report',
           'report_file': 'asset_verification_report.asset_movement_report',
           'data': {
               'asset_id': selected_asset,
           },
           'context': {

            'landscape': 1,
         },
         'display_name': 'Asset Movement',
       });
   }
}
AssetMovementReport.template = 'AssetMovementReport';
actionRegistry.add("asset_movement", AssetMovementReport);
