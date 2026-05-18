from odoo import fields, models, _


class RiskRevertWizaed(models.TransientModel):
    """Project Task revert"""
    _name = 'risk.revert.wizard'

    oi_risk_management_risk = fields.Html(string='Risk', readonly=True)
    oi_risk_register_risk = fields.Html(string='Risk Register', readonly=True)
    oi_risk_management_activity = fields.Html(string='Activity', readonly=True)
    risk_details = fields.Many2one('oi_risk_management.risk', string="Risk Details")
    risk_register_details = fields.Many2one('risk.register', string="Risk Register Details")
    activity_details = fields.Many2one('oi_risk_management.activity', string="Risk Details")
    comments = fields.Text(string="Comments", required=True)
    risk_type = fields.Selection(
        [('risk', 'Risk'), ('assessment', 'Assessment'), ('treatment', 'Treatment'), ('activity', 'Activity'),('register','Register')],
        string="Risk Type")

    def action_submit_revert(self):
        record = ''
        if self.risk_details:
            record = self.risk_details
        if self.activity_details:
            record = self.activity_details
        if self.risk_register_details:
            record = self.risk_register_details
        if record:
            res_user_id = ''
            state = ''
            reference_type = 'oi_risk_management_risk'
            if self.risk_type and self.risk_type == 'risk':
                state = record.risk_state
            if self.risk_type and self.risk_type == 'assessment':
                state = record.risk_assessment_state
            if self.risk_type and self.risk_type == 'treatment':
                state = record.risk_treatment_state
            if self.risk_type and self.risk_type == 'activity':
                state = record.factor_state
                reference_type = 'oi_risk_management_activity'
            if self.risk_type and self.risk_type == 'register':
                state = record.risk_register_state
                reference_type = 'oi_risk_management_register'

            if record and state:
                if state == 'prepared':
                    res_user_id = record.preparer_id
                if state == 'rejected':
                    res_user_id = record.preparer_id
                if state == 'reviewed':
                    res_user_id = record.reviewer_id
                if state in ['prepared', 'reviewed', 'rejected']:
                    self.env['audit.revert'].create({
                        'res_id': record.id,
                        'res_model': record._name,
                        'comments': self.comments,
                        'user_id': record.env.uid,
                        'record_state': state,
                        'reference_type': reference_type,
                        'reference': record._name,
                        'res_user_id': res_user_id.id if res_user_id else None,
                        'risk_type': self.risk_type,
                    })
                previous_state = state
                record.feedback = self.comments
                state = 'reverted'

                """Action Submit"""
                if state == 'prepared':
                    mail_template = self.env.ref(
                        'governance_update.email_template_oi_risk_management_risk_to_revert')
                    recipient_ids = record.complaince_preparer_id
                    partner = recipient_ids.mapped('partner_id')
                    email_values = {
                        'recipient_ids': [(6, 0, partner.ids)]
                    }
                    mail_template.send_mail(record.id, force_send=True,
                                            email_values=email_values)
                    record.message_post(body=_('The Audit Findings %s was reverted to previous stage by %s') % (
                        record.name, self.env.user.name))
                    record.message_post(body=_('Revert Comments: %s ') % (self.comments))
                    state = 'draft'
                if state == 'reviewed':
                    mail_template = self.env.ref(
                        'governance_update.email_template_oi_risk_management_risk_to_revert')
                    recipient_ids = record.complaince_reviewer_id
                    partner = recipient_ids.mapped('partner_id')
                    email_values = {
                        'recipient_ids': [(6, 0, partner.ids)]
                    }
                    mail_template.send_mail(record.id, force_send=True,
                                            email_values=email_values)
                    record.message_post(body=_('The Audit Findings %s was reverted to previous stage by %s') % (
                        record.name, self.env.user.name))
                    record.message_post(body=_('Revert Comments: %s ') % (self.comments))
                    state = 'prepared'
                if state == 'rejected':
                    mail_template = self.env.ref(
                        'governance_update.email_template_oi_risk_management_risk_to_revert')
                    recipient_ids = record.complaince_preparer_id
                    partner = recipient_ids.mapped('partner_id')
                    email_values = {
                        'recipient_ids': [(6, 0, partner.ids)]
                    }
                    mail_template.send_mail(record.id, force_send=True,
                                            email_values=email_values)
                    record.message_post(body=_('The Audit Findings %s was reverted to previous stage by %s') % (
                        record.name, self.env.user.name))
                    record.memessage_postssage_post(body=_('Revert Comments: %s ') % (self.comments))
                    state = 'prepared'
