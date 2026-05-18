from odoo import fields, models

class AssetImpairment(models.TransientModel):
    _inherit = 'asset.impairment'

    def action_asset_impairment(self):
        res = super(AssetImpairment, self).action_asset_impairment()
        print('dsdadad',res,self.asset_id)
        for asset in self.asset_ids:
            if asset.state == 'impaired':
                asset.impairment_date = fields.Date.context_today(self)
                asset.action_notify_impairment()
                asset.compute_impairment_board()
        return res