from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from werkzeug import urls


class TransportRequest(models.Model):
    _name = 'transport.request'
    _description = 'Transport Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Request Reference')
    requester_id = fields.Many2one('hr.employee',string='Requester',help='Employee making the request')
    department_id = fields.Many2one('hr.department',string='Department',help="Requester’s department")
    request_date = fields.Datetime(string='Request Date',help="Date/time of request")
    pickup_location = fields.Char(string='Pickup Address/Location')
    dropoff_location = fields.Char(string='Drop Off Address/Location')
    purpose = fields.Text(string='Purpose of Transport')
    rejection_reason = fields.Text(string='Rejection Reason')
    vehicle_type = fields.Selection([('draft','Draft'),('submitted','Submitted'),('approved','Approved'),('assigned','Assigned'),('done','Done'),('rejected','Rejected')],string='Status',default='draft', copy=False)
    approver_id = fields.Many2one('hr.employee',string='Approving Manager')
    approval_date = fields.Datetime(string='Date/time of approval')
    assigned_vehicle_id = fields.Many2one('fleet.vehicle',string='Assigned Vehicle')
    assigned_driver_id = fields.Many2one('hr.employee',string='Assigned Driver')
    assignment_date = fields.Datetime(string='Date/time of assignment')
    completion_date = fields.Datetime(string='Date/time of trip completion')
    notes = fields.Html(string='Notes')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict')

    @api.model
    def create(self, vals):
        """Automatically generate a reference number for new requests."""
        vals['name'] = self.env['ir.sequence'].next_by_code(
                'transport.request')
        return super(TransportRequest, self).create(vals)

    def action_submission(self):
        if self.approver_id:
            mail_template = self.env.ref(
                'transport_request.mail_template_transport_request').with_context(
                lang=self.env.user.lang
            )
            mail_template.send_mail(self.id, force_send=True)
        else:
            raise ValidationError("Please select the approver")
        self.vehicle_type = 'submitted'
        self.request_date = fields.Datetime.now()

    def action_approval(self):
        transport_officer = self.env.ref('transport_request.group_transport_officer',
                                      raise_if_not_found=False)
        if transport_officer and transport_officer.users:
            mail_template = self.env.ref(
                'transport_request.mail_template_transport_approval').with_context(
                lang=self.env.user.lang)
            for user in transport_officer.users:
                mail_template.with_context(
                    lang=user.lang,
                    user=user,
                ).send_mail(self.id, force_send=True)
            self.vehicle_type = 'approved'
            self.approval_date = fields.Datetime.now()


    def action_assign(self):
        if not self.assigned_driver_id or not self.requester_id:
            raise ValidationError(
                "Please assign both vehicle and driver before proceeding.")
        if self.requester_id and self.requester_id.user_id:
            requester_template = self.env.ref(
                'transport_request.mail_template_notify_requester_assignment')
            requester_template.with_context(
                lang=self.env.user.lang).send_mail(self.id,force_send=True)
        if self.assigned_driver_id:
            driver_template = self.env.ref(
                'transport_request.mail_template_notify_driver_assignment')
            driver_template.with_context(
                lang=self.env.user.lang).send_mail(self.id, force_send=True)
        self.vehicle_type = 'assigned'
        self.assignment_date = fields.Datetime.now()

    def action_completion(self):
        if self.requester_id:
            requester_template = self.env.ref(
                'transport_request.mail_template_transport_completion')
            requester_template.with_context(lang=self.env.user.lang).send_mail(self.id,
                                                                  force_send=True)
        else:
            raise ValidationError("Please select the requester")
        self.vehicle_type = 'done'
        self.completion_date = fields.Datetime.now()

    def action_reject(self):
        self.ensure_one()
        return {
            'name': 'Reject Transport Request',
            'type': 'ir.actions.act_window',
            'res_model': 'transport.request.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_request_id': self.id,
            }
        }

    def get_form_request_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        return urls.url_join(
            base_url,
            f"/web#id={self.id}&model=transport.request&view_type=form"
        )


