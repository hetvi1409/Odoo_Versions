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
class AssetVerificationReport extends Component {
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
        this.location = useRef('location');
        this.start_date = useRef("start_date");
        this.end_date = useRef("end_date");
        this.asset = useRef("asset");

        this.period_start_date = useRef("period_start_date");
        this.period_end_date = useRef("period_end_date");

        this.verification_status = useRef("verification_status");

        this.state = useState({
            assets: [],
            // custodian_list: [],
            // department_list: [],
            // location_list: [],
            asset_list: [],
            data: null,
            job_location_list: [],

            });
        this.load_data();

        onWillStart(async () => {
        // Load all custodians (Many2one field)
        // this.state.custodian_list = await this.orm.searchRead(
        //     "hr.employee",
        //     [],
        //     ["name", "id"]
        // );
        // this.state.department_list = await this.orm.searchRead(
        // "hr.department",
        // [],
        // ["name", "id"]
        // );
        // this.state.location_list = await this.orm.searchRead(
        // "asset.verification.job.location",
        // [],
        // ["name", "id"]
        // );
        this.state.job_location_list = await this.orm.searchRead(
            "asset.verification.job",
            [],
            ["name", "id"]
        );

        this.state.asset_list = await this.orm.searchRead(
        "account.asset",
        [],
        ["name", "id"]
        );

        });
    }
    async load_data() {
        console.log("Loading data for Asset Verification Report...");
        const history_id = parseInt(this.asset.el?.value || 0);
        const period_start_date = this.period_start_date.el?.value || "";
        const period_end_date = this.period_end_date.el?.value || "";
        const job_location_id = parseInt(this.location.el?.value || 0);
        const verification_status = this.verification_status.el?.value || "";

        // Build the search domain based on filters
        try {
            const domain = [];
            if (history_id) {
                domain.push(["history_id", "=", history_id]);
            }
            if (job_location_id) {
                const jobLocation = await this.orm.read(
                    "asset.verification.job",
                    [job_location_id],
                    ["asset_ids"]
                );

                const assetLineIds = jobLocation[0]?.asset_ids || [];

                const assetLines = await this.orm.searchRead(
                    "asset.verification.job.line",
                    [["id", "in", assetLineIds]],
                    ["asset_id"]
                );

                const assetIds = assetLines.map(l => l.asset_id[0]);

                if (assetIds.length) {
                    domain.push(["history_id", "in", assetIds]);
                } else {
                    this.state.assets = [];
                    return;
                }
            }
            if(job_location_id && verification_status){
                const jobLocation = await this.orm.read(
                    "asset.verification.job",
                    [job_location_id],
                    ["asset_ids"]
                );

                const assetLineIds = jobLocation[0]?.asset_ids || [];

                const assetLines = await this.orm.searchRead(
                    "asset.verification.job.line",
                    [["id", "in", assetLineIds]],
                    ["asset_id","verified"]
                );

                let assetIds = assetLines.map(l => l.asset_id[0]);
                console.log("Filtered Asset IDs:", assetIds);

                if (verification_status === "verified") {
                    assetIds = assetLines
                        .filter(l => l.verified)
                        .map(l => l.asset_id[0]);
                    console.log("Verified Asset IDs:", assetIds);
                }

                if (verification_status === "not_verified") {
                    assetIds = assetLines
                        .filter(l => !l.verified)
                        .map(l => l.asset_id[0]);
                    console.log("Not Verified Asset IDs:", assetIds);
                }

                if (verification_status === "all") {
                    assetIds = assetLines.map(l => l.asset_id[0]);
                    console.log("All Asset IDs:", assetIds);
                }

                if (assetIds.length) {
                    domain.push(["history_id", "in", assetIds]);
                } else {
                    this.state.assets = [];
                    return;
                }
            }


            const records = await this.orm.searchRead(
                "asset.verification.history",
                domain,
                [
                    "id","history_id","parent_barcode","create_date","asset_verification_user_id",
                    "condition","is_verified","comments",
                    "past_year","this_year","location_id",
                ],
                {
                    order: "create_date desc"
                }
            );
            console.log("Fetched Records:", records);

            // GROUP BY ASSET TO GET LATEST ONLY
            const latestMap = new Map();

            for (const rec of records) {
                const assetId = rec.history_id?.[0];
                if (!assetId) continue;

                // First = latest due to DESC order
                if (!latestMap.has(assetId)) {
                    latestMap.set(assetId, rec);
                }
            }

            let latestAssets = Array.from(latestMap.values());

            // APPLY DATE FILTER AFTER grouping
            if (period_start_date || period_end_date) {
                const start = period_start_date ? new Date(period_start_date) : null;
                const end = period_end_date ? new Date(period_end_date) : null;

                latestAssets = latestAssets.filter(asset => {
                    const d = new Date(asset.create_date);

                    if (start && d < start) return false;
                    if (end && d > end) return false;

                    return true;
                });
            }

            // Resolve condition names
            const conditionIds = new Set();
            for (const asset of latestAssets) {
                for (const id of asset.condition || []) {
                    conditionIds.add(id);
                }
            }

            const conditions = conditionIds.size
                ? await this.orm.read(
                    "asset.condition",
                    [...conditionIds],
                    ["name"]
                )
                : [];

            const conditionMap = {};
            for (const cond of conditions) {
                conditionMap[cond.id] = cond.name;
            }

            for (const asset of latestAssets) {
                asset.condition = (asset.condition || [])
                    .map(id => conditionMap[id])
                    .join(", ");
            }

            console.log("Final Assets:", latestAssets);
            this.state.assets = latestAssets;

        } catch (error) {
            console.error("Error loading assets:", error);
        }
    }

   async print_xlsx() {
    console.log("Asset Verification Report---excel");

    const history_id = parseInt(this.asset.el?.value || 0);
    const period_start_date = this.period_start_date.el?.value || "";
    const period_end_date = this.period_end_date.el?.value || "";
    const job_location_id = parseInt(this.location.el?.value || 0);

       var data =  {
            //    'custodian_id': custodian_id,
            //    'custodian_department_id': department_id,
            //    'job_location_id': location_id,
            //    'date_from': startDate,
            //    'date_to': endDate,
               'history_id': history_id,
                'period_start_date': period_start_date,
                'period_end_date': period_end_date,
                'job_location_id': job_location_id,
           }
        const action = await this.orm.call(
        "assets.verification.reports",
        "action_get_xlsx_report_value",
        ["", data]);

        // Let Odoo handle file download
        await this.action.doAction(action);
   }
   async printPdf(ev) {
       console.log("Generating PDF report for Asset Verification....");
       ev.preventDefault();
       var self = this;
       var action_title = self.props.action.display_name;

    //    Remove unused variables
        // const custodian_id = parseInt(this.custodian.el?.value || 0);
        // const department_id = parseInt(this.department.el?.value || 0);
        // const location_id = parseInt(this.location.el?.value || 0);
        // const startDate = this.start_date.el?.value || "";
        // const endDate = this.end_date.el?.value || "";
        const history_id = parseInt(this.asset.el?.value || 0);
        console.log("HISTORY ID>>>>", history_id);
       return self.action.doAction({
           'type': 'ir.actions.report',
           'report_type': 'qweb-pdf',
           'report_name': 'asset_verification_report.asset_verification_report',
           'report_file': 'asset_verification_report.asset_verification_report',
           'data': {
            //    'custodian_id': custodian_id,
            //    'custodian_department_id': department_id,
            //    'job_location_id': location_id,
            //    'date_from': startDate,
            //    'date_to': endDate,
               'history_id': parseInt(this.asset.el?.value || 0),
           },
           'context': {
            'landscape': 1,
         },
         'display_name': 'Asset Report',
       });
   }
}
AssetVerificationReport.template = 'AssetVerificationReport';
actionRegistry.add("asset_verification", AssetVerificationReport);
