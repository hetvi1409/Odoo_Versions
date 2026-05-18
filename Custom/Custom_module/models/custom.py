from odoo import models, fields, api

class CustomModel(models.Model):
    _name = 'custom.model'

    name = fields.Char('Name')