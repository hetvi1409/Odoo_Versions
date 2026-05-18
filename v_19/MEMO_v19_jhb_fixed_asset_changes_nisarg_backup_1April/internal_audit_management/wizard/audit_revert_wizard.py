from odoo import fields, models, _


class ProjectTaskRevert(models.TransientModel):
    """Project Task revert"""
    _name = 'audit.revert.wizard'

    audit_findings = fields.Html(string='Audit Findings',readonly=True )
    audit_details  = fields.Many2one('audit.finding',string="Audit Details")
    comments = fields.Text(string="Comments", required=True)

    def action_submit_revert(self):
        record = self.audit_details
        res_user_id = ''
        if record.stages == 'first_reviewer':
            res_user_id = record.user_reviewer_1_ids
        if record.stages == 'second_reviewer':
            res_user_id = record.user_reviewer_2_ids
        if record.stages in ['first_reviewer', 'second_reviewer']:
            self.env['audit.revert'].create({
                'res_id': record.id,
                'res_model': record._name,
                'comments': self.comments,
                'user_id': record.env.uid,
                'record_state': record.stages,
                'reference_type': 'audit_finding',
                'res_user_id': res_user_id.id if res_user_id else None,
            })
        previous_state = record.stages
        record.feedback = self.comments
        record.stages = 'reverted'
        self.env['audit.finding.tracking'].create({
            'audit_finding_tracking_id': record.id,
            'user_id': self.env.user.id,
            'previous_stage_id': previous_state,
            'new_stage_id': 'reverted',
            'comment': 'Reverted',
            'date': fields.Datetime.now(),
        })

        """Action Submit"""
        # audit_findings=self.audit_findings
        task = self.audit_details
        task.state = '02_changes_requested'
        if task.stages == 'first_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_findings_to_revert')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Audit Findings %s was reverted to previous stage by %s') % (
                task.audit_finding, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
            task.stages = 'preparer'
        if task.stages == 'second_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_findings_to_revert')
            recipient_ids = task.user_reviewer_2_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Audit Findings %s was reverted to previous stage by %s') % (
                task.audit_finding, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
            task.stages = 'first_reviewer'
        if task.stages == 'rejected':
            task.state = '01_in_progress'
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_findings_to_revert')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Audit Findings %s was reverted to previous stage by %s') % (
                task.audit_finding, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
            task.stages = 'preparer'
