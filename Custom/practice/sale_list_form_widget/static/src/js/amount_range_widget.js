/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class AmountRangeWidget extends Component {
    static template = "sale_list_form_widget.AmountRange";
    static props = { ...standardFieldProps };

    static LOW_MAX  = 100;
    static HIGH_MIN = 500;
    static BAR_MAX  = 900;

    get amount() {
        console.log('Amount:', this);
        return this.props.record.data.amount_total || 0;
    }

    // bar fill percentage, capped at 100
    get fillPercent() {
        const pct = (this.props.record.data.amount_total / AmountRangeWidget.BAR_MAX) * 100;
        return Math.min(pct, 100).toFixed(1);
    }

    get colorClass() {
        if (this.props.record.data.amount_total < AmountRangeWidget.LOW_MAX)  return "range-low";
        if (this.props.record.data.amount_total >= AmountRangeWidget.HIGH_MIN) return "range-high";
        return "range-mid";
    }

    get formattedAmount() {
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0,
        }).format(this.props.record.data.amount_total);
    }
}

registry.category("fields").add("amount_range", {component: AmountRangeWidget,supportedTypes: ["monetary", "float"],});