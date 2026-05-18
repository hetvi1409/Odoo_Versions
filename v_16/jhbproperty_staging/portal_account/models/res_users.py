from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    region_ids = fields.Many2many(
        'regions',
        'regions_res_users_rel',
        'res_users_id',
        'regions_id',
        string='Allowed Regions'
    )
