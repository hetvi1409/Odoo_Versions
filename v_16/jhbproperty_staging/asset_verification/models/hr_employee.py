
from odoo import _, models


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"


    def toggle_active(self):
        assets = self.env['account.asset'].search([('custodian_id','=',self.id)])
        if assets:
            return {'warning': {
                'title': _("Custodian Assets Found"),
                'message': _(
                    "Please use Transfer Asset Ownership Button to transfer assets to another custodian")}
            }
        else:
            return super(HrEmployeePrivate, self).toggle_active()

    def transfer_asset_ownership(self):
        wizard = self.env['asset.verification.confirm.wizard'].create({'custodian_id':self.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'asset.verification.confirm.wizard',
            'view_mode': 'form',
            'name': _("Transfer Asset Ownership"),
            'target': 'new',
            'res_id':wizard.id,
        }

    def check_assets(self,res_id):
        assets = self.env['account.asset'].search([('custodian_id','=',res_id)])
        if assets:
            return False
        else:
            return True
