from odoo import fields, models , _
from odoo.exceptions import UserError
from math import copysign

class AccountAssetModify(models.Model):
    _inherit = 'account.asset'

    custodian_department_id = fields.Many2one('hr.department',string="Custodian Department",required=False) # Make here required True, False for only import sheet purpose
    state = fields.Selection(
        selection_add=[('asset_disposed', 'Asset Disposed')],
        ondelete={'asset_disposed': 'cascade'},
    )

    def action_asset_disposal(self):
        self.state = 'asset_disposed'
        self.ensure_one()
        self.disposal_date = fields.Date.today()
        record_id = self.env['asset.removal.approvals'].search([('assets_id', '=', self.id)])
        if record_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Remove Building',
                'res_model': 'asset.removal.approvals',
                'view_mode': 'form',
                # 'view_id': self.env.ref('assets_disposal.asset_form_approval_form_custom').id,
                # 'view_type': 'form',
                'res_id': record_id.id,
                'target': 'current',  # O   pens in a new window
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Remove Building',
                'res_model': 'asset.removal.approvals',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'default_assets_id': self.id,  # Pre-fill the building in the removal approval form
                },
                'target': 'current',  # Opens in a new window
            }




    def action_approve(self):
        print("fff")
