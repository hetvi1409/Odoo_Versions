# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AppRejectionWizard(models.TransientModel):
    _name = 'app.rejection.wizard'
    _description = 'APP Rejection Wizard'

    app_id = fields.Many2one('annual.procurement.plan', string='APP', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True)

    def action_confirm_rejection(self):
        """Confirm rejection and send notification to initiator"""
        self.ensure_one()

        if not self.rejection_reason or not self.rejection_reason.strip():
            raise ValidationError(_("Rejection reason is mandatory and cannot be empty."))

        app = self.app_id

        # Append rejection reason to approver comment
        if app.approve_comment:
            app.approve_comment = f"{app.approve_comment}\n\n--- Rejection Reason ---\n{self.rejection_reason}"
        else:
            app.approve_comment = self.rejection_reason

        # Change state to rejected
        app.state = 'rejected'

        # Send rejection email to initiator
        template = self.env.ref('sa_government_tender.mail_template_app_rejection', raise_if_not_found=False)
        if template:
            action = self.env['ir.actions.act_window']._for_xml_id('sa_government_tender.action_annual_procurement_plan')
            base_url = app.get_base_url()
            url = f"{base_url}/odoo/{action.get('path')}/{app.id}"

            # Send email to initiator
            if app.initiator_id and app.initiator_id.partner_id.email:
                template.with_context(
                    initiator_name=app.initiator_id.name,
                    app_name=app.name,
                    rejection_reason=self.rejection_reason,
                    app_url=url
                ).send_mail(
                    app.id,
                    force_send=True,
                    email_values={
                        'email_to': app.initiator_id.partner_id.email,
                        'subject': f'APP {app.name} has been Rejected'
                    }
                )

        return {'type': 'ir.actions.act_window_close'}
