# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    legal_type = fields.Selection([('general`', 'General'), ('property', 'Property'), ], string="Legal Type")
    legal_sub_type = fields.Many2one('helpdesk.ticket.legal.subtype', string="Sub Type")
    legal_status = fields.Selection(
        [('0 %`', '0 %'), ('1-25 %', '1-25 %'), ('25-50 %', '25-50 %'), ('50-75 %', '50-75 %'),
         ('75-100 %', '75-100 %'), ('100 %', '100 %')], string="Status")
    legal_source = fields.Selection([('internal`', 'Internal'), ('external', 'External'), ], string="Legal Source")
    our_client_id = fields.Many2one('hr.department',string="Our Client")
    our_client_contact_id = fields.Many2one('hr.employee',string="Our Client Contact")
    date_created = fields.Datetime(string="Date Created",default=lambda self: fields.Datetime.now())
    estimated_completion_date = fields.Datetime(string="Estimated Completion Date")
    total_expenses = fields.Float(string="Total Expenses")

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    is_legal_team = fields.Boolean(string="Is Legal Team")