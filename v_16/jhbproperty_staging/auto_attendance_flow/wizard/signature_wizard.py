from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TimesheetSignatureWizard(models.TransientModel):
    _name = 'timesheet.signature.wizard'
    _description = 'Signature Wizard'

    timesheet_generator_id = fields.Many2one('hr.timesheet.generator', string="Timesheet", required=True)
    field = fields.Char("Field")
    mode = fields.Selection([('approver', 'Approver')], default='approver')
    user_id = fields.Many2one('res.users', string="User")
    use_existing = fields.Boolean("Use existing profile signature", default=False)
    signature = fields.Binary("New Signature")

    def action_confirm(self):
        user_signature = self.user_id.sudo().sign_signature
        sig_to_use = user_signature if self.use_existing and user_signature else self.signature
        if not self.user_id.sudo().sign_signature and self.use_existing:
            self.use_existing = False
            raise ValidationError("Please add signature under user profile OR add new signature.")
        if self.mode == 'approver':
            if self.field:
                setattr(self.timesheet_generator_id, self.field, sig_to_use)
                if self.field == 'signature':
                    self.timesheet_generator_id.signature_date = fields.Datetime.now()
                    self.timesheet_generator_id.state = 'approved'
                    self.timesheet_generator_id.sudo().attendance_ids.write({'timesheet_status':'approved'})
        if not self.user_id.sudo().sign_signature and self.signature:
            self.user_id.sudo().sign_signature = self.signature
        return {'type': 'ir.actions.act_window_close'}
