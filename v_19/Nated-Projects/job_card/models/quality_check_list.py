from odoo import fields, models


class QualityCheckList(models.Model):
    _name = 'quality.check.list'
    _description = 'Quality Check List'

    name = fields.Char(help='Name for the Quality Check List', required=True)
    description = fields.Text('Description')