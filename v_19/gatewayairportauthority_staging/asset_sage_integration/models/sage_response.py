from odoo import fields, models, api


class SageResponse(models.Model):
    _name = "sage.response"
    _description = "Sage Response"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "response_id"


    response_id = fields.Char(string="ID", required=True)
    autoIdx = fields.Char(string="autoIdx")
    transactionDate = fields.Datetime(string="transactionDate")
    reference = fields.Datetime(string="reference")
    description = fields.Char(string="description")
    debit = fields.Float(string="debit")
    credit = fields.Float(string="credit")
    amount = fields.Float(string="amount")
    uniqueId = fields.Char(string="uniqueId")
    accountNumber = fields.Char(string="accountNumber")
    cReference2 = fields.Char(string="cReference2")
    auditNumber = fields.Char(string="auditNumber")
    accountLink = fields.Char(string="accountLink")
    trCode = fields.Char(string="trCode")
    trCodeDescription = fields.Char(string="trCodeDescription")

    quantity = fields.Integer(string="Quantity", default=1)

    def _get_default_asset_model(self):
        account = self.env['account.account'].search([('code', '=', self.accountNumber)])
        asset = ""
        if account:
            asset = self.env['account.asset'].search([('sage_cost_account_id', '=', account.id)])
        return asset.id if asset else 1

    asset_model_id = fields.Many2one('account.asset', domain="[('state', '=', 'model')]")
    asset_ids = fields.One2many('account.asset', 'sage_id', readonly=True)

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        print(res)
        account = res.env['account.account'].search(
            [('code', '=', res.accountNumber)])
        asset = ""
        if account:
            asset = res.env['account.asset'].search(
                [('sage_cost_account_id', '=', account.id)])

        res.asset_model_id = asset.id if asset else False
        return res

    def action_create_asset(self):
        """Create Assets"""
