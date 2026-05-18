odoo.define('oehealth_patient_portal.add_detail', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');
    var utils = require('web.utils');
    var rpc = require('web.rpc');
    var _t = core._t;

    $(document).ready(function() {

        $("#patient_img_upload_btn").on('click', function () {
             $('#patient_img_upload_dialog').modal('show');
        });

        $("#patient_img_remove_btn").on('click', function () {
             $('#patient_img_remove_dialog').modal('show');
        });

    });

});
