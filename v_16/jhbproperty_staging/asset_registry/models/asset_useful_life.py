from odoo import fields, models


class AssetUsefulLife(models.Model):
    _name = 'asset.useful.life'
    _description = 'Useful life'

    date = fields.Date('Date', required=True)
    amount = fields.Float('Amount', required=False)
    asset_id = fields.Many2one('account.asset')
    original_useful_life = fields.Float(string="Original useful life")
    reserved_useful_life = fields.Float(string="Revised useful life")
    remaining_useful_life = fields.Float(string="Remaining useful life")
