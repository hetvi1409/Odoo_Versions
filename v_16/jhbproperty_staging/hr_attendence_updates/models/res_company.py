from odoo import fields, models, api
from odoo.osv.expression import OR

import uuid
from werkzeug.urls import url_join


class ResCompany(models.Model):
    _inherit = 'res.company'

    attendance_overtime_validation = fields.Selection([
        ('no_validation', 'Automatically Approved'),
        ('by_manager', 'Approved by Manager'),
    ], string='Extra Hours Validation', default='by_manager')
