# -*- coding: utf-8 -*-

from odoo import api, fields, models,_


class HelpdeskTicketLegalSubtype(models.Model):
    _name = 'helpdesk.ticket.legal.subtype'
    _description = 'Helpdesk Ticket Legal Subtype'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)

    _name_uniq = models.Constraint(
        'unique(name)',
        'A type with the same name already exists',
    )