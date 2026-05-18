from odoo import models, fields, _
from odoo.exceptions import ValidationError, AccessError


class RecruitmentRequisitionSignatureWizard(models.TransientModel):
    _name = 'recruitment.requisition.signature.wizard'
    _description = 'Recruitment Requisition Signature Wizard'

    requisition_id = fields.Many2one('recruitment.requisition', required=True)
    line_model = fields.Selection([
        ('recruitment.requisition.line.manager', 'Line Manager'),
        ('recruitment.requisition.general.manager', 'General Manager'),
        ('recruitment.requisition.cfo', 'CFO'),
        ('recruitment.requisition.hcm', 'HCM'),
    ], required=True)
    line_id = fields.Integer(required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    use_existing = fields.Boolean('Use existing profile signature', default=False)
    signature = fields.Binary('New Signature')

    def action_confirm(self):
        self.ensure_one()
        line = self.env[self.line_model].browse(self.line_id).exists()
        if not line:
            raise ValidationError(_('Approval line not found.'))
        if line.requisition_id.id != self.requisition_id.id:
            raise ValidationError(_('Approval line does not belong to this requisition.'))
        if self.user_id.id != self.env.user.id or line.user_id.id != self.env.user.id:
            raise AccessError(_('You cannot sign on behalf of another user.'))

        sign_field_exists = 'sign_signature' in self.env['res.users']._fields
        user_signature = self.user_id.sign_signature if sign_field_exists else False
        signature_to_use = user_signature if self.use_existing and user_signature else self.signature
        if self.use_existing and not user_signature:
            raise ValidationError(_('Please add signature in user profile or provide a new signature.'))
        if not signature_to_use:
            raise ValidationError(_('Please provide a signature.'))

        line.write({'sign_initials': signature_to_use})

        if sign_field_exists and not self.user_id.sign_signature and self.signature:
            self.user_id.sign_signature = self.signature

        return {'type': 'ir.actions.act_window_close'}
