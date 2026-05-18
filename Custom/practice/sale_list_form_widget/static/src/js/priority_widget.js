/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";


// --- Define the OWL Component ---
export class PriorityBadgeWidget extends Component {
    // This tells OWL which XML template to use for rendering.
    // The name must match the `t-name` in your .xml file.
    static template = "sale_list_form_widget.PriorityBadge";

    // Props are what the list renderer passes to your widget.
    // standardFieldProps includes: value, update, record, readonly...
    static props = { ...standardFieldProps };

    get badgeClass() {
        const val = this.props.value; // the actual field value from the record
        if (val === "1") return "badge-high";
        if (val === "2") return "badge-very-high";
        return "badge-normal";
    }

    // Another computed getter — returns human-readable label
    get badgeLabel() {
        const val = this.props.value;
        if (val === "1") return "High";
        if (val === "2") return "Very High";
        return "Normal";
    }
}

// --- Register the widget in Odoo's field registry ---
// "fields" registry is specifically for view field widgets.
// First arg: the name you'll use in XML as widget="priority_badge"
// Second arg: the component + supported field types
registry.category("fields").add("priority_badge", {
    component: PriorityBadgeWidget,
    // supportedTypes tells Odoo which field types this widget can render.
    // "selection" means it works on Selection fields (like priority).
    supportedTypes: ["selection"],
});