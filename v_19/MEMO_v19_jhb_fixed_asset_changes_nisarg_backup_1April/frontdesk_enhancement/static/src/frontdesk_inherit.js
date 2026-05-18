// javascript
/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Frontdesk } from "@frontdesk/frontdesk";

patch(Frontdesk.prototype, {

    setup() {
        super.setup();
        this.inputPropertyType = null;
    },

    setPropertyType(value) {
        this.inputPropertyType = value;
    },

    async createVisitor() {
        const result = await rpc(`${this.frontdeskUrl}/prepare_visitor_data`, {
            name: this.visitorData.visitorName,
            phone: this.visitorData.visitorPhone,
            email: this.visitorData.visitorEmail,
            company: this.visitorData.visitorCompany,
            property_type: this.inputPropertyType,
            host_ids: this.hostData ? [this.hostData.hostId] : [],
        });
        this.visitorId = result.visitor_id;
    },

});

// Register the (patched) Frontdesk class as the public component named "frontdesk"
registry.category("public_components").add("frontdesk", Frontdesk);
