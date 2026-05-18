from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MemoSignatureWizard(models.TransientModel):
    _name = 'memo.signature.wizard'
    _description = 'Signature Wizard'

    memo_id = fields.Many2one('memo.memo', required=True)
    field = fields.Char("Field")
    mode = fields.Selection([('memo', 'Memo'), ('approver', 'Approver'),('quality_assurance','Quality Assurance')], default='memo')
    user_id = fields.Many2one('res.users', string="User")
    use_existing = fields.Boolean("Use existing profile signature", default=False)
    signature = fields.Binary("New Signature")

    def action_confirm(self):
        user_signature = self.user_id.sign_signature
        sig_to_use = user_signature if self.use_existing and user_signature else self.signature
        if not self.user_id.sign_signature and self.use_existing:
            self.use_existing = False
            raise ValidationError("Please add signature under user profile OR add new signature.")
        if self.mode == 'memo':
            if self.field:
                setattr(self.memo_id, self.field, sig_to_use)
                if self.field == 'approver_sign':
                    self.memo_id.approve_date = fields.Datetime.now()
                if self.field == 'acknowledged_sign':
                    self.memo_id.acknowledged_date = fields.Datetime.now()
        elif self.mode == 'approver':
            line = self.env['memo.approver'].search([
                ('memo_request_id', '=', self.memo_id.id),
                ('user_id', '=', self.user_id.id)
            ], limit=1)
            if line:
                line.sign_initials = sig_to_use
        elif self.mode == 'quality_assurance':
            line = self.env['memo.quality.assurance'].search([
                ('memo_request_id', '=', self.memo_id.id),
                ('user_id', '=', self.user_id.id)
            ], limit=1)
            if line:
                line.sign_initials = sig_to_use
        if not self.user_id.sign_signature and self.signature:
            self.user_id.sign_signature = self.signature
        return {'type': 'ir.actions.act_window_close'}