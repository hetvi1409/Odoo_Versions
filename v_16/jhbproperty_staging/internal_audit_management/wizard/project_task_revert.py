from odoo import fields, models, _


class ProjectTaskRevert(models.TransientModel):
    """Project Task revert"""
    _name = 'project.task.revert'

    task_id = fields.Many2one('project.task', string="Procedure", readonly=True)
    comments = fields.Text(string="Comments", required=True)

    def action_submit(self):
        """Action Submit"""
        task = self.task_id
        task.state = '02_changes_requested'
        self.env['audit.revert'].create({
            'res_id': task.id,
            'res_model': task._name,
            'comments': self.comments,
            'user_id': task.env.uid,
            'record_state': task.stages,
            'res_user_id': task.env.user.id,
            'reference_type': 'project_task',
        })
        if task.stages == 'first_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_procedure_to_review')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Audit Procedure %s was reverted to previous stage by %s') % (
                    task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
            task.stages = 'preparer'
        if task.stages == 'second_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_procedure_to_review')
            recipient_ids = task.user_reviewer_2_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Audit Procedure %s was reverted to previous stage by %s') % (
                    task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
            task.stages = 'preparer'
        if task.stages == 'rejected':
            task.state = '01_in_progress'
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_procedure_to_review')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Audit Procedure %s was reverted to previous stage by %s') % (
                    task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
            task.stages = 'preparer'
