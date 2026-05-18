from odoo import models, fields, _


class Court(models.Model):
    _name = 'court.court'
    _description = 'Court'

    name = fields.Char("Court Name")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    country_code = fields.Char(related='country_id.code', string="Country Code")

    judge_ids = fields.One2many("court.judge", 'court_id')
