# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class CustomAuditTags(models.Model):
    _name = "custom.audit.tag"
    _description = 'Audit Tags'
    
    name = fields.Char(
        string='Name', 
        copy=False,
        required=True
    )
    code = fields.Char(
        string='Code', 
        copy=False,
        required=True 
    )
    color = fields.Integer(string='Color Index')
    
