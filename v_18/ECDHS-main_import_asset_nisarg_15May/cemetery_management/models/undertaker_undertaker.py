from odoo import api, models, fields


class Undertaker(models.Model):
    _name = 'undertaker.undertaker'
    _description = 'Undertaker'
    _rec_name = 'full_name'

    def _get_country_id(self):
        """Returns Country"""
        return self.env.ref('base.za').id

    def _get_province_data(self):
        """Returns province data"""
        return self.env.ref(
            'cemetery_management.province_province_kwaZulu_natal').id

    def _get_municipality(self):
        """Returns municipality data"""
        municipality = self.env['municipality.municipality'].search(
            [('company_id', '=', self.env.company.id)], limit=1)
        return municipality.id

    full_name = fields.Char(string='Full Name', required=True)
    surname = fields.Char(string='Surname', required=False)
    forename = fields.Char(string='Forename', required=False)
    id_number = fields.Char(string='ID Number', required=False, size=13)

    photo = fields.Binary(string='Photo')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', required=False)
    date_of_birth = fields.Date(string='Date of Birth', required=False)
    nationality = fields.Char(string='Nationality')
    phone_number = fields.Char(string='Phone Number')
    email_address = fields.Char(string='Email Address')
    # address = fields.Text(string='Address')
    undertaker_street = fields.Char(string="Street",
                                    help="Name of the street")
    undertaker_street2 = fields.Char(string="Street 2",
                                     help="Name of the street")
    undertaker_zip = fields.Char(string="Postal Code", help="Postal Code")
    undertaker_city = fields.Char(string="City", help="Name of the city")
    undertaker_country_id = fields.Many2one('res.country', string='Country',
                                            default=_get_country_id,
                                            ondelete='restrict',
                                            help="Name of the country")
    undertaker_province_id = fields.Many2one('province.province',
                                             string="Province",
                                             required=False,
                                             default=_get_province_data)
    undertaker_municipality_id = fields.Many2one('municipality.municipality',
                                                 string="Municipality",
                                                 default=_get_municipality)

    emergency_contact_name = fields.Char(string='Emergency Contact Name')
    emergency_contact_phone = fields.Char(string='Emergency Contact Phone')
    emergency_contact_relationship = fields.Char(
        string='Emergency Contact Relationship')
    user_id = fields.Many2one('res.users', string='Related User', required=True,
                              domain="[('id', 'in', portal_user_ids)]")
    portal_user_ids = fields.Many2many('res.users',
                                       compute='_compute_portal_user_ids',
                                       store=False)

    @api.depends('user_id')
    def _compute_portal_user_ids(self):
        portal_group = self.env.ref('base.group_portal')
        self.portal_user_ids = self.env['res.users'].search(
            [('groups_id', 'in', portal_group.id)])
