odoo.define("asset_verification.AssetVerification", function (require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var BarcodeScanner = require("@web/webclient/barcode/barcode_scanner");
    console.log(BarcodeScanner, 'BarcodeScanner')
    var AssetVerification = AbstractAction.extend({
        contentTemplate: 'AssetVerification',
        events: {
            'keypress': '_onKeypress',
            'change': '_onChange',
            'click .button_asset': 'openMobileScanner',
        },
        start: async function () {
            await this._super(...arguments);
            window.addEventListener('keydown', this._onMouseMove.bind(this));
            window.addEventListener('click', this._onMouseMove.bind(this));
            window.addEventListener('mousemove', this._onMouseMove.bind(this));
                this._addEventListeners();
            if(document.getElementById('oe_barcode_id')){
                document.getElementById('oe_barcode_id').focus();
            }
            this._fetchJobs();
        },
         _fetchJobs: function() {
            var self = this;
            console.log(this.getSession().uid,'dasde32434')
            this._rpc({
                model: "asset.verification.job",
                method: "search_read",
                fields: ["id", "name"],
                domain: [['user_ids', 'in', [this.getSession().uid]]],
            }).then(function(jobs) {
                self.jobs = jobs;
                self._renderJobOptions();
            });
        },
        _onJobSelectionChange: function(event) {
            this.selectedJobId = event.target.value;
            this.update();
        },
        _renderJobOptions: function() {
            var selectElement = document.getElementById('verificationJobSelection');
            selectElement.innerHTML = '';
            this.jobs.forEach(function(job) {
                var option = document.createElement('option');
                option.value = job.id;
                option.textContent = job.name;
                selectElement.appendChild(option);
            });
        },
        /* focusing the input field */
		_onMouseMove: function() {
    var barcodeInput = document.getElementById('oe_barcode_id');
    var selectionField = document.getElementById('verificationJobSelection');

    // Check if there is a modal or dialog open
    var isModalOpen = document.querySelector('.modal') !== null;
    var isDropdownOpen = document.querySelector('.dropdown-menu.show') !== null;

    // Check if the barcode input exists and no other input field is currently focused
    // Also check if the selection field is not focused
    if (barcodeInput && !isModalOpen && !isDropdownOpen && document.activeElement !== selectionField) {
        barcodeInput.focus();
    }
},

_addEventListeners: function() {
    var selectionField = document.getElementById('verificationJobSelection');
    var barcodeInput = document.getElementById('oe_barcode_id');

    if (selectionField) {
        selectionField.addEventListener('focusout', function() {
            setTimeout(function() {
                // Re-focus the barcode input after the selection field loses focus
                barcodeInput.focus();
            }, 0); // Use a timeout to ensure the focus shift is handled correctly
        });
    }
},


		/* Triggering flag for removing the duplicating the scan */
        _onKeypress: function(data) {
            this.typed_into = true;
        },
        /* scanning using gun */
        _onChange: function(data) {
    var self = this;

    // Get the selected verification job
    var selectedJobId = document.getElementById('verificationJobSelection').value;

    // Check if a job is selected
    if (!selectedJobId) {
        self.displayNotification({
            title: 'Please select a verification job before scanning a barcode.',
            type: 'warning',
        });
        return;
    }

    var barcode = document.getElementById('oe_barcode_id').value;
    console.log(this.typed_into, barcode);

    if (this.typed_into) {
        this.typed_into = false;

        this._rpc({
            model: "account.asset",
            method: "search_read",
            fields: [
                "id", "name", "asset_type_id",
                "description", "alternative_ref",
                "location_id","current_condition_this_year",
                "custodian_id",
            ],
            domain: [["identification_number", "=", barcode]],
        }).then(function(asset) {
            console.log('asset', asset);

            if (asset.length == 0) {
                // Asset not found, redirect to staging model form for data entry
                console.log('Asset not found, redirecting to staging form');
                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'asset.verification.staging',  // Redirecting to the staging model
                    view_mode: 'form',
                    view_type: 'form',
                    views: [[false, 'form']],
                    context: {
                        default_barcode: barcode,  // Pass the scanned barcode to the new form
                        default_verification_job_id: parseInt(selectedJobId),
                        default_user_id: self.getSession().uid,

                        // Add any additional default values here if needed
                    },
                    target: 'new',
                });

                self.displayNotification({
                    title: 'Asset not found. You can enter the details to create a new asset.',
                    type: 'danger',
                });

            } else {
                console.log(asset[0].custodian_id[0],'dsaddada')
                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'asset.verification',
                    view_mode: 'form',
                    view_type: 'form',
                    views: [[false, 'form']],
                    context: {
                        default_asset_id: asset[0].id,
                        default_name: asset[0].name,
                        default_asset_type_id: asset[0].asset_type_id[0],
                        default_barcode_number: barcode,
                        default_description: asset[0].description,
                        default_verification_job_id: parseInt(selectedJobId),
//                        default_allocation: asset[0].allocation,
                        default_location: asset[0].location_id[0],
//                        default_condition: asset[0].condition,
                        default_user_id: self.getSession().uid,
                        default_custodian_id: asset[0].custodian_id[0]

                    },
                    target: 'new',
                });
            }
        });

        document.getElementById('oe_barcode_id').value = '';
    }
},

        /* scanning from the webcam */
         async openMobileScanner() {
            console.log('openMobileScanner');
            const barcode = await BarcodeScanner.scanBarcode();
            console.log('barcode', barcode);
            if (barcode) {
                // Reuse _onChange logic for barcode processing
                var self = this;
                // Get the selected verification job
                var selectedJobId = document.getElementById('verificationJobSelection').value;

                // Check if a job is selected
                if (!selectedJobId) {
                    self.displayNotification({
                        title: 'Please select a verification job before scanning a barcode.',
                        type: 'warning',
                    });
                    return;
                }

                this._rpc({
                    model: "account.asset",
                    method: "search_read",
                    fields: [
                        "id", "name", "asset_type_id",
                        "description", "alternative_ref",
                        "location_id", "current_condition_this_year",
                    ],
                    domain: [["alternative_ref", "=", barcode]],
                }).then(function(asset) {
                    if (asset.length == 0) {
                        console.log('Asset not found');
                        self.displayNotification({
                            title: 'There is no asset with this barcode. Please try with another code',
                            type: 'danger',
                        });
                        self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: 'asset.verification.staging',
                            view_mode: 'form',
                            view_type: 'form',
                            views: [[false, 'form']],
                            context: {
                                default_barcode: barcode,
                                default_verification_job_id: parseInt(selectedJobId),
                            },
                            target: 'new',
                        });
                    } else {
                        self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: 'asset.verification',
                            view_mode: 'form',
                            view_type: 'form',
                            views: [[false, 'form']],
                            context: {
                                default_asset_id: asset[0].id,
                                default_name: asset[0].name,
                                default_asset_type_id: asset[0].asset_type_id[0],
                                default_barcode_number: barcode,
                                default_description: asset[0].description,
                                default_verification_job_id: parseInt(selectedJobId),
                                default_location: asset[0].location_id[0],
                            },
                            target: 'new',
                        });
                    }
                });
            } else {
                this.notificationService.add(this.env._t("Please, Scan again !"), { type: 'warning' });
            }
        },

   });
   core.action_registry.add('account_alternative_ref', AssetVerification);
   return AssetVerification;
});