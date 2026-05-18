from odoo import fields, models, _


class ProjectTaskRevert(models.TransientModel):
    """Project Task revert"""
    _name = 'project.task.revert'

    task_id = fields.Many2one('project.task', string="Procedure", readonly=True)
    comments = fields.Text(string="Comments", required=True)

    def action_submit(self):

        # self.env['audit.revert'].create({
        #     # 'task_id': self.task_id,  # Replace with actual fields in audit.task
        #     'comments': self.comments,  # Map to appropriate fields  # Example: Link to the source record
        # })

        """Action Submit"""
        task = self.task_id
        task.state = '02_changes_requested'
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
            task.stages = 'first_reviewer'
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
