from odoo import models, fields, api

class TransportRequestRejectWizard(models.TransientModel):
    _name = 'transport.request.reject.wizard'
    _description = 'Wizard to Reject Transport Request'

    reason = fields.Text(string="Rejection Reason", required=True)
    request_id = fields.Many2one('transport.request', string="Request")

    def action_reject(self):
        self.ensure_one()
        if self.request_id:
            self.request_id.write({
                'vehicle_type': 'rejected',
                'rejection_reason': self.reason,
            })
            if self.request_id.requester_id:
                requester_template = self.env.ref(
                    'transport_request.mail_template_transport_rejection')
                requester_template.with_context(
                    lang=self.env.user.lang).send_mail(self.request_id.id,
                                                       force_send=True)
            else:
                raise ValidationError("Please select the requester")
