/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

import { Component, useRef, onWillStart } from "@odoo/owl";

class EsystemSystray extends owl.Component {
    setup() {
        this.hm = useService("home_menu");
        this.studio = useService("studio");
        this.user = useService("user");
        this.rootRef = useRef("root");
        this.env.bus.on("ACTION_MANAGER:UI-UPDATED", this, (mode) => {
            if (mode !== "new" && this.rootRef.el) {
                this.rootRef.el.classList.toggle("d-lg-none", this.buttonDisabled);
            }
        });
        onWillStart(async () => {
            this.isStudioUser = await this.user.hasGroup("e_system.group_studio_access");
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

// replace the systray item
EsystemSystray.template = "e_system.SystrayItem";

export const systrayItem = {
    Component: EsystemSystray,
    isDisplayed: (env) => env.services.user.isSystem,
//    isDisplayed: async (env) => {
//        const hasGroup = await env.services.user.hasGroup("e_system.group_studio_access");
//        return hasGroup;
//    },
};

registry.category("systray").add("EsystemSystrayItem", systrayItem, { sequence: 1 });















///** @odoo-module **/
//import { patch } from "@web/core/utils/patch";
//import { systrayItem } from "@web_studio/systray_item/systray_item";
//
//patch(systrayItem, 'e_system.custom_systray_item',{
//    async isDisplayed(env) {
//        const hasGroup = await env.services.user.hasGroup("e_system.group_studio_access");
//        console.log("=== group check ===", hasGroup);
//        return hasGroup;  // return true only if user has the group
//    },
//});

//import { registry } from "@web/core/registry";
//import { user } from "@web/core/user";
//import { patch } from "@web/core/utils/patch";
//const systrayRegistry = registry.category("systray");
//
//patch(systrayRegistry.get("StudioSystrayItem"), {
//  isDisplayed: async (env) => {
//    console.log("\n\n===group===",env.services.user.hasGroup("e_system.group_studio_access"))
//    if (!(await env.services.user.hasGroup("e_system.group_studio_access"))) {
//      return false;
//    }
//    return true;
//  },
//});