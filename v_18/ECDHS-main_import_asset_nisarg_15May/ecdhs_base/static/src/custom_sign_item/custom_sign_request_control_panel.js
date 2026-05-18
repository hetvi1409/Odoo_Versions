/** @odoo-module **/

import { user } from "@web/core/user";
import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { SignRequestControlPanel } from "@sign/backend_components/sign_request/sign_request_control_panel";

// Patch the original component to add showCertificateButton
patch(SignRequestControlPanel.prototype, {
    setup() {
        // call the original setup
        super.setup();

        // add our custom group check
        onWillStart(async () => {
            this.isSignAdmin = await user.hasGroup("sign.group_sign_manager");
        });
    },
    get showCertificateButton() {
        // Only allow system users
        console.log("\n\n====call custom=this.isSignAdmin==",this.isSignAdmin)
        return !!this.isSignAdmin;
    },
    get showSignNowButton() {
        // Only allow system users
        console.log("\n\n====call custom=this.isSignAdmin==",this.isSignAdmin)
        // Treat user with id=2 (Administrator) as sign admin
        this.isSignAdmin = user.userId === 2 || !!this.isSignAdmin;
        return !!this.isSignAdmin;
    },
});
