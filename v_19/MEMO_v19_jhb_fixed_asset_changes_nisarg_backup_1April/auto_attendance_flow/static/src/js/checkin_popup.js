/** @odoo-module **/
odoo.define('auto_attendance_flow.checkin_popup', function (require) {
    var ajax = require('web.ajax');
    var session = require('web.session');

    $(document).ready(function () {
        console.log("\n\n==window.location==",window.location)
//        $(document).on("click", "#web_log_in", function(e) {
////            if (window.location.pathname == '/web') {
//                e.preventDefault()
////                ajax.jsonRpc('/web/get_login_response_value/call_kw', 'call', {'user_id': session.uid || session.user_id}).then(function (result) {
////                        console.log("\n\n===result===",result)
////                    });
//                var modal = $(document).find('#login_confirm_modal').modal('show');
//                setTimeout(function () {
//                    $('#login_confirm_modal').modal('hide');
//                }, 20000);
////            }
//        });

    });
});