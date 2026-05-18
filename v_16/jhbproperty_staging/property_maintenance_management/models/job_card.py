from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError
# from geopy.geocoders import GoogleV3


class JobCard(models.Model):
    _name = 'job.card'
    _description = 'Job Card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'job_card_id'
    #
    job_card_id = fields.Char(string='Job Card')
    helpdesk_job_card_id = fields.Many2one('helpdesk.ticket')
    #
    name = fields.Char(string='Name')
    ticket_ref = fields.Char(string='Ticket Reference')
    #Property Details
    property_name = fields.Char(string='Property Name')
    jmc_number = fields.Char(string='JMC Number')
    location = fields.Char(string='Location')
    # Customer Details
    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_street = fields.Char(string='Street')
    partner_street2 = fields.Char(string='Street2')
    partner_city = fields.Char(string='City')
    partner_state_id = fields.Many2one("res.country.state", string='State',
                                        ondelete='restrict')
    partner_country_id = fields.Many2one('res.country', string='Country',
                                          ondelete='restrict')
    partner_zip = fields.Char(string="Zip", help="Zip code for the customer" )
    partner_phone = fields.Char(string='Phone')
    partner_mobile = fields.Char(string='Mobile')
    partner_email = fields.Char(string='Email')
    # latitude = fields.Float("Latitude", digits=(9, 6), required=True)
    # longitude = fields.Float("Longitude", digits=(9, 6), required=True)

    # @api.onchange('address')
    # def _onchange_address(self):
    #     if self.address:
    #         geolocator = GoogleV3(api_key='YOUR_GOOGLE_MAPS_API_KEY')
    #         location = geolocator.geocode(self.address)
    #
    #         if location:
    #             self.latitude = location.latitude
    #             self.longitude = location.longitude

    #Appointment Order
    appointment_date = fields.Date(string='Appointment Date')
    technician = fields.Many2one('res.users',string='Technician')
    requests = fields.Text()
    is_inventory_required = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Is Inventory Required')
    job_description = fields.Text(string='Job Description')
    required_inventory_ids = fields.One2many('inventory.required', "required_inventory_job", string="Required Inventory Items")

    state = fields.Selection([('draft', 'Draft'), ('waiting_approval', 'Waiting for the Approval'),
                              ('approve', 'Approved'),
                              ('declined', 'Declined')], default='draft')
    is_decline = fields.Boolean(string="Is Decline")
    decline_reason = fields.Text(string='Reason For decline')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            partner = self.partner_id
            self.partner_street = partner.street
            self.partner_street2 = partner.street2
            self.partner_city = partner.city
            self.partner_state_id = partner.state_id
            self.partner_country_id = partner.country_id
            self.partner_zip = partner.zip
            self.partner_phone = partner.phone
            self.partner_mobile = partner.mobile
            self.partner_email = partner.email

    def action_location_navigate(self):
        return self.partner_id.action_partner_navigate()

    def name_get(self):
        result = []
        for ticket in self:
            result.append((ticket.id, f"{ticket.name} (#{ticket.ticket_ref})"))
        return result


    def action_inventory_approval_request(self):

        if not self.is_inventory_required:
            raise UserError(_('Please select is inventory required or not'))
            # Check if there are any required_inventory_ids
        if self.is_inventory_required == 'yes':
            if not self.required_inventory_ids:
                raise ValidationError(
                    "No products have been added. Please add products and Quantities.")

        self.write({'state': 'waiting_approval'})

    def action_approve_inventory(self):
        self.write({'state': 'approve'})
        self.helpdesk_job_card_id.is_card_approved = True
        self.helpdesk_job_card_id.is_card_decline = False


    def action_decline_inventory(self):
        # self.is_decline = True
        # decline = self.env['enquiry.assessment'].create({
        #     'enquiry_id': self.id,
        #     'partner_id': self.partner_id.id,
        #     'jmc_number': self.asset_number,
        #     'stand_number': self.stand_number,
        #     'property_id': self.property_id.id,
        #     'user_domain_ids': asset.ids
        # })
        # self.assessment_id = assessment.id
        # self.state = 'assessment'
        #
        # mail_template = self.env.ref(
        #     'client_enquiry.email_template_enquiry_assessment_created')
        # recipient_ids = self.env.ref(
        #     'client_enquiry.group_asset_evaluator').users
        # partner = recipient_ids.mapped('partner_id')
        # email_values = {
        #     'recipient_ids': [(6, 0, partner.ids)]
        # }
        # mail_template.send_mail(self.id, force_send=True,
        #                         email_values=email_values)
        action = {
            'name': _('Reason For Decline'),
            'type': 'ir.actions.act_window',
            'res_model': 'job.card.decline',
            'context': {
                'default_decline_id': self.id
            },
            'target': 'new',
            'view_mode': 'form',
        }
        return action

    def action_resubmit_approval_request(self):
        self.write({'state': 'waiting_approval'})


        # self.is_decline = True  # Set is_decline to True
        # if not self.is_decline:
        #     self.is_decline = True
        # if not self.decline_reason:
        #     raise ValidationError("Please mention the decline reason")
        # else:
        #     # Your additional logic when is_decline is True and decline_reason is provided
        #     pass