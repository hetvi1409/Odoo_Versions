from random import randint
from odoo import fields, models


class JobCardTag(models.Model):
    _name = 'job.card.tag'
    _description = 'Job Card Tag'

    name = fields.Char('Tag Name', help='name of the tag',
                       required=True)

    def _default_color(self):
        return randint(1, 11)

    color = fields.Integer('Color', default=_default_color)
