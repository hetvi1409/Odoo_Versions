# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class View(models.Model):
    _inherit = 'ir.ui.view'
    type = fields.Selection(
        selection_add=[
            ('setaanalysis', 'SETA Analysis'),
            ('setadashboard', 'SETA Dashboard'),
        ]
    )

    def _get_view_info(self):
        return {
            'setaanalysis': {'icon': 'fa fa-tachometer'},
            'setadashboard': {'icon': 'fa fa-tachometer'}
        } | super()._get_view_info()

# class ActWindowView(models.Model):
#     _inherit = 'ir.actions.act_window.view'
#     view_mode = fields.Selection(
#         selection_add=[
#             ('setaanalysis', 'SETA Analysis'),
#             ('setadashboard', 'SETA Dashboard'),
#         ],
#         ondelete={
#             'setaanalysis': 'cascade',
#             'setadashboard': 'cascade',
#         }
#     )
