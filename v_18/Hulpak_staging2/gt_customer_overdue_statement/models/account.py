# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, AccessError
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta, date
from odoo import api, fields, models, _
from werkzeug.urls import url_encode
from odoo.tools.misc import formatLang
from itertools import groupby
from odoo.osv import expression
import uuid
import time

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'line_ids.amount_residual',
        'line_ids.currency_id')
    def _compute_residual(self):
        for record in self:
            record.paid_amount = record.amount_total - record.amount_residual
    
    paid_amount = fields.Float(string="Payments/Credit", compute='_compute_residual')
    new_date_invoice = fields.Date(string='New Invoice Date', related='invoice_date')
    new_date_due = fields.Date(string='New Due Date', related='invoice_date_due')
    new_company_id = fields.Many2one('res.company', string='New Company',related='company_id')
    
    
class account_move_line(models.Model):
    _inherit = 'account.move.line'

    stat_report = fields.Boolean(string='Statement Report')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
