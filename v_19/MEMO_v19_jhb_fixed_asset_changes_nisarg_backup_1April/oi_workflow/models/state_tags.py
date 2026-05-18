from odoo import models, api, fields, _
from random import randint


class StatetTags(models.Model):
    """ Tags of state's workfkow """
    _name = "state.tags"
    _description = "State Tags"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _name_uniq = models.Constraint(
        'unique(name)',
        'Tag name already exists!',
    )