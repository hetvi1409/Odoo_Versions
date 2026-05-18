from odoo import models, fields


class TenderCategory(models.Model):
    """
    Model representing a category for tenders.
    """
    _name = 'tender.category'
    _description = 'Tender Category'

    name = fields.Char(string='Category Name', required=True,
                       help='The name of the tender category')
    description = fields.Text(string='Description',
                              help='Description of the tender category')
