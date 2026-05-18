from odoo import models, fields, api
from odoo.exceptions import ValidationError


class APPSignatureWizard(models.TransientModel):
    _name = 'app.signature.wizard'
    _description = 'Signature Wizard'

    app_id = fields.Many2one('annual.procurement.plan', required=True)
    field = fields.Char("Field")
    mode = fields.Selection([('review', 'Review'), ('approver', 'Approver')], default='review')
    user_id = fields.Many2one('res.users', string="User")
    use_existing = fields.Boolean("Use existing profile signature", default=False)
    signature = fields.Binary("New Signature")

    def action_confirm(self):
        user_signature = self.user_id.sign_signature
        sig_to_use = user_signature if self.use_existing and user_signature else self.signature
        if not self.user_id.sign_signature and self.use_existing:
            self.use_existing = False
            raise ValidationError("Please add signature under user profile OR add new signature.")
        if self.mode == 'approver':
            if self.field:
                setattr(self.app_id, self.field, sig_to_use)
                if self.field == 'approver_sign':
                    self.app_id.approve_date = fields.Datetime.now()
        elif self.mode == 'review':
            line = self.env['app.reviewer'].search([
                ('app_id', '=', self.app_id.id),
                ('user_id', '=', self.user_id.id)
            ], limit=1)
            if line:
                line.sign_initials = sig_to_use
        if not self.user_id.sign_signature and self.signature:
            self.user_id.sign_signature = self.signature
        return {'type': 'ir.actions.act_window_close'}