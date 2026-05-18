# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountReportBudgetItem(models.Model):
    _inherit = 'account.report.budget.item'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        help='Product linked to this budget item'
    )