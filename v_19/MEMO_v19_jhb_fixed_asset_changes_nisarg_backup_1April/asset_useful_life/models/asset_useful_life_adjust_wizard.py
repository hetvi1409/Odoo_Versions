from odoo import models, fields, api

class AdjustLifeWizard(models.TransientModel):
    _name = 'account.asset.adjust_life_wizard'
    _description = 'Wizard to adjust remaining useful life of an asset'

    asset_id = fields.Many2one('account.asset', string='Asset', required=True)
    new_remaining_life = fields.Float(string="New Remaining Useful Life", required=True)

    def confirm(self):
        """
        This method is triggered when the user confirms the adjustment of the remaining useful life.
        It calls the method on the asset record to adjust its remaining life.
        """
        # Adjust the asset's remaining useful life
        self.asset_id.adjust_remaining_useful_life(self.new_remaining_life)
        return {'type': 'ir.actions.act_window_close'}