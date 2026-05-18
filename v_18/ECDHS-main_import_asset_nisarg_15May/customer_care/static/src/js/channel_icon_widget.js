/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class ChannelIconWidget extends Component {
    static props = standardFieldProps;
    static template = "customer_care.ChannelIconWidget"; // XML template

    get channelIcon() {
        const channel = this.props.record.data.channel;
        const iconMap = {
            "facebook": "fa fa-facebook text-primary",
            "whatsapp": "fa fa-whatsapp text-success",
            "tiktok": "fa fa-tiktok text-dark",
            "email": "fa fa-envelope text-danger",
            "walk_in": "fa fa-user text-muted",
            "phone_call": "fa fa-phone text-info",
            "hotline": "fa fa-bullhorn text-warning",
            "correspondence": "fa fa-file-text text-brown",
            "website": "fa fa-globe text-primary",
        };
        return iconMap[channel] || "fa fa-question text-secondary"; // Default icon
    }
}

export const channelIconField = {
    component: ChannelIconWidget,
    displayName: "Channel Icon",
    supportedTypes: ["char"],
};

registry.category("fields").add("channel_icon", channelIconField);
