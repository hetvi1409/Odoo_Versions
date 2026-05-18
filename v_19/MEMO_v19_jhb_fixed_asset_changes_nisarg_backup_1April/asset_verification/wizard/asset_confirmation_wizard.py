from odoo import models, fields
from odoo.exceptions import UserError


class AssetSubmitConfirmationWizard(models.TransientModel):
    _name = 'asset.submit.confirmation.wizard'
    _description = 'Asset Submit For Approval Confirmation'

    asset_ids = fields.Many2many('asset.verification.staging', string="Assets", required=True)
    text = fields.Text('Are you sure you want to submit this asset for approval?')

    def default_get(self, fields):
        print("DEFAULT_GET CALLLING===========>",self)
        res = super(AssetSubmitConfirmationWizard, self).default_get(fields)
        asset_ids = self.env.context.get('default_assets_ids')
        if asset_ids:
            res['asset_ids'] = asset_ids
        return res

    def action_approve(self):
        print("\n\n\n Action confirm called==>",self.asset_ids)
        # if asset is not in awaiting_approval state then give me warning first need to approvcal
        for asset in self.asset_ids:
            if asset.state != 'awaiting_approval':
                raise UserError("Asset must be in 'Awaiting Approval' state to be approved.")
            asset.sudo().action_approve()
        return {'type': 'ir.actions.act_window_close'}