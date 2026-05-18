# -*- coding: utf-8 -*-

from odoo import models, fields


class SagovTenderUiSection(models.Model):
    _name = 'sagovtender.ui.section'
    _description = 'Tender UI Section'
    _order = 'section_type, name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    section_type = fields.Selection([
        ('tab', 'Tab'),
        ('header_button', 'Header Button')
    ], string='Section Type', required=True, default='tab')

    _sql_constraints = [
        ('code_section_type_unique', 'unique(code, section_type)', 'Section code must be unique per type.')
    ]
