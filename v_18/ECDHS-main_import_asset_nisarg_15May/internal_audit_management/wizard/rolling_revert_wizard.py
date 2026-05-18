from odoo import fields, models, _


class RollingPlanRevert(models.TransientModel):
    """Project Task revert"""
    _name = 'rolling.revert.wizard'

    rolling_plan = fields.Char(string='Rolling Plan',readonly=True )
    rolling_plan_detail_id  = fields.Many2one('rolling.plan',string="Rolling Plan Details")
    comments = fields.Text(string="Comments", required=True)

    def action_submit_revert(self):
        """Action Submit"""
        task = self.rolling_plan_detail_id
        task.state = '02_changes_requested'
        if task.stages == 'first_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_template_rolling_plan_to_review')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {'recipient_ids': [(6, 0, partner.ids)]}
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Rollin Plan %s was reverted to previous stage by %s') % (
                task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
            task.feedback = self.comments
        if task.stages == 'second_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_template_rolling_plan_to_review')
            recipient_ids = task.user_reviewer_2_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True, email_values=email_values)
            task.message_post(body=_('The Rolling Plan %s was reverted to previous stage by %s') % (task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
        if task.stages == 'rejected':
            task.state = '01_in_progress'
            task.stages = 'preparer'
            mail_template = self.env.ref('internal_audit_management.email_template_rolling_plan_to_review')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True, email_values=email_values)
            task.message_post(body=_('The Rolling Plan %s was reverted to previous stage by %s') % (task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
        res_user_id = ""
        if task.stages == 'second_reviewer':
            res_user_id = task.preparer_id
        if task.stages == 'approved':
            res_user_id = task.reviewer_id
        self.env['audit.revert'].create({
            'res_id': task.id,
            'res_model': task._name,
            'comments': self.comments,
            'user_id': task.env.uid,
            'record_state': task.stages,
            'reference_type': 'rolling_plan',
            'res_user_id': res_user_id.id if res_user_id else None,
        })
        task.stages = 'reverted'
