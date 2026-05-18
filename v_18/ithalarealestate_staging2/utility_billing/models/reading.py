from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class UtilityMeterReading(models.Model):
    _name = "utility.meter.reading"
    _description = "Utility Meter Reading"
    _order = "reading_date desc, id desc"
    _rec_name = "meter_id"

    company_id = fields.Many2one("res.company",
                                 default=lambda self: self.env.company,
                                 required=True)
    meter_id = fields.Many2one("utility.meter", required=True,
                               ondelete="cascade")
    partner_id = fields.Many2one("res.partner", related="meter_id.partner_id",
                                 store=True, readonly=True)
    utility_type = fields.Selection(related="meter_id.utility_type", store=True,
                                    readonly=True)

    reading_date = fields.Date(required=True)
    billing_period_start = fields.Date(required=True)
    billing_period_end = fields.Date(required=True)

    previous_reading = fields.Float(compute="_compute_previous_reading", readonly=True)
    reading = fields.Float(required=True)
    consumption = fields.Float(compute="_compute_consumption", store=True)

    invoice_id = fields.Many2one("account.move", readonly=True)
    invoice_amount = fields.Float(compute="_compute_invoice_amount")

    abnormal_usage = fields.Boolean("Abnormal Usage", compute="_compute_abnormal_usage", store=True)

    # Integration
    integration_source = fields.Selection([
        ('manual', 'Manual'),
        ('bulk_import', 'Bulk Import'),
        ('iot', 'IoT Integration'),
    ], string="Source", default='manual')
    external_sync_id = fields.Char("External Sync Reference")
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], default='pending')

    # Sustainability
    renewable_share = fields.Float("Renewable Share (%)")
    carbon_emission = fields.Float("Carbon Emission (kg CO₂)", compute="_compute_carbon_emission", store=True)

    @api.depends('consumption', 'meter_id.alert_threshold')
    def _compute_abnormal_usage(self):
        for rec in self:
            threshold = rec.meter_id.alert_threshold or 0.0
            rec.abnormal_usage = rec.consumption > threshold

    @api.depends('consumption', 'renewable_share')
    def _compute_carbon_emission(self):
        for rec in self:
            base = rec.consumption * 0.5
            rec.carbon_emission = base - (base * (rec.renewable_share or 0.0) / 100.0)

    def action_generate_alert(self):
        for rec in self:
            if rec.abnormal_usage:
                self.env['helpdesk.ticket'].create({
                    'name': _("Abnormal Usage Alert"),
                    'description': _("Meter %s exceeded threshold on %s.") % (rec.meter_id.name, rec.reading_date),
                    'partner_id': rec.partner_id.id,
                })
        return True

    @api.constrains('reading')
    def _check_reading_non_negative(self):
        for rec in self:
            if rec.reading < 0:
                raise ValidationError(_("Reading value cannot be negative."))

    @api.constrains('reading', 'previous_reading')
    def _check_reading_progression(self):
        for rec in self:
            if rec.reading < rec.previous_reading:
                raise ValidationError("Reading must be greater than or equal to previous reading.")

    @api.depends('reading', 'meter_id', 'consumption')
    def _compute_invoice_amount(self):
        for rec in self:
            rec.invoice_amount = 10
            plan = rec.meter_id.tariff_id
            total = 0
            remaining = rec.consumption
            for block in plan.block_ids:

                block_cap = (block.to_qty or remaining + block.from_qty) - block.from_qty
                units = min(block_cap, remaining)
                total += units * block.price_per_unit
                remaining -= units
                rec.invoice_amount = total

    _sql_constraints = [
        ("unique_meter_period",
         "unique(meter_id, billing_period_start, billing_period_end)",
         "A meter cannot have duplicate readings for the same billing period.")
    ]

    @api.depends("reading", "previous_reading")
    def _compute_consumption(self):
        for rec in self:
            rec.consumption = max(
                (rec.reading or 0) - (rec.previous_reading or 0), 0.0)

    @api.depends("meter_id", "reading_date", "billing_period_start",
                  "billing_period_end")
    def _compute_previous_reading(self):
        for rec in self:
            if rec.meter_id:
                # prev = rec._get_previous_reading_value()
                meter = rec.meter_id
                if not meter:
                    return 0.0
                last = rec.search([
                    ("meter_id", "=", meter.id), ('id', '!=', rec.id),
                    ("reading_date", "<",
                     rec.reading_date ),
                ], order="reading_date desc, id desc", limit=1)
                rec.previous_reading = last.reading

    def _get_previous_reading_value(self):
        self.ensure_one()
        meter = self.meter_id
        if not meter:
            return 0.0
        last = self.search([
            ("meter_id", "=", meter.id), ('id', '!=', self.id),
            ("reading_date", "<", self.reading_date or fields.Date.today()),
        ], order="reading_date desc, id desc", limit=1)
        return last.reading if last else (meter.start_reading or 0.0)
