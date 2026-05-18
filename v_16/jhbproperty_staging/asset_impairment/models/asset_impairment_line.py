from odoo import models, fields


class AssetImpairmentMove(models.Model):
    _name = 'asset.impairment.move'
    _description = 'Asset Impairment Move'

    asset_id = fields.Many2one('account.asset', string='Asset', required=True)
    impairment_date = fields.Date(string='Impairment Date', required=True)
    impairment_value = fields.Monetary(string='Impairment Loss', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', related='asset_id.currency_id')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft')
    reference = fields.Char()
    cumulative_impairment_value = fields.Monetary(string='Cumulative Impairment Loss', currency_field='currency_id')
    current_value = fields.Monetary(string='Current Value', currency_field='currency_id')
    # Add any other fields as necessary
