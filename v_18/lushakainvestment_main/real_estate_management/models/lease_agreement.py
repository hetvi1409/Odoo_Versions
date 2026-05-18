from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class LeaseAgreement(models.Model):
    _name = "lease.agreement"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Sequence", copy=False, readonly="1")

    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")
    crm_lead_id = fields.Many2one('crm.lead', string="Enquiry")
    property_id = fields.Many2one('building', string="Property")
    building_id = fields.Many2one('product.template',
                                  domain="[('is_property','=',True), ('building_id', '=', property_id)]",
                                  string="Building Unit")
    transaction_type = fields.Selection([('retail', 'Retail')])


    section_number = fields.Char(string="Section Number")
    floor = fields.Char(string="Floor")
    internal_area = fields.Float(string="Internal Area (m2)")
    additional_area = fields.Float(string="Additional Area (m2)")
    annual_escalation = fields.Float(string="Annual Escalation")

    date_offer = fields.Date(string="Date Of Offer", default=fields.Date.today())
    offer_open_days = fields.Integer(string="Offer Open Days")
    offer_expiry_date = fields.Date(string="Offer Expiry Date", store=True,
                                    compute="_compute_offer_expiry_date")

    net_rent = fields.Float(string="Net Rent (Rates)")
    net_rent_monthly = fields.Monetary(string="Net Rent (Monthly)", compute="_compute_net_rent_monthly")
    additional_area_rate = fields.Float(string="Additional Area (Rates)")
    additional_area_monthly = fields.Monetary(string="Additional Area (Monthly)", compute="_compute_additional_area_monthly")
    marketing_fee = fields.Float(string="Marketing Fee (Rates)")
    marketing_fee_monthly = fields.Monetary(string="Marketing Fee (Monthly)", compute="_compute_marketing_fee_monthly")
    rates_tax = fields.Monetary(string="Rates & Taxes (p/m2)")
    rates_tax_monthly = fields.Monetary(string="Rates & Taxes (Monthly)", compute="_compute_rates_tax_monthly")
    operating_cost = fields.Monetary(string="Operating Cost (p/m2)" )
    operating_cost_monthly = fields.Monetary(string="Operating Cost (Monthly)", compute="_compute_operating_cost_monthly")
    gross_rent = fields.Monetary(string="Gross Rent", compute="_compute_gross_rent")
    parking = fields.Integer(string="Parking")
    parking_bays = fields.Monetary(string="Parking Bays")
    parking_bays_monthly = fields.Monetary(string="Parking Bays (Monthly)", compute="_compute_parking_bays_monthly")
    total_gross_rental = fields.Monetary(string="Total Gross Rental", compute="_compute_total_gross_rental")

    leave_period = fields.Integer(string="Leave Period (year)")

    @api.model
    def create(self, values):
        """Method for generating sequence"""
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code(
                'lease.agreement') or _('New')
        return super(LeaseAgreement, self).create(values)

    @api.depends('date_offer', 'offer_open_days')
    def _compute_offer_expiry_date(self):
        """Calculate expiry date"""
        for rec in self:
            offer_expiry_date = rec.date_offer + relativedelta(days=rec.offer_open_days)
            rec.offer_expiry_date = offer_expiry_date

    @api.depends('net_rent', 'internal_area')
    def _compute_net_rent_monthly(self):
        """Net rent monthly"""
        for rec in self:
            net_rent_monthly = 0
            net_rent_monthly = rec.net_rent * rec.internal_area
            rec.net_rent_monthly = net_rent_monthly

    @api.depends('additional_area_rate', 'additional_area')
    def _compute_additional_area_monthly(self):
        """Add value to additional area monthly"""
        for rec in self:
            rec.additional_area_monthly = rec.additional_area_rate * rec.additional_area

    @api.depends('marketing_fee', 'additional_area_monthly', 'net_rent_monthly')
    def _compute_marketing_fee_monthly(self):
        """dd value to marketing fee"""
        for rec in self:
            rec.marketing_fee_monthly = (rec.additional_area_monthly + rec.net_rent_monthly) * rec.marketing_fee

    @api.depends('rates_tax', 'internal_area')
    def _compute_rates_tax_monthly(self):
        """"""
        for rec in self:
            rec.rates_tax_monthly = rec.internal_area * rec.rates_tax

    @api.depends('internal_area', 'operating_cost')
    def _compute_operating_cost_monthly(self):
        for rec in self:
            rec.operating_cost_monthly = rec.internal_area * rec.operating_cost

    @api.depends('net_rent_monthly', 'additional_area_monthly',
                 'marketing_fee_monthly', 'rates_tax_monthly',
                 'operating_cost_monthly')
    def _compute_gross_rent(self):
        for rec in self:
            rec.gross_rent = (rec.net_rent_monthly + rec.additional_area_monthly
                              + rec.marketing_fee_monthly + rec.rates_tax_monthly
                              + rec.operating_cost_monthly)

    @api.depends('parking', 'parking_bays')
    def _compute_parking_bays_monthly(self):
        for rec in self:
            rec.parking_bays_monthly = rec.parking * rec.parking_bays

    @api.depends('parking_bays_monthly', 'gross_rent')
    def _compute_total_gross_rental(self):
        for rec in self:
            rec.total_gross_rental = rec.parking_bays_monthly + rec.gross_rent
