from odoo import models, fields


class EntityClass(models.Model):
    """
    Model representing a class of procurement entity.
    """
    _name = 'entity.class'
    _description = 'Entity Class'

    name = fields.Char(string='Class Name',
                       help='The name of the class of the procurement entity')
