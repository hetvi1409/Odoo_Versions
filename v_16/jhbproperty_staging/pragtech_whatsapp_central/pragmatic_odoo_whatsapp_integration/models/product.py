from odoo import fields, models, api

class ProductTemps(models.Model):
    _inherit = 'product.template'

    def compute_currency_symbol(self):
        for rec in self:
            rec.currency_symbol = rec.currency_id.symbol

    currency_symbol = fields.Char(string="symbol", compute="compute_currency_symbol")

class PurchaseCurrency(models.Model):
    _inherit = 'purchase.order'

    def compute_currency_symbol(self):
        for rec in self:
            rec.currency_symbol = rec.currency_id.symbol

    currency_symbol = fields.Char(string="symbol", compute="compute_currency_symbol")

class SaleCurrency(models.Model):
    _inherit = 'sale.order'

    def compute_currency_symbol(self):
        for rec in self:
            rec.currency_symbol = rec.currency_id.symbol

    currency_symbol = fields.Char(string="symbol", compute="compute_currency_symbol")

class InvoicingCurrency(models.Model):
    _inherit = 'account.move'

    def compute_currency_symbol(self):
        for rec in self:
            rec.currency_symbol = rec.currency_id.symbol

    currency_symbol = fields.Char(string="symbol", compute="compute_currency_symbol")