/** @odoo-module **/
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { scanBarcode } from "@web/core/barcode/barcode_dialog";
import { BarcodeScanner } from "@barcodes/components/barcode_scanner";


class AssetVerification extends Component {
    static template = "asset_verification.AssetVerification";

    setup() {

        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.barcode = useService("barcode");
        this.state = useState({
            jobs: [],
            selectedJobId: null,
            barcode: "",
        });
        this.typedInto = false;

        onMounted(() => {
            this._fetchJobs();
            this._addEventListeners();
            this._focusBarcodeInput();
        });

        onWillUnmount(() => {
            window.removeEventListener('keydown', this._onMouseMove);
            window.removeEventListener('click', this._onMouseMove);
            window.removeEventListener('mousemove', this._onMouseMove);
        });
    }

    async _fetchJobs() {
    console.log(this.env.session,"ddd",session.storeData.Store.settings.user_id.id)
        const jobs = await this.orm.searchRead("asset.verification.job", [
                ["user_ids", "=",session.storeData.Store.settings.user_id.id],
            ]);
        this.state.jobs = jobs;
        this._updateOpenJobButton();
    }

    _updateOpenJobButton() {
        const openJobButton = document.getElementById('openJobButton');
        if (openJobButton) {
            openJobButton.style.display = this.state.selectedJobId ? 'inline-block' : 'none';
        }
    }

    _onJobSelectionChange(ev) {
        this.state.selectedJobId = ev.target.value;
        this._updateOpenJobButton();
    }

    _focusBarcodeInput() {
        const barcodeInput = document.getElementById('oe_barcode_id');
        if (barcodeInput) {
            barcodeInput.focus();
        }
    }

    _onMouseMove = () => {
        const barcodeInput = document.getElementById('oe_barcode_id');
        const selectionField = document.getElementById('verificationJobSelection');
        const isModalOpen = document.querySelector('.modal') !== null;
        const isDropdownOpen = document.querySelector('.dropdown-menu.show') !== null;

        if (barcodeInput && !isModalOpen && !isDropdownOpen && document.activeElement !== selectionField) {
            barcodeInput.focus();
        }
    };

    _addEventListeners() {
        window.addEventListener('keydown', this._onMouseMove);
        window.addEventListener('click', this._onMouseMove);
        window.addEventListener('mousemove', this._onMouseMove);

        const selectionField = document.getElementById('verificationJobSelection');
        const barcodeInput = document.getElementById('oe_barcode_id');
        if (selectionField) {
            selectionField.addEventListener('focusout', () => {
                setTimeout(() => barcodeInput.focus(), 0);
            });
        }
    }

    _onKeypress() {
        this.typedInto = true;
    }

    async _onChange() {
        if (!this.state.selectedJobId) {
            this.notification.add("Please select a verification job before scanning a barcode.", { type: "warning" });
            return;
        }

        const barcode = this.state.barcode;
        if (this.typedInto) {
            this.typedInto = false;
            await this._processBarcode(barcode);
            this.state.barcode = "";
        }
    }

    async _processBarcode(barcode) {
    const assets = await this.orm.searchRead(
            "account.asset",
            [["alternative_ref", "ilike", barcode]],
            [
                "id", "name", "asset_type_id",
                "description", "alternative_ref",
                "location_id", "current_condition_this_year",
                "custodian_id", "is_verified",
            ]
        );

        if (!assets.length) {
            this.notification.add("Asset not found. You can enter the details to create a new asset.", { type: "danger" });
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "asset.verification.staging",
                view_mode: "form",
                views: [[false, "form"]],
                context: {
                    default_barcode: barcode,
                    default_verification_job_id: parseInt(this.state.selectedJobId),
                    default_user_id: session.storeData.Store.settings.user_id.id,
                },
                target: "new",
            });
        } else {
            const asset = assets[0];
            console.log('asset>>',asset)
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "asset.verification",
                view_mode: "form",
                views: [[false, "form"]],
                context: {
                    default_asset_id: asset.id,
                    default_name: asset.name,
                    default_asset_type_id: asset.asset_type_id[0],
                    default_barcode_number: barcode,
                    default_description: asset.description,
                    default_verification_job_id: parseInt(this.state.selectedJobId),
                    default_location: asset.location_id,
                    default_user_id: session.storeData.Store.settings.user_id.id,
                    default_custodian_id: asset.custodian_id[0],
                    default_is_verified : asset.is_verified,
                },
                target: "new",
            });
        }
    }

    async openSelectedJob() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "asset.verification.job",
            view_mode: "form",
            views: [[false, "form"]],
            res_id: parseInt(this.state.selectedJobId),
            target: "new",
        });
    }

    async openMobileScanner() {
        if (!this.state.selectedJobId) {
            this.notification.add("Please select a verification job before scanning a barcode.", { type: "warning" });
            return;
        }

        try {
            const barcode = await scanBarcode(this.env);
            console.log(barcode,"ffd")
            if (barcode) {
                await this._processBarcode(barcode);
            }
        } catch (error) {
            this.notification.add("Failed to scan barcode. Please try again.", { type: "warning" });
        }
    }
}

registry.category("actions").add("account_alternative_ref", AssetVerification);

