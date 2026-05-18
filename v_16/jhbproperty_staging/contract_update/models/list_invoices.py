from odoo import models, fields, api, _
from datetime import datetime


class ListInvoices(models.Model):
    _name = 'list.invoices'

    invoice_date = fields.Datetime(string='Invoice Date')
    invoice_number = fields.Char(string='Invoice Number')
    invoice_amount = fields.Float(string='Invoice Amount')
    due = fields.Float(string='Due')
    invoice_list = fields.Many2one('xf.partner.contract', string="list Invoices")
