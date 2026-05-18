# -*- coding: utf-8 -*-
from odoo import api, fields, models

class RootCause(models.Model):
    _name = "root.cause"
    _description = "Root Cause"

    ref = fields.Char(default='New', string="Cause No.")
    name = fields.Char(default='New', string="Title")
    type = fields.Selection(
        [('materials', 'Materials'), ('machines', 'Machines'), ('methods', 'Methods'),
         ('measurements', 'Measurements'), ('environment', 'Environment'), ('people', 'People')],
        string="Type")
    why1 = fields.Char(string='Why1')
    why2 = fields.Char(string='Why2')
    why3 = fields.Char(string='Why3')
    why4 = fields.Char(string='Why4')
    why5 = fields.Char(string='Why5')

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('cause.sequence')
        return super(RootCause, self).create(vals)
