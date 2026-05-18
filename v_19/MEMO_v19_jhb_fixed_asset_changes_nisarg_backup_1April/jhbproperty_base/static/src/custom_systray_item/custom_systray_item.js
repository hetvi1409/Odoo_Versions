/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";
import { PromoteStudioDialog } from "@web_enterprise/webclient/promote_studio/promote_studio_dialog";
import { Component, onWillStart } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

export class EsystemSystrayItem extends Component {
    static template = "e_system.SystrayItem";

    setup() {
        this.dialog = useService("dialog");
        this.hasStudioAccess = false;

        onWillStart(async () => {
            this.hasStudioAccess = await user.hasGroup("e_system.group_studio_access");
        });
    }

    get isVisible() {
        return this.hasStudioAccess && user.isSystem;
    }

    onClick() {
        this.dialog.add(PromoteStudioDialog, {
            title: _t("Odoo Studio – Customize your views"),
        });
    }
}

export const esystemSystrayItem = {
    Component: EsystemSystrayItem,
    isDisplayed: () => user.isSystem,
};

registry
    .category("systray")
    .add("EsystemSystrayItem", esystemSystrayItem, { sequence: 1 });


//import { registry } from "@web/core/registry";
//import { useBus, useService } from "@web/core/utils/hooks";
//import { user } from "@web/core/user";
//import { Component, useRef, onWillStart } from "@odoo/owl";
//
//class EsystemSystray extends owl.Component {
//    static props = {};
//    setup() {
//        this.hm = useService("home_menu");
//        this.studio = useService("studio");
//        this.rootRef = useRef("root");
//        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", ({ detail: mode }) => {
//            if (mode !== "new" && this.rootRef.el) {
//                this.rootRef.el.classList.toggle("d-lg-none", this.buttonDisabled);
//            }
//        });
//        onWillStart(async () => {
//            this.isStudioUser = await user.hasGroup("e_system.group_studio_access");
//        });
//
//    }
//    get buttonDisabled() {
//        console.log("\n\n==this.isStudioUser===",this.isStudioUser)
//        console.log("\n\n==this.this.studio.isStudioEditable()===",this.studio.isStudioEditable())
//        return !(this.isStudioUser && this.studio.isStudioEditable());
//    }
//    _onClick() {
//        this.studio.open();
//    }
//}
//
//// replace the systray item
//EsystemSystray.template = "e_system.SystrayItem";
//
//export const systrayItem = {
//    Component: EsystemSystray,
//    isDisplayed: (env) => user.isSystem,
////    isDisplayed: async (env) => {
////        const hasGroup = await env.services.user.hasGroup("e_system.group_studio_access");
////        return hasGroup;
////    },
//};
//
//registry.category("systray").add("EsystemSystrayItem", systrayItem, { sequence: 1 });















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