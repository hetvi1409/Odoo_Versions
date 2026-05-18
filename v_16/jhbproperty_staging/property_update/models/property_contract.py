from odoo import fields, models, _
from odoo.exceptions import UserError


class PropertyContract(models.Model):
    _inherit = 'rental.contract'

    building_unit= fields.Many2one('product.template','Building Unit', required=False,domain=[('is_property', '=', True),('state', '=', 'free')])
    lease_type = fields.Selection([('portfolio_lease', 'Portfolio Lease'),
                                   ('outdoor_lease', 'Outdoor Advertisement Lease'),
                                   ('trade_lease', 'Informal Trade Lease'),], default="portfolio_lease", string='Type')
    rental_type = fields.Char(string="Rental Type")
    view_group = fields.Char(string="Viewing Group")
    creditor_region_id = fields.Many2one('creditor.region')
    bldg_code = fields.Char(string="Bldg Code")
    bldg_name = fields.Char(string="Bldg Name")
    portfolio_manager_id = fields.Many2one('res.partner',
                                        string="Portfolio Manager (Comm)")
    credit_controller_id = fields.Many2one('res.partner', string="Credit Controller (Comm)")
    unit_code = fields.Char(string="Unit Code")
    jmc_number = fields.Char('JMC Number')
    prem_no = fields.Char(string="Prem. No")
    quick_ref = fields.Char(string="Quick Ref")
    arr_status_id = fields.Many2one('arr.status', string="Arr Status")
    lease_type_id = fields.Many2one('lease.type', string="Lease Type")
    portfolio_category_id = fields.Many2one('portfolio.category',
                                            string="Portfolio Category")
    unit_type_id = fields.Many2one('property.unit.type', string="Unit Type")
    ten_name = fields.Char(string="Ten Name")
    commence_date = fields.Date(string="Commence Date")
    lease_exp_date = fields.Date(string="Lease Exp Date")
    rentroll_period = fields.Date(string="Rentroll Period")
    opening_balance = fields.Float(string="Opening Balance")
    deposits = fields.Float(string="Deposits")
    other_income = fields.Float(string="Other Income")
    closing_balance = fields.Float(string="Closing Balance")
    interest = fields.Float(string="Interest")

    # Changing the attributes
    pricing = fields.Float("Price", required=False, digits="Product Price")

    # property_id = fields.Many2one('building',)
    building = fields.Many2one('building','Building', )
    commercial_charges = fields.Float(string="Commercial Charges")
    development = fields.Float(string="Development L/T")
    expenditure = fields.Float(string="Expenditure")
    recoveries = fields.Float(string="Recoveries")
    social = fields.Float(string="Social")
    vat = fields.Float(string="VAT")
    advertising_charges = fields.Float(string="Advertising Charges")
    application_fees = fields.Float(string="Application Fees")
    land_sales = fields.Float(string="Land Sales")
    residential = fields.Float(string="Residential")
    servitudes = fields.Float(string="Servitudes")
    total_receipts = fields.Float(string="Total Receipts")
    total_charges = fields.Float(string="Total Charges")
    outdoor_advertisement_id = fields.Many2one('outdoor.advertisement', string="Outdoor Advertisement")

    def unlink(self):
        """restrict the unlink options for some particular state"""
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("You can not delete a contract not in draft state"))
        return super(PropertyContract, self).unlink()

    def action_confirm(self):
        """To set the property state into lease"""
        res = super().action_confirm()
        self.building.write({'state': 'on_lease'})
        return res

    def action_cancel(self):
        """To reset the property into available state"""
        res = super().action_cancel()
        self.building.write({'state':  'free'})
        return res
