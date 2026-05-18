from odoo import models, fields, api
from odoo.exceptions import UserError


class UtilityBillingWizard(models.TransientModel):
    _name = "utility.billing.wizard"
    _description = "Batch Utility Billing Wizard"

    company_id = fields.Many2one("res.company",
                                 default=lambda self: self.env.company,
                                 required=True)
    utility_type = fields.Selection(
        [("water", "Water"), ("electricity", "Electricity")],
        required=True
    )
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    auto_invoice_date = fields.Date(
        help="If provided, set as invoice date; else reading date is used.")
    only_active_meters = fields.Boolean(default=True,
                                        help="Respect move-in/move-out dates.")

    def action_generate(self):
        self.ensure_one()
        if self.period_start > self.period_end:
            raise UserError("Period start must be before period end.")

            # Find readings in period and generate invoices
        domain = [
            ("company_id", "=", self.company_id.id),
            ("utility_type", "=", self.utility_type),
            ("billing_period_start", "=", self.period_start),
            ("billing_period_end", "=", self.period_end),
            ("invoiced", "=", False),
        ]
        readings = self.env["utility.meter.reading"].search(domain)
        if not readings:
            raise UserError("No readings found for the given filters.")

        for r in readings:
            if self.only_active_meters:
                m = r.meter_id
                if m.move_in_date and self.period_end < m.move_in_date:
                    continue
                if m.move_out_date and self.period_start > m.move_out_date:
                    continue
            action = r._generate_invoice_one()
            if self.auto_invoice_date and r.invoice_id:
                r.invoice_id.invoice_date = self.auto_invoice_date
                # Optionally return last invoice or a list view
        return {"type": "ir.actions.act_window_close"}
