# -*- coding: utf-8 -*-

from odoo import fields, models


class EcdhsContractChangeRequest(models.Model):
    _name = 'ecdhs.contract.change.request'
    _description = 'Contract Provider Change Request'
    _order = 'contract_id, sequence, id'

    contract_id = fields.Many2one(
        'ecdhs.contract', string='Contract', required=True, ondelete='cascade'
    )
    sequence = fields.Integer(default=10)
    section_reference = fields.Char('Draft Terms Section', required=True)
    requested_change = fields.Text('Requested Change', required=True)
    submitted_by = fields.Selection([
        ('provider', 'Service Provider'),
        ('internal', 'Internal Team'),
    ], default='provider', required=True)
    status = fields.Selection([
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('incorporated', 'Incorporated in Revised Draft'),
    ], string='Status', default='submitted', required=True)
    requested_on = fields.Datetime('Requested On', default=fields.Datetime.now)
    due_date = fields.Date('Response Due Date')
    response_note = fields.Text('Response / Decision Note')
    resolved_by_id = fields.Many2one('res.users', string='Resolved By')
    resolved_on = fields.Datetime('Resolved On')
