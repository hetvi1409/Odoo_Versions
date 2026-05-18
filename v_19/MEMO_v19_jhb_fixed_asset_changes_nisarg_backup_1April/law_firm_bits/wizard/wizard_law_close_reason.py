from odoo import models, fields, _
from odoo.exceptions import AccessError, UserError


class WizardLawCloseReason(models.TransientModel):
    _name = 'wizard.law.close.reason'
    _description = 'Close Reason'

    close_reason = fields.Selection(
        selection=[('won', 'Won'), ('loss', 'Loss'), ('settled', 'Settled'), ('dropped', 'Dropped')])

    def btn_submit_close_reason(self):
        model = self.env.context('active_model', False)
        ids = self.env.context('active_ids', [])
        if not model or not ids:
            raise UserError("Something missing in context model or ids")

        self.env[model].browse(ids).write({'close_reason': self.close_reason})
