/** @odoo-module **/

// ─────────────────────────────────────────────────────────────────────────────
// AmountSummaryWidget
//
// PURPOSE:
//   Displayed at the bottom of the sale order form.
//   Reads amount_untaxed, amount_tax, amount_total from the current record
//   and shows them as a styled summary card — no separate Python field needed.
//
// FIELD TYPES READ:
//   amount_untaxed  → monetary (float)
//   amount_tax      → monetary (float)
//   amount_total    → monetary (float)
//   currency_id     → many2one  [id, name]  e.g. [3, "INR"]
// ─────────────────────────────────────────────────────────────────────────────

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class AmountSummaryWidget extends Component {
    static template = "sale_form_custom.AmountSummary";

    // standardFieldProps gives us: value, record, readonly, update, …
    static props = { ...standardFieldProps };

    // ── helpers ──────────────────────────────────────────────────────────────

    // Formats a number as currency using the browser's Intl API.
    // We read the currency symbol from the record's currency_id field.
    _fmt(amount) {
        // currency_id is a many2one → props.record.data.currency_id = [id, "INR"]
        const currencyName = this.props.record.data.currency_id?.[1] || "INR";

        // Map Odoo currency names to ISO codes for Intl.NumberFormat
        const isoMap = { "INR": "INR", "USD": "USD", "EUR": "EUR", "GBP": "GBP" };
        const iso = isoMap[currencyName] || "INR";

        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: iso,
            maximumFractionDigits: 2,
        }).format(amount || 0);
    }

    // ── computed getters (used in OWL template via t-esc / t-att-*) ──────────

    get untaxed() {
        // amount_untaxed is a monetary field → raw float in props.record.data
        return this._fmt(this.props.record.data.amount_untaxed);
    }

    get tax() {
        return this._fmt(this.props.record.data.amount_tax);
    }

    get total() {
        return this._fmt(this.props.record.data.amount_total);
    }

    // Percentage of tax out of total — used for the visual bar
    get taxPercent() {
        const total = this.props.record.data.amount_total || 0;
        const tax   = this.props.record.data.amount_tax   || 0;
        if (!total) return 0;
        return Math.min((tax / total) * 100, 100).toFixed(1);
    }

    // Color class for total amount — low / mid / high thresholds
    get totalColorClass() {
        const total = this.props.record.data.amount_total || 0;
        if (total < 10000)  return "amt-low";
        if (total < 100000) return "amt-mid";
        return "amt-high";
    }
}

// Register as a field widget named "amount_summary"
// We attach it to the "amount_total" field in the form XML.
// supportedTypes: monetary covers amount_total.
registry.category("fields").add("amount_summary", {
    component: AmountSummaryWidget,
    supportedTypes: ["monetary", "float"],
});
