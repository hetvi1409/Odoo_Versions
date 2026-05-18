/** @odoo-module **/

import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { SignTemplateControlPanel } from "@sign/backend_components/sign_template/sign_template_control_panel";

// ✅ Patch the original component
patch(SignTemplateControlPanel.prototype, {

    setup() {
        // call the original setup
        super.setup();

        // add our custom group check
        onWillStart(async () => {
            this.isStudioUser = await user.hasGroup("e_system.group_studio_access");
        });
    },

    // ✅ Our custom getter for the button
    get showSignNowButton() {
        console.log("\n\n====call custom===",this.isStudioUser)
        console.log("\n\n====call user.userId===",user.userId)
        // Treat user with id=2 (Administrator) as studio user
        this.isStudioUser = user.userId === 2 || !!this.isStudioUser;
        return !!this.isStudioUser;
    },
});
