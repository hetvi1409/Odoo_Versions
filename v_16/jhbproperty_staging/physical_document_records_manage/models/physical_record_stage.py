# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class CustomPhysicalRecordStage(models.Model):
    _name = 'custom.physical.record.stage'
    _description = 'Record Stage Custom'

    name = fields.Char(
        string='Name',
        required=True,
    )
    fold = fields.Boolean(
        string="Folded in Kanban"
    )
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: