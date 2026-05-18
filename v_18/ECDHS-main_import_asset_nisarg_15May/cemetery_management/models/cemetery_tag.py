from random import randint

from odoo import fields, models


class CemeteryTags(models.Model):
    """Cemetery Tags"""
    _name = 'cemetery.tag'
    _description = "Cemetery Tags"

    def _get_default_color(self):
        return randint(1, 10)

    name = fields.Char('Tag', required=True, translate=True)
    color = fields.Integer('Color', default=_get_default_color)