/** @odoo-module */
import { Component, useRef, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const HISTORY_FIELDS = [
    "id", "history_id", "parent_barcode", "create_date",
    "asset_verification_user_id", "condition", "is_verified",
    "comments", "past_year", "this_year", "location_id",
];

const ASSET_FIELDS = [
    "id", "name", "alternative_ref", "latest_verification_history_id",
];

class AssetVerificationReport extends Component {

    setup() {
        this.orm    = useService("orm");
        this.action = useService("action");

        this.refs = {
            asset:               useRef("asset"),
            location:            useRef("location"),
            period_start_date:   useRef("period_start_date"),
            period_end_date:     useRef("period_end_date"),
            verification_status: useRef("verification_status"),
        };

        this.state = useState({
            assets:              [],
            job_location_list:   [],
            asset_list:          [],
            verification_status: "all",
            loading:             false,
            error:               null,
        });

        onWillStart(async () => {
            await this._loadDropdowns();
            await this.load_data();
        });
    }

    // Filter
    _getFilters() {
        const r = this.refs;
        return {
            history_id:          parseInt(r.asset.el?.value              || 0),
            job_location_id:     parseInt(r.location.el?.value           || 0),
            period_start_date:   r.period_start_date.el?.value           || "",
            period_end_date:     r.period_end_date.el?.value             || "",
            verification_status: r.verification_status.el?.value         || "all",
        };
    }

    async _loadDropdowns() {
        const [job_location_list, asset_list] = await Promise.all([
            this.orm.searchRead("asset.verification.job", [], ["name", "id"]),
            this.orm.searchRead("account.asset",          [], ["name", "id"]),
        ]);
        Object.assign(this.state, { job_location_list, asset_list });
    }

    async _fetchAssetsByJob(job_location_id) {
        const [job] = await this.orm.read(
            "asset.verification.job",
            [job_location_id],
            ["job_location_id"]
        );
        const locationId = job?.job_location_id?.[0];

        const assets = locationId
            ? await this.orm.searchRead(
                "account.asset",
                [["job_location_id", "=", locationId]],
                ASSET_FIELDS
              )
            : await this.orm.searchRead("account.asset", [], ASSET_FIELDS);

        const verifiedIds       = assets.filter(a =>  a.latest_verification_history_id?.[0]).map(a => a.id);
        const notVerifiedAssets = assets.filter(a => !a.latest_verification_history_id?.[0]);

        return { allAssets: assets, verifiedIds, notVerifiedAssets };
    }


    async _fetchVerifiedHistories(assetIds, period_start_date, period_end_date) {
        const domain = [];
        if (assetIds && assetIds.length) domain.push(["history_id", "in", assetIds]);
        if (period_start_date) domain.push(["create_date", ">=", period_start_date]);
        if (period_end_date)   domain.push(["create_date", "<=", period_end_date]);

        const records = await this.orm.searchRead(
            "asset.verification.history",
            domain,
            HISTORY_FIELDS,
            { order: "create_date desc, id desc" }
        );

        // latest verification history line
        const seen = new Set();
        const latest = [];
        for (const rec of records) {
            const aid = rec.history_id?.[0];
            if (aid && !seen.has(aid)) {
                seen.add(aid);
                latest.push(rec);
            }
        }
        return latest;
    }

    async _resolveConditions(records) {
        const ids = [...new Set(records.flatMap(r => r.condition || []))];
        if (!ids.length) return;
        const conditions = await this.orm.read("asset.condition", ids, ["name"]);
        const map = Object.fromEntries(conditions.map(c => [c.id, c.name]));
        for (const rec of records) {
            rec.condition = (rec.condition || []).map(id => map[id]).join(", ");
        }
    }

    // Not-verified
    _buildNotVerifiedRows(assets) {
        return assets.map(a => ({
            id:                         `not_verified_${a.id}`,
            history_id:                 [a.id, a.name || ""],
            alternative_ref:             a.alternative_ref || "",
            asset_verification_user_id: false,
            is_verified:                "Not Verified",
            create_date:                "",
            condition:                  "",
            past_year:                  "",
            this_year:                  "",
        }));
    }

    async _resolveData(filters) {
        const {
            history_id, job_location_id,
            period_start_date, period_end_date, verification_status,
        } = filters;

        let verifiedRows    = [];
        let notVerifiedRows = [];

        // Case 1: job + specific asset
        if (job_location_id && history_id) {
            const { verifiedIds, notVerifiedAssets } =
                await this._fetchAssetsByJob(job_location_id);

            if (verifiedIds.includes(history_id)) {
                verifiedRows = await this._fetchVerifiedHistories(
                    [history_id], period_start_date, period_end_date
                );
                await this._resolveConditions(verifiedRows);
            } else {
                const asset = notVerifiedAssets.find(a => a.id === history_id);
                notVerifiedRows = asset ? this._buildNotVerifiedRows([asset]) : [];
            }
            return { verifiedRows, notVerifiedRows };
        }

        // Case 2: job only
        if (job_location_id) {
            const { allAssets, verifiedIds, notVerifiedAssets } =
                await this._fetchAssetsByJob(job_location_id);

            if (verification_status === "not_verified") {
                notVerifiedRows = this._buildNotVerifiedRows(notVerifiedAssets);
                return { verifiedRows, notVerifiedRows };
            }

            if (verification_status === "verified" || verification_status === "all") {
                verifiedRows = await this._fetchVerifiedHistories(
                    verifiedIds, period_start_date, period_end_date
                );
                await this._resolveConditions(verifiedRows);
            }

            if (verification_status === "all") {
                // Not verified = all job assets whose ID is NOT in verifiedRows
                // mirrors Python: unverified = assets.filtered(lambda a: a.id not in verified_asset_ids)
                const verifiedAssetIds = new Set(verifiedRows.map(r => r.history_id?.[0]));
                const notVerifiedIds   = allAssets.map(a => a.id).filter(id => !verifiedAssetIds.has(id));

                if (notVerifiedIds.length) {
                    const notVerifiedRecords = await this.orm.searchRead(
                        "account.asset",
                        [["id", "in", notVerifiedIds]],
                        ASSET_FIELDS
                    );
                    notVerifiedRows = this._buildNotVerifiedRows(notVerifiedRecords);
                }
            }

            return { verifiedRows, notVerifiedRows };
        }

        // Case 3: single asset, no job
        if (history_id) {
            verifiedRows = await this._fetchVerifiedHistories(
                [history_id], period_start_date, period_end_date
            );
            await this._resolveConditions(verifiedRows);
            return { verifiedRows, notVerifiedRows };
        }

        // Case 4: fallback — all assets, latest history within period
        verifiedRows = await this._fetchVerifiedHistories(
            null, period_start_date, period_end_date
        );
        await this._resolveConditions(verifiedRows);
        return { verifiedRows, notVerifiedRows };
    }

    // ─── Main load ────────────────────────────────────────────────────────────
    async load_data() {
        this.state.loading = true;
        this.state.error   = null;
        try {
            const filters = this._getFilters();
            this.state.verification_status = filters.verification_status;
            const { verifiedRows, notVerifiedRows } = await this._resolveData(filters);
            this.state.assets = [...verifiedRows, ...notVerifiedRows];
        } catch (err) {
            console.error("AssetVerificationReport.load_data:", err);
            this.state.error = err.message || "Unexpected error loading data.";
        } finally {
            this.state.loading = false;
        }
    }

    // ─── Event handlers ───────────────────────────────────────────────────────
    async onFilterChange() {
        await this.load_data();
    }

    // Keep old name so existing templates don't break
    async onVerificationStatusChange() {
        await this.load_data();
    }

    // ─── Export ───────────────────────────────────────────────────────────────
    _buildReportData() {
        const { history_id, job_location_id, period_start_date,
                period_end_date, verification_status } = this._getFilters();
        return { history_id, period_start_date, period_end_date,
                 job_location_id, verification_status };
    }

    async print_xlsx() {
        const action = await this.orm.call(
            "assets.verification.reports",
            "action_get_xlsx_report_value",
            [this._buildReportData()],
            { context: { landscape: 1 } }
        );
        await this.action.doAction(action);
    }

    async printPdf(ev) {
        ev.preventDefault();
        await this.action.doAction({
            type:         "ir.actions.report",
            report_type:  "qweb-pdf",
            report_name:  "asset_verification_report.asset_verification_report",
            report_file:  "asset_verification_report.asset_verification_report",
            data:         this._buildReportData(),
            context:      { landscape: 1 },
            display_name: "Asset Report",
        });
    }
}

AssetVerificationReport.template = "AssetVerificationReport";
registry.category("actions").add("asset_verification", AssetVerificationReport);