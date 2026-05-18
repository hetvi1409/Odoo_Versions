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
    console.log("jhgfdede")
    const assets = await this.orm.searchRead(
            "account.asset",
            [["alternative_ref", "ilike", barcode]],
            [
                "id", "name", "asset_type_id",
                "description", "alternative_ref",
                "location_id", "current_condition_this_year",
                "custodian_id", "is_verified"
            ]
        );
    console.log('ASSET>>>>',assets);

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
        console.log('oju')
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
                    default_is_verified : asset.is_verified
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
    console.log("gf")
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



//odoo.define("asset_verification.AssetVerification", function (require) {
//    "use strict";
//    var AbstractAction = require('web.AbstractAction');
//    var core = require('web.core');
//    var BarcodeScanner = require("@web/webclient/barcode/barcode_scanner");
//    console.log(BarcodeScanner, 'BarcodeScanner')
//    var AssetVerification = AbstractAction.extend({
//        contentTemplate: 'AssetVerification',
//        events: {
//            'keypress': '_onKeypress',
//            'change': '_onChange',
//            'click .button_asset': 'openMobileScanner',
//            'click .button_job': 'openSelectedJob',
//            'change #verificationJobSelection': '_onJobSelectionChange',
//        },
//        start: async function () {
//            await this._super(...arguments);
//            window.addEventListener('keydown', this._onMouseMove.bind(this));
//            window.addEventListener('click', this._onMouseMove.bind(this));
//            window.addEventListener('mousemove', this._onMouseMove.bind(this));
//                this._addEventListeners();
//            if(document.getElementById('oe_barcode_id')){
//                document.getElementById('oe_barcode_id').focus();
//            }
//            this._fetchJobs();
//
//        },
//         _fetchJobs: function() {
//            var self = this;
//            console.log(this.getSession().uid,'dasde32434')
//            this._rpc({
//                model: "asset.verification.job",
//                method: "search_read",
//                fields: ["id", "name"],
//                domain: [['user_ids', 'in', [this.getSession().uid]]],
//            }).then(function(jobs) {
//                self.jobs = jobs;
//                self._renderJobOptions();
//             var openJobButton = document.getElementById('openJobButton');
//            if (document.getElementById('verificationJobSelection').value) {
//                openJobButton.style.display = 'inline-block';  // Show button if job is selected
//            } else {
//                openJobButton.style.display = 'none';  // Hide button if no job is selected
//            }
//
//            });
//        },
//        _onJobSelectionChange: function(event) {
//            this.selectedJobId = event.target.value;
//            // Show or hide the "Open Job" button based on job selection
//            var openJobButton = document.getElementById('openJobButton');
//            if (this.selectedJobId) {
//                openJobButton.style.display = 'inline-block';  // Show button if job is selected
//            } else {
//                openJobButton.style.display = 'none';  // Hide button if no job is selected
//            }
//        },
//        _renderJobOptions: function() {
//            var selectElement = document.getElementById('verificationJobSelection');
//            selectElement.innerHTML = '';
//            this.jobs.forEach(function(job) {
//                var option = document.createElement('option');
//                option.value = job.id;
//                option.textContent = job.name;
//                selectElement.appendChild(option);
//            });
//        },
//        /* focusing the input field */
//		_onMouseMove: function() {
//    var barcodeInput = document.getElementById('oe_barcode_id');
//    var selectionField = document.getElementById('verificationJobSelection');
//
//    // Check if there is a modal or dialog open
//    var isModalOpen = document.querySelector('.modal') !== null;
//    var isDropdownOpen = document.querySelector('.dropdown-menu.show') !== null;
//
//    // Check if the barcode input exists and no other input field is currently focused
//    // Also check if the selection field is not focused
//    if (barcodeInput && !isModalOpen && !isDropdownOpen && document.activeElement !== selectionField) {
//        barcodeInput.focus();
//    }
//},
//
//_addEventListeners: function() {
//    var selectionField = document.getElementById('verificationJobSelection');
//    var barcodeInput = document.getElementById('oe_barcode_id');
//
//    if (selectionField) {
//        selectionField.addEventListener('focusout', function() {
//            setTimeout(function() {
//                // Re-focus the barcode input after the selection field loses focus
//                barcodeInput.focus();
//            }, 0); // Use a timeout to ensure the focus shift is handled correctly
//        });
//    }
//},
//
//
//		/* Triggering flag for removing the duplicating the scan */
//        _onKeypress: function(data) {
//            this.typed_into = true;
//        },
//        /* scanning using gun */
//        _onChange: function(data) {
//    var self = this;
//
//    // Get the selected verification job
//    var selectedJobId = document.getElementById('verificationJobSelection').value;
//
//    // Check if a job is selected
//    if (!selectedJobId) {
//        self.displayNotification({
//            title: 'Please select a verification job before scanning a barcode.',
//            type: 'warning',
//        });
//        return;
//    }
//
//    var barcode = document.getElementById('oe_barcode_id').value;
//    console.log(this.typed_into, barcode);
//
//    if (this.typed_into) {
//        this.typed_into = false;
//
//        this._rpc({
//            model: "account.asset",
//            method: "search_read",
//            fields: [
//                "id", "name", "asset_type_id",
//                "description", "alternative_ref",
//                "location_id","current_condition_this_year",
//                "custodian_id",
//            ],
//            domain: [["alternative_ref", "ilike", barcode]],
//        }).then(function(asset) {
//            console.log('asset', asset);
//
//            if (asset.length == 0) {
//                // Asset not found, redirect to staging model form for data entry
//                console.log('Asset not found, redirecting to staging form');
//                self.do_action({
//                    type: 'ir.actions.act_window',
//                    res_model: 'asset.verification.staging',  // Redirecting to the staging model
//                    view_mode: 'form',
//                    view_type: 'form',
//                    views: [[false, 'form']],
//                    context: {
//                        default_barcode: barcode,  // Pass the scanned barcode to the new form
//                        default_verification_job_id: parseInt(selectedJobId),
//                        default_user_id: self.getSession().uid,
//
//                        // Add any additional default values here if needed
//                    },
//                    target: 'new',
//                });
//
//                self.displayNotification({
//                    title: 'Asset not found. You can enter the details to create a new asset.',
//                    type: 'danger',
//                });
//
//            } else {
//                console.log(asset[0].custodian_id[0],'dsaddada')
//                self.do_action({
//                    type: 'ir.actions.act_window',
//                    res_model: 'asset.verification',
//                    view_mode: 'form',
//                    view_type: 'form',
//                    views: [[false, 'form']],
//                    context: {
//                        default_asset_id: asset[0].id,
//                        default_name: asset[0].name,
//                        default_asset_type_id: asset[0].asset_type_id[0],
//                        default_barcode_number: barcode,
//                        default_description: asset[0].description,
//                        default_verification_job_id: parseInt(selectedJobId),
////                        default_allocation: asset[0].allocation,
//                        default_location: asset[0].location_id[0],
////                        default_condition: asset[0].condition,
//                        default_user_id: self.getSession().uid,
//                        default_custodian_id: asset[0].custodian_id[0]
//
//                    },
//                    target: 'new',
//                });
//            }
//        });
//
//        document.getElementById('oe_barcode_id').value = '';
//    }
//},
//        async openSelectedJob() {
//            console.log('fddfsfdsfdsrweds')
//        await this.do_action({
//                    type: 'ir.actions.act_window',
//                    res_model: 'asset.verification.job',  // Redirecting to the staging model
//                    view_mode: 'form',
//                    view_type: 'form',
//                    views: [[false, 'form']],
//                    res_id:parseInt(document.getElementById('verificationJobSelection').value),
//                    target: 'new',
//                });
//
//        },
//        /* scanning from the webcam */
//         async openMobileScanner() {
//            console.log('openMobileScanner');
//            const barcode = await BarcodeScanner.scanBarcode();
//            console.log('barcode', barcode);
//            if (barcode) {
//                // Reuse _onChange logic for barcode processing
//                var self = this;
//                // Get the selected verification job
//                var selectedJobId = document.getElementById('verificationJobSelection').value;
//
//                // Check if a job is selected
//                if (!selectedJobId) {
//                    self.displayNotification({
//                        title: 'Please select a verification job before scanning a barcode.',
//                        type: 'warning',
//                    });
//                    return;
//                }
//
//                this._rpc({
//                    model: "account.asset",
//                    method: "search_read",
//                    fields: [
//                        "id", "name", "asset_type_id",
//                        "description", "alternative_ref",
//                        "location_id", "current_condition_this_year",
//                    ],
//                    domain: [["alternative_ref", "ilike", barcode]],
//                }).then(function(asset) {
//                    if (asset.length == 0) {
//                        console.log('Asset not found');
//                        self.displayNotification({
//                            title: 'There is no asset with this barcode. Please try with another code',
//                            type: 'danger',
//                        });
//                        self.do_action({
//                            type: 'ir.actions.act_window',
//                            res_model: 'asset.verification.staging',
//                            view_mode: 'form',
//                            view_type: 'form',
//                            views: [[false, 'form']],
//                            context: {
//                                default_barcode: barcode,
//                                default_verification_job_id: parseInt(selectedJobId),
//                            },
//                            target: 'new',
//                        });
//                    } else {
//                        self.do_action({
//                            type: 'ir.actions.act_window',
//                            res_model: 'asset.verification',
//                            view_mode: 'form',
//                            view_type: 'form',
//                            views: [[false, 'form']],
//                            context: {
//                                default_asset_id: asset[0].id,
//                                default_name: asset[0].name,
//                                default_asset_type_id: asset[0].asset_type_id[0],
//                                default_barcode_number: barcode,
//                                default_description: asset[0].description,
//                                default_verification_job_id: parseInt(selectedJobId),
//                                default_location: asset[0].location_id[0],
//                            },
//                            target: 'new',
//                        });
//                    }
//                });
//            }
//            //else {
//            //    this.notificationService.add(this.env._t("Please, Scan again !"), { type: 'warning' });
//            //}
//        },
//
//   });
//   core.action_registry.add('account_alternative_ref', AssetVerification);
//   return AssetVerification;
//});
