from odoo import fields, models, _


class ProjectTaskRevert(models.TransientModel):
    """Project Task revert"""
    _name = 'audit.universe.revert.wizard'

    # audit_findings = fields.Html(string='Audit Findings',readonly=True )
    period = fields.Char(string="Period")
    audit_details_id  = fields.Many2one('audit.universe',string="Audit Details")
    comments = fields.Text(string="Comments", required=True)

    def action_submit_revert(self):
        self.env['audit.universe.tracking'].create({
            'audit_universe_revert_id': self.audit_details_id.id,
            'period': self.period,  # Replace with actual fields in audit.task
            'comments': self.comments,  # Map to appropriate fields  # Example: Link to the source record
            'stage': "Reverted",  # Map to appropriate fields  # Example: Link to the source record
        })
        """Action Submit"""
        # audit_findings = self.audit_findings
        task = self.audit_details_id
        task.state = '02_changes_requested'
        if task.stages == 'first_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_universe_to_revert')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Audit Universe %s was reverted to previous stage by %s') % (
                task.period, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
        if task.stages == 'second_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_universe_to_revert')
            recipient_ids = task.user_reviewer_2_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Audit Universe %s was reverted to previous stage by %s') % (
                task.period, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
        if task.stages == 'rejected':
            task.state = '01_in_progress'
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_universe_to_revert')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Audit Universe %s was reverted to previous stage by %s') % (
                task.period, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
            task.stages = 'preparer'
        res_user_id = ""
        if task.stages == 'first_reviewer':
            res_user_id = task.user_reviewer_1_ids
        if task.stages == 'second_reviewer':
            res_user_id = task.user_reviewer_2_ids
        if task.stages in ['first_reviewer', 'second_reviewer']:
            self.env['audit.revert'].create({
                'res_id': task.id,
                'res_model': task._name,
                'comments': self.comments,
                'user_id': task.env.uid,
                'record_state': task.stages,
                'reference_type': 'audit_universe',
                'res_user_id': res_user_id.id if res_user_id else None,
            })
            task.stages = 'reverted'
            task.feedback = self.comments
