from odoo import models, fields


class CauseDeath(models.Model):
    _name = 'cause.death'
    _description = 'Cause of Death'

    name = fields.Char(string='Name', required=True,
                       help='Name of the cause of death')
    category = fields.Char(string='Category', help='Category of '
                                                   'the cause of death')
    code = fields.Char(string='Code', required=True,
                       help='Code representing the cause of death')
