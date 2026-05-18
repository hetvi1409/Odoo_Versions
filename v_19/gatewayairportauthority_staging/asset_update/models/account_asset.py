from odoo import api, fields, models, _


class AccountAsset(models.Model):
    """ account.asset model has been inherited for add some fields """
    _inherit = 'account.asset'

    account_depreciation_id = fields.Many2one(
        comodel_name='account.account',
        string='Depreciationss Account',
        check_company=True,
        # default=7,  # this will cause the error because it used here static value
        domain="[('account_type', 'not in', ('asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card', 'off_balance'))]",
        help="Account used in the depreciation entries, to decrease the asset value."
    )
    account_depreciation_expense_id = fields.Many2one(
        comodel_name='account.account',
        string='Expense Account',
        check_company=True,
        # default=8,  # this will cause the error because it used here static value
        domain="[('account_type', 'not in', ('asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card', 'off_balance'))]",
        help="Account used in the periodical entries, to record a part of the asset as expense.",
    )

    def action_custom_validate(self):
        self.state = 'open'

    def action_custom_draft(self):
        self.state = 'draft'

    def action_custom_cancel(self):
        self.state = 'cancelled'
