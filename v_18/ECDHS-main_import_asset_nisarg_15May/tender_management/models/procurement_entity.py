from odoo import models, fields


class ProcurementEntity(models.Model):
    """
    Model representing a procurement entity.
    """
    _name = 'procurement.entity'
    _description = 'Procurement Entity'

    name = fields.Char(string='Entity Name',
                       help='The name of the procurement entity')
    entity_class_id = fields.Many2one('entity.class', string='Class of Entity',
                                      help='Class of the procurement entity')
