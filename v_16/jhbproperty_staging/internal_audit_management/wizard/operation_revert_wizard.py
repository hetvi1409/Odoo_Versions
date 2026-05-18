from odoo import fields, models, _


class OperationalPlanRevert(models.TransientModel):
    """Project Task revert"""
    _name = 'operational.revert.wizard'

    operational_plan = fields.Char(string='Operational Plan',readonly=True )
    operational_plan_detail_id  = fields.Many2one('operational.plan',string="Operational Plan Details")
    comments = fields.Text(string="Comments", required=True)

    def action_submit_revert(self):
        """Action Submit"""
        # audit_findings=self.audit_findings
        task = self.operational_plan_detail_id
        if task.stages == 'second_reviewer':
            res_user_id = task.preparer_id
        if task.stages == 'approved':
            res_user_id = task.reviewer_id
        if task.stages in ['preparer', 'first_reviewer', 'second_reviewer', 'rejected']:
            self.env['audit.revert'].create({
                'res_id': self.operational_plan_detail_id.id,
                'res_model': self.operational_plan_detail_id._name,
                'comments': self.comments,
                'user_id': self.operational_plan_detail_id.env.uid,
                'record_state': self.operational_plan_detail_id.stages,
                'reference_type': 'operational_plan',
                'res_user_id': res_user_id.id if res_user_id else None,
            })
        previous_state = task.stages
        task.feedback = self.comments
        task.stages = 'reverted'
        task.operational_plan_tracking_ids.create({
            'operational_plan_tracking_id': task.id,
            'comment': "Reverted",
            'new_stage_id': task.stages,
            'previous_stage_id': previous_state,
            'user_id': self.env.user.id,
            'date': fields.Datetime.now(),
        })
        task.state = '02_changes_requested'
        if task.stages == 'first_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_template_operational_plan_to_review')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Operational Plan %s was reverted to previous stage by %s') % (
                task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
        if task.stages == 'second_reviewer':
            mail_template = self.env.ref(
                'internal_audit_management.email_template_operational_plan_to_review')
            recipient_ids = task.user_reviewer_2_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Operational Plan %s was reverted to previous stage by %s') % (
                task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
        if task.stages == 'rejected':
            task.state = '01_in_progress'
            mail_template = self.env.ref(
                'internal_audit_management.email_template_operational_plan_to_review')
            recipient_ids = task.user_reviewer_1_ids
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(task.id, force_send=True,
                                    email_values=email_values)
            task.message_post(body=_('The Operational Plan %s was reverted to previous stage by %s') % (
                task.name, self.env.user.name))
            task.message_post(body=_('Revert Comments: %s ') % (self.comments))
        res_user_id = ""
        if task.stages == 'first_reviewer':
            res_user_id = task.user_reviewer_1_ids
        if task.stages == 'second_reviewer':
            res_user_id = task.user_reviewer_2_ids
