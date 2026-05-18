from odoo import fields, models, api
from odoo.exceptions import UserError


class TenantMixCriteria(models.TransientModel):
    _name = "tenant.mix.criteria"
    _description = "Tenant Mix Criteria Wizard"

    enquiry_id = fields.Many2one('property.enquiry', string="Enquiry", required=True)
    comments = fields.Text(string="Comments", required=True)
    type = fields.Selection([
        ('approve', 'Approve'),
        ('decline', 'Decline')
    ], string="Action", required=True)

    def action_submit(self):
        """Handle submit action."""
        self.ensure_one()
        enquiry = self.enquiry_id

        if self.type == 'approve':
            enquiry.state = 'proceed'
        elif self.type == 'decline':
            enquiry.state = 'declined'
        enquiry.comments = self.comments

        enquiry.message_post(
            body=f"Tenant Mix Criteria: {self.type.title()} Comments: {self.comments}"
        )
        template = self.env.ref(
            'property_management_system.mail_template_enquiry_declined',
            raise_if_not_found=False)
        if template:
            template.send_mail(enquiry.id, force_send=True)

        return {'type': 'ir.actions.act_window_close'}


class FacilityComments(models.TransientModel):
    _name = "facility.comments"
    _description = "Facility Comments Wizard"

    enquiry_id = fields.Many2one('property.enquiry', string="Enquiry", required=True)
    comments = fields.Text(string="Comments", required=True)
    type = fields.Selection([
        ('approve', 'Approve'),
        ('decline', 'Decline')
    ], string="Suitable for Nature of Business ", required=True)

    def action_submit(self):
        """Handle submit action."""
        self.ensure_one()
        enquiry = self.enquiry_id

        if self.type == 'approve':
            enquiry.state = 'confirm_suitability'
        elif self.type == 'decline':
            enquiry.state = 'declined'
        enquiry.facility_comments = self.comments

        enquiry.message_post(
            body=f"Suitable for Nature of Business: {self.type.title()} Comments: {self.comments}"
        )
        template = self.env.ref(
            'property_management_system.mail_template_enquiry_declined',
            raise_if_not_found=False)
        if template:
            template.send_mail(enquiry.id, force_send=True)

        return {'type': 'ir.actions.act_window_close'}
