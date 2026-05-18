# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class View(models.Model):
    _inherit = 'ir.ui.view'
    type = fields.Selection(
        selection_add=[
            ('setaanalysis', 'seta Analysis'),
            ('setadashboard', 'seta Dashboard'),
        ]
    )

class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'
    view_mode = fields.Selection(
        selection_add=[
            ('setaanalysis', 'seta Analysis'),
            ('setadashboard', 'seta Dashboard'),
        ],
        ondelete={
            'setaanalysis': 'cascade',
            'setadashboard': 'cascade',
        }
    )