# -*- coding: utf-8 -*-
from odoo import fields, models


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    is_portal_attendance = fields.Boolean(string="From Portal",
                               help="To check if the attendance from portal "
                                    "or not", default=False)