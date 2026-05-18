/** @odoo-module **/

// ─────────────────────────────────────────────────────────────────────────────
// StatusBarWidget
//
// PURPOSE:
//   A custom visual status bar for sale.order's "state" field.
//   Replaces the default statusbar widget with a horizontal step-indicator
//   that shows: Draft → Quotation Sent → Sales Order → Locked → Cancelled
//
// HOW IT WORKS:
//   - Reads this.props.value  (the current state string, e.g. "sale")
//   - Renders each step; highlights the current and completed steps
//   - Read-only display only (not interactive — state changes via buttons)
//
// FIELD TYPE:
//   state → selection field → supportedTypes: ["selection"]
// ─────────────────────────────────────────────────────────────────────────────

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class StatusBarWidget extends Component {
    static template = "sale_form_custom.StatusBar";
    static props = { ...standardFieldProps };

    // Define the ordered steps for sale.order state
    // key   = value stored in DB (from selection field definition)
    // label = human readable label shown in UI
    static STEPS = [
        { key: "draft",      label: "Quotation"      },
        { key: "sent",       label: "Quotation Sent" },
        { key: "sale",       label: "Sales Order"    },
        { key: "done",       label: "Locked"         },
        { key: "cancel",     label: "Cancelled"      },
    ];

    // this.props.value = the current state string e.g. "sale"
    get currentKey() {
        return this.props.value || "draft";
    }

    // Index of the currently active step (0-based)
    get currentIndex() {
        return StatusBarWidget.STEPS.findIndex(s => s.key === this.currentKey);
    }

    // Build step objects with status flags for the OWL template
    // Each step gets: key, label, isDone, isActive, isCancelled
    get steps() {
        const idx = this.currentIndex;
        const isCancelled = this.currentKey === "cancel";

        return StatusBarWidget.STEPS.map((step, i) => ({
            ...step,
            // isCancelled: only the cancel step itself
            isCancelled: isCancelled && step.key === "cancel",
            // isActive: the step we are currently on (not cancelled)
            isActive: !isCancelled && i === idx,
            // isDone: steps before the current one (not cancelled flow)
            isDone: !isCancelled && i < idx,
        }));
    }

    // Progress bar fill % (0–100) based on current step
    // Used to draw the connecting line fill in the template
    get progressPercent() {
        if (this.currentKey === "cancel") return 0;
        const total = StatusBarWidget.STEPS.length - 2; // exclude cancel from progress
        const done  = Math.min(this.currentIndex, total);
        return Math.round((done / total) * 100);
    }
}

registry.category("fields").add("sale_status_bar", {
    component: StatusBarWidget,
    supportedTypes: ["selection"],
});
