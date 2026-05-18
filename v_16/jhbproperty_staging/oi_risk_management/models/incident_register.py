from random import randint

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
# the order is important
from odoo.tools.safe_eval import safe_eval


class IncidentRegister(models.Model):
    _name = 'incident.register'
    _description = 'Incident Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    incident_id = fields.Char(string="Incident ID")
    type = fields.Selection([('Incident','Incident'),('Near-Miss','Near-Miss')],string="Type")
    category_id = fields.Many2one('oi_risk_management.activity_category',string="Category")
    description = fields.Text(string="Description")
    incident_date = fields.Datetime(default=fields.Datetime.now, copy=False,string="Date")
    root_cause = fields.Text(string="Root Cause")
    impact = fields.Integer(required=True, string='Impact / Potential Impact')
    actions_taken = fields.Char(string="Actions Taken")
    responsible_person = fields.Many2one('hr.employee',string="Responsible Person")
    status = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('close', 'Close'),
    ], default='open', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        # Assign sequence numbers for records missing incident_id
        for vals in vals_list:
            if not vals.get('incident_id'):
                vals['incident_id'] = self.env['ir.sequence'].sudo().next_by_code('incident.register') or '/'
        records = super().create(vals_list)
        return records
