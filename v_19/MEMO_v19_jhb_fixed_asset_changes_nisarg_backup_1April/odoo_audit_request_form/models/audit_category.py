# -*- coding: utf-8 -*-


from odoo import fields, api, models, _


class CustomAuditCategory(models.Model):
    _name = "custom.audit.category"
    _description = 'Audit Category'
    
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
    
