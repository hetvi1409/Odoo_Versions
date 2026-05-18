/** @odoo-module **/

// ─────────────────────────────────────────────────────────────────────────────
// SaleFormRenderer
//
// PURPOSE:
//   Extends Odoo 18's default FormRenderer to add extra behavior on the
//   sale.order form view:
//     1. Highlights the form header with a dynamic color based on state
//     2. Adds a JS-driven "quick info" banner below the breadcrumb
//     3. Patches the renderer so our custom OWL template is used
//
// HOW FORM RENDERER EXTENSION WORKS IN ODOO 18:
//   - FormRenderer is the OWL component responsible for rendering <form> views
//   - We import it, subclass it, override its template, and register it
//     in the "views" registry under the key "form" — but ONLY for sale.order
//     (we do this scoping via the view XML's js_class attribute)
//
// IMPORTANT:
//   We use `js_class="sale_form_custom"` in the view XML.
//   This tells Odoo: "use the view registered under 'sale_form_custom'
//   from the views registry" instead of the default form renderer.
// ─────────────────────────────────────────────────────────────────────────────

import { FormRenderer } from "@web/views/form/form_renderer";
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { registry } from "@web/core/registry";

// ── 1. Custom Renderer ────────────────────────────────────────────────────────

export class SaleFormRenderer extends FormRenderer {
    // Point to our custom OWL template (defined in sale_form_renderer.xml)
    // This template EXTENDS the default FormRenderer template so we don't
    // lose any standard form functionality.
    static template = "sale_form_custom.SaleFormRenderer";

    // ── State color based on sale.order state ───────────────────────────────
    // Called from the OWL template via t-att-class
    get headerColorClass() {
        // Access the current record through the model
        // In Odoo 18 FormRenderer, props.model.root is the record
        const state = this.props.model?.root?.data?.state;
        const map = {
            draft:  "state-draft",
            sent:   "state-sent",
            sale:   "state-confirmed",
            done:   "state-locked",
            cancel: "state-cancelled",
        };
        return map[state] || "state-draft";
    }

    // ── Human-readable state label ──────────────────────────────────────────
    get stateLabel() {
        const state = this.props.model?.root?.data?.state;
        const labels = {
            draft:  "Draft Quotation",
            sent:   "Quotation Sent",
            sale:   "Confirmed Order",
            done:   "Locked",
            cancel: "Cancelled",
        };
        return labels[state] || "Draft";
    }

    // ── Customer name for the info banner ───────────────────────────────────
    get partnerName() {
        // partner_id is a many2one → data.partner_id = [id, "display_name"]
        return this.props.model?.root?.data?.partner_id?.[1] || "—";
    }

    // ── Order date formatted ─────────────────────────────────────────────────
    get orderDate() {
        const dt = this.props.model?.root?.data?.date_order;
        if (!dt) return "—";
        // dt is a luxon DateTime object in Odoo 18
        // .toFormat() is luxon's formatting method
        try {
            return dt.toFormat("dd MMM yyyy");
        } catch {
            return String(dt);
        }
    }

    // ── Order name / reference ───────────────────────────────────────────────
    get orderName() {
        return this.props.model?.root?.data?.name || "New";
    }

    // ── Is this a new (unsaved) record? ──────────────────────────────────────
    get isNew() {
        // isNew is true when the record has never been saved
        return this.props.model?.root?.isNew;
    }
}

// ── 2. Custom Controller ──────────────────────────────────────────────────────
// We extend FormController only to bind our custom renderer.
// FormController handles save/discard/action buttons.
// We don't change any logic here — just wire up the renderer.

export class SaleFormController extends FormController {}

// ── 3. Register the custom view ───────────────────────────────────────────────
// "views" registry maps js_class names → view descriptors
// A view descriptor = { type, Controller, Renderer, Model, ... }
//
// We spread formView (the default form view descriptor) and override
// only Renderer and Controller with our custom classes.

registry.category("views").add("sale_form_custom", {
    ...formView,                        // inherit everything from standard form
    Controller: SaleFormController,     // our controller (same behavior)
    Renderer: SaleFormRenderer,         // our renderer (custom template + getters)
});
