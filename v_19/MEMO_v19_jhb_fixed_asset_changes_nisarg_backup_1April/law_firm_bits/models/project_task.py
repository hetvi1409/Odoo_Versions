# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, _lt
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import ast


class Task(models.Model):
    _inherit = 'project.task'

    # name = fields.Char(default="/")
    planned_date_begin = fields.Datetime("Start date", tracking=True, task_dependency_tracking=True)
    planned_date_end = fields.Datetime("End date", tracking=True, task_dependency_tracking=True)

    law_task_type = fields.Selection(selection=[('consultation', 'Consultation'),
                                                ('submission', 'Submission'),
                                                ('trial', 'Trial'),
                                                ('meeting', 'Meeting'),
                                                ('other', 'Other'), ])
    law_charges = fields.Float("Charges")

    law_sub_selection = fields.Selection(selection=[('doc', 'Documents'), ('fund', 'Funds')])
    law_document_names = fields.Many2many("law.document.name", string="Documents Names")
    law_fund = fields.Float("Funds")

    law_document_ids = fields.Many2many('ir.attachment', 'law_document_rel')

    court_id = fields.Many2one("court.court")
    judge_id = fields.Many2one("court.judge")

    law_default_id = fields.Many2one("law.task")
    count_invoice = fields.Integer(compute="_compute_count_invoice")

    is_case = fields.Boolean("Cases", related='project_id.is_case')
    is_matter = fields.Boolean("Matter", related='project_id.is_matter')

    law_invoice_ids = fields.One2many('account.move', 'law_task_id', 'Law Invoices')

    def _compute_count_invoice(self):
        for rec in self:
            rec.count_invoice = len(self.env['account.move'].search([('law_task_id', '=', rec.id)]))

    def open_invoice_from_task_view(self):
        action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        domain = ast.literal_eval(action['domain'])
        domain.append(('law_task_id', '=', self.id))
        action['domain'] = domain
        return action

    def update_default_task(self):
        for rec in self:
            if rec.law_default_id:
                rec.law_default_id.write({'name': rec.name, 'description': rec.description})

    def create_law_invoice(self):
        action = self.env.ref('law_firm_bits.wizard_create_law_invoice_action').sudo().read()[0]
        return action

    def default_get(self, default_fields):
        res = super(Task, self).default_get(default_fields)
        # Use context as a mapping, not a callable. Prefer active_id over id.
        if self.env.context.get('active_model') == 'project.project':
            active_model = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id') or self.env.context.get('id')
            if active_model and active_id:
                project = self.env[active_model].browse(active_id)
                if project:
                    res.update({'partner_id': project.partner_id.id})
        return res

    @api.model
    def btn_view_to_invoice_tasks(self, ds_time_frame):
        case_matter_obj = self.env['project.project']

        if ds_time_frame == 'this_week':
            last_date = datetime.today() + timedelta(days=-datetime.today().weekday())
            domain = [('date', '>=', last_date.strftime("%Y-%m-%d 00:00:00"))]

        elif ds_time_frame == 'this_month':
            month_day = datetime.today().replace(day=1)
            domain = [('date', '>=', month_day.strftime("%Y-%m-%d 00:00:00"))]

        elif ds_time_frame == 'this_year':
            year_day = datetime.today().replace(day=1, month=1)
            domain = [('date', '>=', year_day.strftime("%Y-%m-%d 00:00:00"))]

        else:
            raise UserError("Dashboard Not Loaded")

        project_domain = ['|', ('is_case', '=', True), ('is_matter', '=', True)]

        for rec in domain:
            project_domain.append(rec)

        return case_matter_obj.search(project_domain).mapped('task_ids').filtered(lambda x: not x.law_invoice_ids).ids

