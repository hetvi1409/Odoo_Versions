from odoo import fields, models, _

class AccountAssets(models.Model):
    _inherit = 'account.asset'

    def action_remove_asset(self):
        """Remove Assets"""
        removal = self.env['asset.removal.approval'].search([('asset_id', '=', self.id),
                                                             ('state', 'not in', ('approved', 'rejected'))], limit=1)
        if not removal:
            return {
                'name': _('Asset Removal Approval'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'asset.removal.approval',
                'context': {
                    'default_asset_id': self.id
                },
                'target': 'new'
            }
        else:
            return {
                'name': _('Asset Removal Approval'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'asset.removal.approval',
                'res_id': removal.id,
                'target': 'new'
            }
