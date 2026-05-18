from odoo import fields, models, _


class AuditStrategyRevert(models.TransientModel):
    """Audit Strategy revert"""
    _name = 'audit.strategy.wizard'

    audit_strategy_id  = fields.Many2one('audit.strategy',string="Audit Strategy")
    comments = fields.Text(string="Comments", required=True)

    def action_submit_revert(self):
        """Action Submit"""
        task = self.audit_strategy_id
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_strategy_reviewed')
        recipient_ids = task.user_reviewer_1_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        task.message_post(body=_(
            'The Rollin Plan %s was reverted to previous stage by %s') % (
                               task.name, self.env.user.name))
        task.message_post(body=_('Revert Comments: %s ') % (self.comments))
