from odoo import models, fields

class AssetSubmitApprovalWizard(models.TransientModel):
    _name = 'asset.submit.approval.wizard'
    _description = 'Asset Submit For Approval Confirmation'

    asset_ids = fields.Many2many('asset.verification.staging', string="Assets", required=True)
    text = fields.Text('Are you sure you want to submit this asset for approval?')

    def default_get(self, fields):
        res = super(AssetSubmitApprovalWizard, self).default_get(fields)
        asset_ids = self.env.context.get('default_assets_ids')
        if asset_ids:
            res['asset_ids'] = asset_ids
        return res

    def action_confirm(self):
        print("\n\n\n Action confirm called==>",self.asset_ids)
        for asset in self.asset_ids:
            asset.sudo().action_submit_for_approval()
        return {'type': 'ir.actions.act_window_close'}