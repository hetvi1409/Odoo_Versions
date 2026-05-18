/** @odoo-module **/
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";

import { Component, useRef, onWillStart } from "@odoo/owl";

class EsystemSystray extends Component {
    static template = "ecdhs_base.SystrayItem";
    static props = {};
    setup() {
        this.hm = useService("home_menu");
        this.studio = useService("studio");
        this.rootRef = useRef("root");
        this.env.bus.addEventListener("ACTION_MANAGER:UI-UPDATED", (ev) => {
            const mode = ev.detail;
            if (mode !== "new" && this.rootRef.el) {
                this.rootRef.el.classList.toggle("d-lg-none", this.buttonDisabled);
            }
        });
        onWillStart(async () => {
            this.isStudioUser = await user.hasGroup("e_system.group_studio_access");
        });
    }
    get buttonDisabled() {
        console.log("\n\n==this.isStudioUser===",this.isStudioUser)
        console.log("\n\n==this.this.studio.isStudioEditable()===",this.studio.isStudioEditable())
        return !(this.isStudioUser && this.studio.isStudioEditable());
    }
    _onClick() {
        this.studio.open();
    }
}

export const systrayItem = {
    Component: EsystemSystray,
    isDisplayed: () => user.isSystem,
};

registry.category("systray").add("EsystemSystray", systrayItem, { sequence: 1 });
