from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    vat = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Vat")
    category_id = fields.Many2one('account.category')
    budget_type = fields.Selection([('OPEX', 'OPEX'),
                                    ('CAPEX', 'CAPEX'),
                                    ('Balance Sheet Budgeting',
                                     'Balance Sheet Budgeting')],
                                   string="Budget Type")
    item_code = fields.Char(string="Item Code")
    department_code = fields.Char(string="Cost Centre /Department Code")
    department_description = fields.Char(string="Cost Centre /Department Description")

    @api.constrains('code')
    def _check_account_code(self):
        """Rewrite this for import the chart of accounts"""
        for account in self:
            pass
