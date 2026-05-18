odoo.define("asset_verification.AssetVerification", function (require) {
    "use strict";

    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');
    const BarcodeScanner = require("@web/webclient/barcode/barcode_scanner");

    const AssetVerification = AbstractAction.extend({
        contentTemplate: 'AssetVerification',
        events: {
            'keypress': '_onKeypress',
            'change': '_onChange',
            'click .button_asset': 'openMobileScanner',
            'click .button_job': 'openSelectedJob',
            'change #verificationJobSelection': '_onJobSelectionChange',
        },

        async start() {
            await this._super(...arguments);
            ['keydown', 'click', 'mousemove'].forEach(event =>
                window.addEventListener(event, this._onMouseMove.bind(this))
            );
            this._addEventListeners();
            document.getElementById('oe_barcode_id')?.focus();
            this._fetchJobs();
        },

        _fetchJobs() {
            this._rpc({
                model: "asset.verification.job",
                method: "search_read",
                fields: ["id", "name"],
                domain: [['user_ids', 'in', [this.getSession().uid]]],
            }).then(jobs => {
                this.jobs = jobs;
                this._renderJobOptions();
                this._toggleOpenJobButton();
            });
        },

        _toggleOpenJobButton() {
            const openJobButton = document.getElementById('openJobButton');
            const hasJobSelected = Boolean(document.getElementById('verificationJobSelection')?.value);
            if (openJobButton) openJobButton.style.display = hasJobSelected ? 'inline-block' : 'none';
        },

        _onJobSelectionChange(event) {
            this.selectedJobId = event.target.value;
            this._toggleOpenJobButton();
        },

        _renderJobOptions() {
            const selectElement = document.getElementById('verificationJobSelection');
            if (!selectElement) return;
            selectElement.innerHTML = '';
            this.jobs.forEach(job => {
                const option = new Option(job.name, job.id);
                selectElement.appendChild(option);
            });
        },

        _onMouseMove() {
            const barcodeInput = document.getElementById('oe_barcode_id');
            const selectionField = document.getElementById('verificationJobSelection');
            const isModalOpen = document.querySelector('.modal');
            const isDropdownOpen = document.querySelector('.dropdown-menu.show');

            if (barcodeInput && !isModalOpen && !isDropdownOpen && document.activeElement !== selectionField) {
                barcodeInput.focus();
            }
        },

        _addEventListeners() {
            const selectionField = document.getElementById('verificationJobSelection');
            const barcodeInput = document.getElementById('oe_barcode_id');

            selectionField?.addEventListener('focusout', () => {
                setTimeout(() => barcodeInput?.focus(), 0);
            });
        },

        _onKeypress() {
            this.typed_into = true;
        },

        _onChange() {
            if (!this.typed_into) return;

            const barcodeInput = document.getElementById('oe_barcode_id');
            const selectedJobId = document.getElementById('verificationJobSelection')?.value;

            if (!selectedJobId) {
                this.displayNotification({
                    title: 'Please select a verification job before scanning a barcode.',
                    type: 'warning',
                });
                return;
            }

            const barcode = barcodeInput.value.trim();
            this.typed_into = false;

            this._rpc({
                model: "account.asset",
                method: "search_read",
                fields: [
                    "id", "name", "asset_type_id", "description", "alternative_ref",
                    "location_id", "current_condition_this_year", "custodian_id",
                ],
                domain: [["alternative_ref", "ilike", barcode]],
            }).then(asset => {
                const context = {
                    default_barcode: barcode,
                    default_verification_job_id: parseInt(selectedJobId),
                    default_user_id: this.getSession().uid,
                };

                // No match found at all
                if (!asset.length) {
                    this._openStagingForm(context);
                    return;
                }

                // Extract digits from scanned barcode
                const barcodeDigits = barcode.match(/\d+/g)?.join('') || '';

                // Try to find exact match by digits
                const exact_asset = asset.find(i => {
                    const refDigits = i.alternative_ref?.match(/\d+/g)?.join('') || '';
                    return refDigits === barcodeDigits && i.alternative_ref?.endsWith(barcodeDigits);
                });

                if (exact_asset) {
                    Object.assign(context, {
                        default_asset_id: exact_asset.id,
                        default_name: exact_asset.name,
                        default_asset_type_id: exact_asset.asset_type_id[0],
                        default_description: exact_asset.description,
                        default_barcode_number: barcode,
                        default_location: exact_asset.location_id?.[0],
                        default_custodian_id: exact_asset.custodian_id?.[0],
                    });

                    this._openVerificationForm(context);
                } else {
                    // No exact match — open staging
                    this._openStagingForm(context);
                }

                barcodeInput.value = '';
            });
        },

        // Helper method to open asset.verification form
        _openVerificationForm(context) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'asset.verification',
                view_mode: 'form',
                views: [[false, 'form']],
                context,
                target: 'new',
            });
        },

        // Helper method to open asset.verification.staging form
        _openStagingForm(context) {
            this.displayNotification({
                title: 'Asset not found. You can enter the details to create a new asset.',
                type: 'danger',
            });
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'asset.verification.staging',
                view_mode: 'form',
                views: [[false, 'form']],
                context,
                target: 'new',
            });
        },


//        _onChange() {
//            if (!this.typed_into) return;
//
//            const barcodeInput = document.getElementById('oe_barcode_id');
//            const selectedJobId = document.getElementById('verificationJobSelection')?.value;
//
//            if (!selectedJobId) {
//                this.displayNotification({
//                    title: 'Please select a verification job before scanning a barcode.',
//                    type: 'warning',
//                });
//                return;
//            }
//
//            const barcode = barcodeInput.value;
//            this.typed_into = false;
//
//            this._rpc({
//                model: "account.asset",
//                method: "search_read",
//                fields: [
//                    "id", "name", "asset_type_id", "description", "alternative_ref",
//                    "location_id", "current_condition_this_year", "custodian_id",
//                ],
//                domain: [["alternative_ref", "ilike", barcode]],
//            }).then(asset => {
//                const context = {
//                    default_barcode: barcode,
//                    default_verification_job_id: parseInt(selectedJobId),
//                    default_user_id: this.getSession().uid,
//                };
//
//                if (!asset.length) {
//                    this.do_action({
//                        type: 'ir.actions.act_window',
//                        res_model: 'asset.verification.staging',
//                        view_mode: 'form',
//                        views: [[false, 'form']],
//                        context,
//                        target: 'new',
//                    });
//                    this.displayNotification({
//                        title: 'Asset not found. You can enter the details to create a new asset.',
//                        type: 'danger',
//                    });
//                } else {
//                    console.log("jjjjj",asset)
//                    console.log("jjjjj",asset.length)
//                    if (asset.length) {
//                    console.log("ifff")
//                    const letters = barcode.match(/[a-zA-Z]+/g)?.join('') || '';
//                    const numbers = barcode.match(/\d+/g)?.join('') || '';
//
//                    console.log("Letters:", letters); // e.g., "JPC"
//                    console.log("Numbers:", numbers);
//                    const exact_asset = asset.find(i => {
//                        const refDigits = i.alternative_ref?.match(/\d+/g)?.join('') || '';
//                        return refDigits === barcode;
//                    });
//                    console.log(exact_asset,"rrrr")
//                    if (exact_asset) {
//
//                     Object.assign(context, {
//
//                        default_asset_id: exact_asset.id,
//                        default_name: exact_asset.name,
//                        default_asset_type_id: exact_asset.asset_type_id[0],
//                        default_description: exact_asset.description,
//                        default_barcode_number: barcode,
//                        default_location: exact_asset.location_id?.[0],
//                        default_custodian_id: exact_asset.custodian_id?.[0]
//                    });
//
//
//                    }
//                    else{
//                    this.do_action({
//                        type: 'ir.actions.act_window',
//                        res_model: 'asset.verification.staging',
//                        view_mode: 'form',
//                        views: [[false, 'form']],
//                        context,
//                        target: 'new',
//                    });
//                    this.displayNotification({
//                        title: 'Asset not found. You can enter the details to create a new asset.',
//                        type: 'danger',
//                    });
//
//                    }
//                    }
//                    else {
//
//                    Object.assign(context, {
//
//                        default_asset_id: asset[0].id,
//                        default_name: asset[0].name,
//                        default_asset_type_id: asset[0].asset_type_id[0],
//                        default_description: asset[0].description,
//                        default_barcode_number: barcode,
//                        default_location: asset[0].location_id[0],
//                        default_custodian_id: asset[0].custodian_id?.[0]
//                    });
//                    }
//
//                   this.do_action({
//                        type: 'ir.actions.act_window',
//                        res_model: 'asset.verification',
//                        view_mode: 'form',
//                        views: [[false, 'form']],
//                        context,
//                        target: 'new',
//                    });
//                }
//                barcodeInput.value = '';
//            });
//        },

        async openSelectedJob() {
            const jobId = parseInt(document.getElementById('verificationJobSelection')?.value);
            if (!jobId) return;
            await this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'asset.verification.job',
                view_mode: 'form',
                views: [[false, 'form']],
                res_id: jobId,
                target: 'new',
            });
        },

       async openMobileScanner() {
        console.log("ffff");
        const barcode = await BarcodeScanner.scanBarcode();
        if (!barcode) return;

        const selectedJobId = document.getElementById('verificationJobSelection')?.value;
        if (!selectedJobId) {
            this.displayNotification({
                title: 'Please select a verification job before scanning a barcode.',
                type: 'warning',
            });
            return;
        }

        const context = {
            default_barcode: barcode,
            default_verification_job_id: parseInt(selectedJobId),
        };

        this._rpc({
            model: "account.asset",
            method: "search_read",
            fields: [
                "id", "name", "asset_type_id", "description", "alternative_ref",
                "location_id", "current_condition_this_year",
            ],
            domain: [["alternative_ref", "ilike", barcode]],
        }).then(asset => {
            if (!asset.length) {
                this._openStagingForm(context);
                return;
            }

            // Extract digits from the barcode
            const barcodeDigits = barcode.match(/\d+/g)?.join('') || '';

            // Try to find exact match by numeric part only
            const exact_asset = asset.find(i => {
                const refDigits = i.alternative_ref?.match(/\d+/g)?.join('') || '';
                return refDigits === barcodeDigits && i.alternative_ref?.endsWith(barcodeDigits);
            });

            if (exact_asset) {
                Object.assign(context, {
                    default_asset_id: exact_asset.id,
                    default_name: exact_asset.name,
                    default_asset_type_id: exact_asset.asset_type_id[0],
                    default_description: exact_asset.description,
                    default_barcode_number: barcode,
                    default_location: exact_asset.location_id?.[0],
                });

                this._openVerificationForm(context);
            } else {
                this._openStagingForm(context);
            }
        });
    },

    // Reuse helper to open verification form
    _openVerificationForm(context) {
        this.do_action({
            type: 'ir.actions.act_window',
            res_model: 'asset.verification',
            view_mode: 'form',
            views: [[false, 'form']],
            context,
            target: 'new',
        });
    },

    // Reuse helper to open staging form
    _openStagingForm(context) {
        this.displayNotification({
            title: 'There is no asset with this barcode. Please try with another code',
            type: 'danger',
        });
        this.do_action({
            type: 'ir.actions.act_window',
            res_model: 'asset.verification.staging',
            view_mode: 'form',
            views: [[false, 'form']],
            context,
            target: 'new',
        });
    }
    });

    core.action_registry.add('account_alternative_ref', AssetVerification);
    return AssetVerification;
});