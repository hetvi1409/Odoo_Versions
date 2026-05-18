from odoo import models, fields, api, _
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from .chart import get_line_chart, get_bar_chart, prepare_chart_data


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    count_case = fields.Integer(compute="_compute_count_case_or_matter")
    count_matter = fields.Integer(compute="_compute_count_case_or_matter")

    @api.model
    def btn_view_leads(self, ds_time_frame):

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

        return self.search(domain).ids

    def _compute_count_case_or_matter(self):
        for lead in self:
            case = matter = 0
            for rec in self.env['project.project'].search([('crm_lead_id', '=', lead.id)]):
                if rec.is_case:
                    case += 1
                else:
                    matter += 1

            lead.count_case = case
            lead.count_matter = matter

    def action_open_case(self):
        action = self.env.ref('law_firm_bits.action_view_all_cases').sudo().read()[0]
        action['domain'] = [('crm_lead_id', '=', self.id), ('is_case', '=', True)]
        if action.get('context'):
            action['context'] = {'default_crm_lead_id': self.id,
                                 'default_is_case': True,
                                 'default_partner_id': self.partner_id.id}
        return action

    def action_open_matter(self):
        action = self.env.ref('law_firm_bits.action_view_all_matters').sudo().read()[0]
        action['domain'] = [('crm_lead_id', '=', self.id), ('is_matter', '=', True)]
        if action.get('context'):
            action['context'] = {'default_crm_lead_id': self.id,
                                 'default_is_matter': True,
                                 'default_partner_id': self.partner_id.id}
        return action
