from odoo import api, models, fields, _


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    def action_print_verification_history_button(self):
        records = self.env['account.asset'].browse(self.ids)
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Asset Verification Report',
            'res_model': 'assets.verification.reports',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_ids': records.ids,
                'active_model': 'account.asset',
            }
        }
        wizard = self.env['assets.verification.reports'].with_context(action['context']).create({})
        return wizard.action_export_excel()

    def action_print_latest_verification_history_button(self):
        records = self.env['account.asset'].browse(self.ids)
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Latest Asset Verification Report',
            'res_model': 'latest.assets.verification.reports',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_ids': records.ids,
                'active_model': 'account.asset',
                'latest_verification_history': True,
            }
        }
        wizard = self.env['assets.verification.reports'].with_context(action['context']).create({})
        records = self.env['account.asset'].browse(self.ids)
        for asset in records:
            last_verification = self.env['asset.verification.history'].search([('history_id', '=', asset.id)], order='create_date desc', limit=1)
            wizard.latest_verification_history_ids = [(4, last_verification.id)]
        return wizard.action_export_excel()
