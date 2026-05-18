/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { formatMonetary } from "@web/views/fields/formatters";

export class ColorAmountField extends Component {
    static template = "view_customization.ColorAmountField";
    static props = {
        ...standardFieldProps,
    };

    get amount() {
        return this.props.record.data[this.props.name] || 0;
    }

    get colorStyle() {
        const amount = this.amount;
        if (amount > 50000) {
            return {
                color: '#dc3545',       // Red
                fontWeight: 'bold',
                fontSize: '16px',
            };
        } else if (amount >= 10000) {
            return {
                color: '#ffc107',       // Yellow
                fontWeight: 'bold',
                fontSize: '16px',
            };
        } else {
            return {
                color: '#28a745',       // Green
                fontWeight: 'bold',
                fontSize: '16px',
            };
        }
    }

    get formattedAmount() {
        return `₹${this.amount.toFixed(2)}`;
    }

    get label() {
        if (this.amount > 50000) return "🔴 High Value";
        if (this.amount >= 10000) return "🟡 Medium Value";
        return "🟢 Low Value";
    }
}

registry.category("fields").add("color_amount", ColorAmountField);