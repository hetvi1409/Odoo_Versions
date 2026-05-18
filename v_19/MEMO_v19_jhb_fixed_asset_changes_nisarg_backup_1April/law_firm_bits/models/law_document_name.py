from odoo import models, fields, _


class DocumentName(models.Model):
    _name = 'law.document.name'
    _description = 'Document names'

    name = fields.Char("Name")
