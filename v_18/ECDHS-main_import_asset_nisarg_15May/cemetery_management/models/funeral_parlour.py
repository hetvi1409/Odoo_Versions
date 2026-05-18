from odoo import models, fields


class FuneralParlour(models.Model):
    _name = 'funeral.parlour'
    _description = 'Funeral Parlour'
    _rec_name = 'name'

    def _get_municipality(self):
        """Returns municipality data"""
        municipality = self.env['municipality.municipality'].search([('company_id', '=', self.env.company.id)], limit=1)
        return municipality.id

    municipality_id = fields.Many2one('municipality.municipality',
                                                 string="Municipality",
                                                 default=_get_municipality,)
    name = fields.Char(string='Funeral Palour', required=True)
    undertaker_ids = fields.Many2many('undertaker.undertaker', string='Particulars of Owner/manager',
                                      )
    street = fields.Char(string="Street", required=True,
                         help="Name of the street")
    street2 = fields.Char(string="Street 2",
                          help="Name of the street")
    postal_code = fields.Char(string="Postal", help="Postal code")
    city = fields.Char(string="City", help="Name of the city")
    ward_id = fields.Many2one('ward.ward', string="Ward", help="Name of the Ward")
    province_id = fields.Many2one('province.province', string="Province",
                                  required=False,
                                  domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict',
                                 help="Name of the country")
    coc = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="COC", help="Certificate of Compliance", default='no')
    premises_in_operation = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Premises in Operation",
        help="Is the premises currently in operation?", default='no')
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")

