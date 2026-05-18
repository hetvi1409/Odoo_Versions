from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GraveGrave(models.Model):
    _name = 'grave.grave'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Grave Grave'

    def _get_municipality(self):
        """Returns municipality data"""
        municipality = self.env['municipality.municipality'].search(
            [('company_id', '=', self.env.company.id)], limit=1)
        return municipality.id

    name = fields.Char(string='Grave Name', required=True)
    state = fields.Selection([('active', 'Active'),
                              ('re_use', 'Re Use'),
                              ('purchase', 'Purchased'),
                              ('lease', 'Leased'), ('used', 'Used')],
                             store=True,
                             default='active', compute='_compute_the_state')
    municipality_id = fields.Many2one('municipality.municipality',
                                      default=_get_municipality,
                                      string="Municipality", required=True)
    cemetery_id = fields.Many2one('cemetery.cemetery', string='Cemetery',
                                  domain="[('municipality_id', '=', municipality_id)]")
    number = fields.Char(string='Grave Number', readonly=True)
    section_id = fields.Many2one('cemetery.section', string='Section',
                                  domain="[('cemetery_id', '=', cemetery_id)]")
    grave_type = fields.Selection([('adult', 'Adult'), ('infant', 'Infant')],
                                  string='Grave Type', required=True)
    occupied = fields.Boolean(string='Occupied', copy=False)
    lease_id = fields.Many2one('cemetery.application', string='Lease')
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 help="Company Name",
                                 default=lambda self: self.env.company)

    category = fields.Selection([('general', 'General'), ('vip', 'VIP')],
                                string='Category')
    surveyor_general_number = fields.Char(
        string='Surveyor General Number')
    in_use = fields.Boolean(string='In Use', copy=False)
    rented = fields.Boolean(string='Rented', copy=False)
    grave_rental_value = fields.Float(string='Grave Rental Value')
    purchased = fields.Boolean(string='Purchased', copy=False)
    grave_purchase_value = fields.Float(string='Grave Purchase Value')
    burial_possible = fields.Boolean(string='Burial Possible')
    date_initial_use = fields.Date(string='Date Initial Use')
    burial_type = fields.Char(string='Burial Type')
    tasks = fields.Text(string='Tasks (Inspections)')
    images = fields.Binary(string='Images')
    documents = fields.Binary(string='Documents')

    # person details
    re_use = fields.Boolean(string='Re Use', help='Reuse Grave')

    person_details_ids = fields.One2many('death.register', 'grave_id',
                                         string="Persons Details")

    @api.constrains('surveyor_general_number')
    def _check_surveyor_general_number(self):
        for record in self:
            if record.surveyor_general_number and len(
                    record.surveyor_general_number) != 21:
                raise ValidationError(
                    _(
                        "The Surveyor General Number must be exactly 21 digits long."))

    @api.depends('in_use', 'rented', 'purchased', 're_use')
    def _compute_the_state(self):
        """Compute the state based on purchased, leased, or used"""
        for rec in self:
            state = ""
            if not rec.in_use and not rec.rented and not rec.purchased:
                if rec.re_use:
                    state = "re_use"
                else:
                    state = 'active'
            else:
                if rec.re_use:
                    state = 're_use'
                    if rec.in_use:
                        state = 'used'
                        rec.re_use = False
                    elif rec.rented:
                        state = 'lease'
                    elif rec.purchased:
                        state = 'purchase'
                else:
                    if rec.in_use:
                        state = 'used'
                        rec.re_use = False
                    elif rec.rented:
                        state = 'lease'
                    elif rec.purchased:
                        state = 'purchase'
            rec.state = state

    @api.onchange('re_use')
    def _onchange_reuse(self):
        """Based on the reuse functionality need to change the values in some
        other fields like purchased and leased. based on this configuration,
          we can use the grave in purchase and lease"""
        if self.re_use:
            self.purchased = False
            self.rented = False
            self.in_use = False
        # else:
        #     self.in_use = True

    @api.onchange( 'in_use')
    def _onchange_inuse(self):
        """Based on the inuse functionality need to change the values in some
        other fields like purchased and leased. based on this configuration,
          we can use the grave in purchase and lease"""
        if self.in_use:
            self.occupied = True

    @api.onchange('section_id')
    def _onchange_section_id(self):
        self.cemetery_id = self.section_id.cemetery_id.id

    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code(
            'grave.grave') or 'New'
        res = super(GraveGrave, self).create(vals)
        res.cemetery_id = res.section_id.cemetery_id.id
        return res
