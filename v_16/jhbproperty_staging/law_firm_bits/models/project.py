# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, _lt
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError
from collections import OrderedDict

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class Project(models.Model):
    _inherit = 'project.project'
    name = fields.Char(string='Sequence Number',
                       default=lambda self: _('New'))
    status = fields.Char(string='Rating')
    matter_name = fields.Char(string='Matter')

    is_case = fields.Boolean("Cases", default=False)
    is_matter = fields.Boolean("Matter", default=False)

    court_id = fields.Many2one("court.court")
    judge_id = fields.Many2one("court.judge")

    crm_lead_id = fields.Many2one("crm.lead")

    task_template_id = fields.Many2one("law.task.list")
    is_tasks_listed = fields.Boolean(default=False)

    close_reason = fields.Selection(
        selection=[('draft', 'Draft'), ('won', 'Won'), ('loss', 'Loss'), ('settled', 'Settled'),
                   ('dropped', 'Dropped')], default='draft')

    count_trust_account = fields.Integer(compute="_compute_count_trust_account")
    crime_type_id = fields.Many2one("crime.type")

    document_ids = fields.Many2many("ir.attachment")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('project.project') or 'New'
        return super(Project, self).create(vals)

    @api.model
    def get_upcoming_reminders(self):
        data = []
        for rec in self.env['calendar.event'].search(
                [('start', '>=', (date.today() + timedelta(days=1)).strftime(DATE_FORMAT))],
                limit=10):
            data.append({
                'name': rec.name,
                'model': 'calendar.event',
                'id': rec.id,
                'desc': rec.start.strftime(DATE_FORMAT),
                'date': rec.start.strftime(DATE_FORMAT),
                'icon': 'calendar',
                'partner_ids': [{
                    'id': partner.id,
                    'name': partner.name,
                } for partner in rec.partner_ids]

            })

        for rec in self.env['project.task'].search(
                [('planned_date_begin', '>=', (date.today() + timedelta(days=1)).strftime(DATE_FORMAT))],
                limit=10):
            data.append({
                'name': rec.name,
                'model': 'project.task',
                'id': rec.id,
                'desc': rec.planned_date_begin.strftime(DATE_FORMAT),
                'date': rec.planned_date_begin.strftime(DATE_FORMAT),
                'icon': 'tasks',
                'partner_ids': [{
                    'id': partner.id,
                    'name': partner.name,
                } for partner in rec.user_ids.mapped('partner_id')]
            })
        data.sort(key=lambda x: x['date'])
        return data

    @api.model
    def get_today_reminders(self):
        data = []
        for rec in self.env['calendar.event'].search(
                [('start', '>=', date.today().strftime(DATE_FORMAT)),
                 ('start', '<', (date.today() + timedelta(days=1)).strftime(DATE_FORMAT))],
                limit=10):
            data.append({
                'name': rec.name,
                'model': 'calendar.event',
                'id': rec.id,
                'desc': rec.start.strftime(DATE_FORMAT),
                'date': rec.start.strftime(DATE_FORMAT),
                'icon': 'calendar',
                'partner_ids': [{
                    'id': partner.id,
                    'name': partner.name,
                } for partner in rec.partner_ids]
            })

        for rec in self.env['project.task'].search(
                [('planned_date_begin', '>=', date.today().strftime(DATE_FORMAT)),
                 ('planned_date_begin', '<', (date.today() + timedelta(days=1)).strftime(DATE_FORMAT))],
                limit=10):
            data.append({
                'name': rec.name,
                'model': 'project.task',
                'id': rec.id,
                'desc': rec.planned_date_begin.strftime(DATE_FORMAT),
                'date': rec.planned_date_begin.strftime(DATE_FORMAT),
                'icon': 'tasks',
                'partner_ids': [{
                    'id': partner.id,
                    'name': partner.name,
                } for partner in rec.user_ids.mapped('partner_id')]
            })
        data.sort(key=lambda x: x['date'])
        return data

    @api.model
    def btn_view_case_matter(self, ds_time_frame):

        if ds_time_frame == 'this_week':
            last_date = datetime.today() + timedelta(days=-datetime.today().weekday())
            domain = [('create_date', '>=', last_date.strftime("%Y-%m-%d 00:00:00"))]

        elif ds_time_frame == 'this_month':
            month_day = datetime.today().replace(day=1)
            domain = [('create_date', '>=', month_day.strftime("%Y-%m-%d 00:00:00"))]

        elif ds_time_frame == 'this_year':
            year_day = datetime.today().replace(day=1, month=1)
            domain = [('create_date', '>=', year_day.strftime("%Y-%m-%d 00:00:00"))]

        else:
            raise UserError("Dashboard Not Loaded")

        project_domain = ['|', ('is_case', '=', True), ('is_matter', '=', True)]
        for rec in domain:
            project_domain.append(rec)

        return self.search(project_domain).ids

    def _compute_count_trust_account(self):
        for rec in self:
            rec.count_trust_account = len(
                self.env['trust.account'].search(['|', ('matter_id', '=', rec.id), ('case_id', '=', rec.id)]))

    def create_default_tasks(self):
        for rec in self:
            for task in rec.task_template_id.task_ids:
                self.env['project.task'].create({
                    'name': task.name,
                    'description': task.description,
                    'project_id': rec.id,
                    'law_default_id': task.id,
                    'law_task_type': task.law_task_type,
                })
            rec.is_tasks_listed = True

    def open_close_reason_wizard(self):
        return self.env.ref('law_firm_bits.wizard_law_close_reason_action').sudo().read()[0]

    def open_trust_account_case_view(self):
        action = self.env.ref('law_firm_bits.law_trust_account_act_action').sudo().read()[0]
        action['domain'] = [('case_id', '=', self.id)]
        if action.get('context'):
            action['context'] = {'default_case_id': self.id, 'default_partner_id': self.partner_id.id}
        return action

    def open_trust_account_matter_view(self):
        action = self.env.ref('law_firm_bits.law_trust_account_act_action').sudo().read()[0]
        action['domain'] = [('matter_id', '=', self.id)]
        if action.get('context'):
            action['context'] = {'default_matter_id': self.id, 'default_partner_id': self.partner_id.id}
        return action
