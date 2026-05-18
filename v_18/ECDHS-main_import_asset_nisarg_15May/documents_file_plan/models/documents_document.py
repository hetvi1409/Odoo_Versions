# -*- coding: utf-8 -*-
from odoo import api,fields, models


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    @staticmethod
    def year_range_selection(start_offset, end_offset, steps=1):
        current_year = fields.Datetime.now().year
        return [(str(year), str(year)) for year in range(current_year - start_offset, current_year + end_offset, steps)]

    reference_month = fields.Selection([
        ('january', 'January'),
        ('february', 'February'),
        ('march', 'March'),
        ('april', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('august', 'August'),
        ('september', 'September'),
        ('october', 'October'),
        ('november', 'November'),
        ('december', 'December'),
    ], string='Month')
    reference_year = fields.Selection(
        string='Year',
        selection=lambda self: self.year_range_selection(50, 20),
        default=lambda self: str(fields.Datetime.now().year),
        help='Select the year for which you want to see file for which year.')
    description_1 = fields.Html("Description 1")
    description_2 = fields.Html("Description 2")
    sender_id = fields.Many2one("res.users", string="Sender", help="Person who send the file",default=lambda self: self.env.user)
    receiver_id = fields.Many2one("res.users", string="Receiver", help="Person who receive the file")
    department_id = fields.Many2one('hr.department', string='Department', copy=True, )
    location_id = fields.Many2one('custom.physical.location', string='Location', copy=True, )
    d_number = fields.Char(string='D Number', copy=False)
    umz_number = fields.Char(string='UMZ Number', copy=False)
    submission_date = fields.Datetime(string="Submission Date")


class RequestWizard(models.TransientModel):
    _inherit = "documents.request_wizard"

    department_id = fields.Many2one('hr.department', string='Department', copy=True, )
    location_id = fields.Many2one('custom.physical.location', string='Location', copy=True, )
    d_number = fields.Char(string='D Number', copy=False)
    umz_number = fields.Char(string='UMZ Number', copy=False)
    requester_id = fields.Many2one("res.users", string="Requester", help="Person who request for the file",default=lambda self: self.env.user)
    request_date = fields.Datetime(string="Request Date")