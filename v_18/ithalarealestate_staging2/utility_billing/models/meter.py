from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class UtilityMeter(models.Model):
    _name = "utility.meter"
    _description = "Utility Meter"
    _order = "name"

    name = fields.Char(required=True, help="Meter ID/Serial")
    utility_type = fields.Selection([
        ("water", "Water"),
        ("electricity", "Electricity"),
        ("gas", "Gas"),
        ("solar", "Solar"),
        ("refuse_collection", "Refuse Collection"),
        ("sewage", "Sewage"),
        ("other", "Other"),
    ], required=True)

    company_id = fields.Many2one("res.company",
                                 default=lambda self: self.env.company,
                                 required=True)
    contract_id = fields.Many2one('rental.contract', domain="[('state', '=', 'confirmed')]",
                                  required=True, string="Lease Contract")
    property_id = fields.Many2one("building", string="Property", required=False)
    partner_id = fields.Many2one("res.partner", string="Tenant", required=True)
    building_id = fields.Many2one('product.template', required=True,
                                  domain="[('is_property','=',True), ('tenant_id', '=', partner_id)]",
                                  string="Building Unit")

    # Optional: link to a unit or property text
    unit_reference = fields.Char(help="e.g., Unit 3B, 12 Rose St")
    service_address = fields.Char()
    tariff_id = fields.Many2one("utility.tariff", required=True,
                                domain="[('utility_type', '=', utility_type)]")
    start_reading = fields.Float(default=0.0)
    move_in_date = fields.Date()
    move_out_date = fields.Date()
    active = fields.Boolean(default=True)

    reading_ids = fields.One2many("utility.meter.reading", "meter_id",
                                  string="Readings")

    # Monitoring & alerts
    alert_threshold = fields.Float("Alert Threshold", default=100.0)
    last_reading = fields.Float("Last Reading", compute="_compute_last_reading", store=True)
    last_reading_date = fields.Date("Last Reading Date", compute="_compute_last_reading", store=True)
    abnormal_usage = fields.Boolean("Abnormal Usage", compute="_compute_meter_abnormal_usage", store=True)

    # Integration
    integration_source = fields.Selection([
        ('manual', 'Manual'),
        ('bulk_import', 'Bulk Import'),
        ('iot', 'IoT Integration'),
    ], string="Integration Source", default='manual')
    external_sync_id = fields.Char("External Sync Reference")
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], default='pending')

    # Sustainability
    renewable_share = fields.Float("Renewable Share (%)")
    carbon_emission_estimate = fields.Float("Carbon Emission (kg CO₂)",
                                            compute="_compute_meter_emission", store=True)

    @api.depends('reading_ids.reading', 'reading_ids.reading_date')
    def _compute_last_reading(self):
        for meter in self:
            if meter.reading_ids:
                last = meter.reading_ids.sorted(key=lambda r: (r.reading_date, r.id), reverse=True)[0]
                meter.last_reading = last.reading
                meter.last_reading_date = last.reading_date
            else:
                meter.last_reading = 0.0
                meter.last_reading_date = False

    @api.depends('reading_ids.consumption', 'alert_threshold')
    def _compute_meter_abnormal_usage(self):
        for meter in self:
            total = sum(meter.reading_ids.mapped('consumption'))
            meter.abnormal_usage = total > (meter.alert_threshold or 0.0)

    @api.depends('reading_ids.consumption', 'renewable_share')
    def _compute_meter_emission(self):
        for meter in self:
            total_cons = sum(meter.reading_ids.mapped('consumption'))
            base = total_cons * 0.5
            meter.carbon_emission_estimate = base - (base * (meter.renewable_share or 0.0) / 100.0)


    @api.onchange('contract_id')
    def _onchange_contract(self):
        """Contract"""
        self.property_id = self.contract_id.building.id
        self.building_id = self.contract_id.building_unit.id
        self.unit_reference = self.contract_id.building_unit.code
        self.partner_id = self.contract_id.partner_id.id

    @api.constrains("tariff_id", "utility_type")
    def _check_tariff_matches_type(self):
        for rec in self:
            if rec.tariff_id and rec.tariff_id.utility_type != rec.utility_type:
                raise ValidationError(
                    "Meter utility type must match the tariff's utility type.")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('meter.reading')
        res = super(UtilityMeter, self).create(vals)
        return res
