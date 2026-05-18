from odoo import fields, models


class AccountCategory(models.Model):
    _name = 'account.category'
    _description = 'Account Category'

    name = fields.Char(string='Category Name', required=True)
