from odoo import fields, models, _


class ProjectTaskRevert(models.TransientModel):
    """Project Task revert"""
    _name = 'internal.audit.charter.wizard'

    # audit_findings = fields.Html(string='Audit Findings',readonly=True )
    name = fields.Char(string="Name",readonly=True)
    audit_details_id  = fields.Many2one('internal.audit.charter',string="Audit Details")
    comments = fields.Text(string="Comments", required=True)

    def action_submit_revert(self):
        """Action Submit"""
        # audit_findings=self.audit_findings
        task = self.audit_details_id
        task.state = '02_changes_requested'
        if task.stages == 'first_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_audit_charter_to_revert')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Internal Audit Charter %s was reverted to previous stage by %s') % (
                task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
        if task.stages == 'second_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_audit_charter_to_revert')
            recipient_ids = task.user_reviewer_2_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Internal Audit Charter%s was reverted to previous stage by %s') % (
                task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
        if task.stages == 'rejected':
            task.state = '01_in_progress'
            mail_template = self.env.ref(
                'internal_audit_management.email_audit_charter_to_revert')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Internal Audit Charter %s was reverted to previous stage by %s') % (
                task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
            task.stages = 'preparer'
        if task.stages in ['first_reviewer', 'second_reviewer']:
            previous_state = self.audit_details_id.stages
            self.audit_details_id.previous_state = previous_state
            res_user_id = ""
            if self.audit_details_id.stages == 'first_reviewer':
                res_user_id = self.audit_details_id.user_reviewer_1_ids
            if self.audit_details_id.stages == 'second_reviewer':
                res_user_id = self.audit_details_id.user_reviewer_2_ids
            self.env['audit.revert'].create({
                'res_id': self.audit_details_id.id,
                'res_model': self.audit_details_id._name,
                'comments': self.comments,
                'user_id': self.audit_details_id.env.uid,
                'record_state': self.audit_details_id.stages,
                'reference_type': 'internal_audit_charter',
                'res_user_id': res_user_id.id if res_user_id else None,
            })
            self.audit_details_id.stages = 'reverted'
            self.audit_details_id.feedback = self.comments