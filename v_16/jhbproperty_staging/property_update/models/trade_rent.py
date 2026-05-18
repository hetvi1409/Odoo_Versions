from odoo import fields, models


class TradeRent(models.Model):
    """Trade Rent"""
    _name = 'trade.rent'
    _description = 'Trade Rent'

    name = fields.Char(string="Prem. No", required=True)
    bldg_code = fields.Char(string="Bldg Code", required=True)
    bldg_name = fields.Char(string="Bldg Name")
    ref = fields.Char(string="Quick Ref", required=True)
    ten_name = fields.Char(string="Ten. Name")
    lease_exp_date = fields.Date(string="Lease Exp")
    state = fields.Selection([('CURRENT', 'CURRENT'), ('EXPIRED', 'EXPIRED')], default='CURRENT')
    rentroll = fields.Date(string="Rentroll")
    opening = fields.Float(string="Opening")
    commercial = fields.Float(string="Commercial")
    total_charges = fields.Float(string="Total Charges")
    closing_balance = fields.Float(string="Closing Balance")
