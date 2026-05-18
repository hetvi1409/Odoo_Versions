# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, _lt
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from .chart import get_line_chart, get_bar_chart, prepare_chart_data

WEEK = ['Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat', 'Sun']
MONTH = [i for i in range(1, 32)]
QUARTER = ['Q1', 'Q2', 'Q3', 'Q4']
YEAR = ['Jan', 'Fab', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

DATE_FORMATE = "%Y-%m-%d 00:00:00"


def get_week_data(obj, domain=None):
    if domain is None:
        domain = []

    weekday = datetime.today().weekday()
    last_date = datetime.today() + timedelta(days=-weekday)
    data = {}

    for i in range(weekday + 1):
        temp_domain = [('create_date', '>', (last_date + timedelta(days=i)).strftime(DATE_FORMATE)),
                       ('create_date', '<', (last_date + timedelta(days=i + 1)).strftime(DATE_FORMATE))]
        for rec in domain:
            temp_domain.append(rec)
        data.update({i: obj.search(temp_domain)})

    return data


def get_month_data(obj, domain=None):
    if domain is None:
        domain = []

    month_day = datetime.today().day
    first_day = datetime.today() + timedelta(days=-month_day + 1)
    data = {}

    for i in range(month_day):
        temp_domain = [('create_date', '>', (first_day + timedelta(days=i)).strftime(DATE_FORMATE)),
                       ('create_date', '<', (first_day + timedelta(days=i + 1)).strftime(DATE_FORMATE))]
        for rec in domain:
            temp_domain.append(rec)
        data.update({i: obj.search(temp_domain)})

    return data


def get_year_data(obj, domain=None):
    if domain is None:
        domain = []

    date_obj = datetime.today().replace(day=1)
    month = date_obj.month
    first_month = date_obj + relativedelta(months=-month + 1)
    data = {}

    for i in range(month):
        temp_domain = [('create_date', '>', (first_month + relativedelta(months=i)).strftime(DATE_FORMATE)),
                       ('create_date', '<', (first_month + relativedelta(months=i + 1)).strftime(DATE_FORMATE))]
        for rec in domain:
            temp_domain.append(rec)
        data.update({i: obj.search(temp_domain)})

    return data


def get_percentage(a, b):
    try:
        if not a and not b:
            return 0
        elif not a:
            return -100
        elif not b:
            return 100
        elif a == b:
            return 0
        else:
            c = a - b
            d = (a + b) / 2
            return (c / d) * 100
    except:
        return 0


class Users(models.Model):
    _inherit = 'res.users'

    def get_invoice_data(self, ds_time_frame):
        case_matter_obj = self.env['project.project']

        if ds_time_frame == 'this_week':
            last_date = datetime.today() + timedelta(days=-datetime.today().weekday())
            domain = [('date', '>=', last_date.strftime("%Y-%m-%d 00:00:00"))]
            last_domain = [('date', '<=', last_date.strftime("%Y-%m-%d 00:00:00")),
                           ('date', '>=', (last_date + timedelta(days=-7)).strftime("%Y-%m-%d 00:00:00"))]

        elif ds_time_frame == 'this_month':
            month_day = datetime.today().replace(day=1)
            domain = [('date', '>=', month_day.strftime("%Y-%m-%d 00:00:00"))]
            last_domain = [('date', '<=', month_day.strftime("%Y-%m-%d 00:00:00")),
                           ('date', '>=', (month_day + relativedelta(months=-1)).strftime("%Y-%m-%d 00:00:00"))]

        elif ds_time_frame == 'this_year':
            year_day = datetime.today().replace(day=1, month=1)
            domain = [('date', '>=', year_day.strftime("%Y-%m-%d 00:00:00"))]
            last_domain = [('date', '<=', year_day.strftime("%Y-%m-%d 00:00:00")),
                           ('date', '>=', (year_day + relativedelta(years=-1)).strftime("%Y-%m-%d 00:00:00"))]

        else:
            raise UserError("Dashboard Not Loaded")

        project_domain = ['|', ('is_case', '=', True), ('is_matter', '=', True)]
        last_project_domain = ['|', ('is_case', '=', True), ('is_matter', '=', True)]

        for rec in domain:
            project_domain.append(rec)

        for rec in last_domain:
            last_project_domain.append(rec)

        task_ids = case_matter_obj.search(project_domain).mapped('task_ids')
        last_task_ids = case_matter_obj.search(last_project_domain).mapped('task_ids')

        invoice_ids = len(task_ids.filtered(lambda x: not x.law_invoice_ids))
        last_invoice_ids = len(last_task_ids.filtered(lambda x: not x.law_invoice_ids))

        per_card_new_invoice = get_percentage(invoice_ids, last_invoice_ids)

        if per_card_new_invoice > 0:
            per_card_new_invoice = "+%.2f" % per_card_new_invoice
            color_card_new_invoice = 'success'
        else:
            per_card_new_invoice = "%.2f" % per_card_new_invoice
            color_card_new_invoice = 'danger'

        return {
            'card_invoice': {
                'value': invoice_ids,
                'class': color_card_new_invoice,
                'percentage': per_card_new_invoice
            },
        }

    def get_card_details(self, domain, last_domain):
        lead_obj = self.env['crm.lead']
        project_obj = self.env['project.project']
        invoice_obj = self.env['account.move']

        card_new_leads = len(lead_obj.search(domain))
        last_card_new_leads = len(lead_obj.search(last_domain))
        per_card_new_leads = get_percentage(card_new_leads, last_card_new_leads)

        if per_card_new_leads >= 0:
            per_card_new_leads = "+%.2f" % per_card_new_leads
            color_card_new_leads = 'success'
        else:
            per_card_new_leads = "%.2f" % per_card_new_leads
            color_card_new_leads = 'danger'

        # case / matter
        project_domain = ['|', ('is_case', '=', True), ('is_matter', '=', True)]
        last_project_domain = ['|', ('is_case', '=', True), ('is_matter', '=', True)]

        for rec in domain:
            project_domain.append(rec)

        for rec in last_domain:
            last_project_domain.append(rec)

        card_case_matter = len(project_obj.search(project_domain))
        last_card_case_matter = len(project_obj.search(last_project_domain))
        per_card_case_matter = get_percentage(card_case_matter, last_card_case_matter)

        if per_card_case_matter > 0:
            per_card_case_matter = "+%.2f" % per_card_case_matter
            color_card_case_matter = 'success'
        else:
            per_card_case_matter = "%.2f" % per_card_case_matter
            color_card_case_matter = 'danger'

        # payment_reminder
        payment_reminder_domain = ['|', ('calendar_id', '!=', False), ('law_task_id', '!=', False)]
        last_payment_reminder_domain = ['|', ('calendar_id', '!=', False), ('law_task_id', '!=', False)]

        for rec in domain:
            payment_reminder_domain.append(rec)

        for rec in last_domain:
            last_payment_reminder_domain.append(rec)

        card_payment_reminder = len(invoice_obj.search(payment_reminder_domain))
        last_card_payment_reminder = len(invoice_obj.search(last_payment_reminder_domain))

        per_card_payment_reminder = get_percentage(card_payment_reminder, last_card_payment_reminder)

        if per_card_payment_reminder > 0:
            per_card_payment_reminder = "+%.2f" % per_card_payment_reminder
            color_card_payment_reminder = 'success'
        else:
            per_card_payment_reminder = "%.2f" % per_card_payment_reminder
            color_card_payment_reminder = 'danger'

        return {
            'card_new_leads': {'value': card_new_leads, 'class': color_card_new_leads,
                               'percentage': per_card_new_leads},
            'card_case_matter': {'value': card_case_matter, 'class': color_card_case_matter,
                                 'percentage': per_card_case_matter},
            'card_payment': {'value': card_payment_reminder, 'class': color_card_payment_reminder,
                             'percentage': per_card_payment_reminder},
        }

    def get_law_dashboard_data(self, ds_time_frame):

        project_obj = self.env['project.project']
        partner_obj = self.env['res.partner']
        invoice_obj = self.env['account.move']

        if ds_time_frame == 'this_week':
            time_frame = 'Week'
            labels = WEEK
            last_date = datetime.today() + timedelta(days=-datetime.today().weekday())
            domain = [('create_date', '>=', last_date.strftime("%Y-%m-%d 00:00:00"))]
            last_domain = [('create_date', '<=', last_date.strftime("%Y-%m-%d 00:00:00")),
                           ('create_date', '>=', (last_date + timedelta(days=-7)).strftime("%Y-%m-%d 00:00:00"))]

            case_data = [len(i) for i in get_week_data(project_obj, [('is_case', '=', True)]).values()]
            chart_court_case_growth = [len(i) for i in get_week_data(project_obj, [('is_case', '=', True)]).values()]
            matter_data = [len(i) for i in get_week_data(project_obj, [('is_matter', '=', True)]).values()]
            sales_data = [sum(i.mapped('amount_total')) for i in
                          get_week_data(invoice_obj, ['|', ('law_task_id', '!=', False),
                                                      ('calendar_id', '!=', False)]).values()]
            client_growth = [len(i) for i in get_week_data(partner_obj, [('is_law_client', '=', True)]).values()]

        elif ds_time_frame == 'this_month':
            time_frame = 'Month'
            labels = MONTH
            month_day = datetime.today().replace(day=1)
            domain = [('create_date', '>=', month_day.strftime("%Y-%m-%d 00:00:00"))]
            last_domain = [('create_date', '<=', month_day.strftime("%Y-%m-%d 00:00:00")),
                           ('create_date', '>=', (month_day + relativedelta(months=-1)).strftime("%Y-%m-%d 00:00:00"))]

            case_data = [len(i) for i in get_month_data(project_obj, [('is_case', '=', True)]).values()]
            chart_court_case_growth = [len(i) for i in get_month_data(project_obj, [('is_case', '=', True)]).values()]
            matter_data = [len(i) for i in get_month_data(project_obj, [('is_matter', '=', True)]).values()]
            sales_data = [sum(i.mapped('amount_total')) for i in
                          get_month_data(invoice_obj, ['|', ('law_task_id', '!=', False),
                                                       ('calendar_id', '!=', False)]).values()]
            client_growth = [len(i) for i in get_month_data(partner_obj, [('is_law_client', '=', True)]).values()]

        elif ds_time_frame == 'this_year':
            time_frame = 'Year'
            labels = YEAR
            year_day = datetime.today().replace(day=1, month=1)
            domain = [('create_date', '>=', year_day.strftime("%Y-%m-%d 00:00:00"))]
            last_domain = [('create_date', '<=', year_day.strftime("%Y-%m-%d 00:00:00")),
                           ('create_date', '>=', (year_day + relativedelta(years=-1)).strftime("%Y-%m-%d 00:00:00"))]

            case_data = [len(i) for i in get_year_data(project_obj, [('is_case', '=', True)]).values()]
            chart_court_case_growth = [len(i) for i in get_year_data(project_obj, [('is_case', '=', True)]).values()]
            matter_data = [len(i) for i in get_year_data(project_obj, [('is_matter', '=', True)]).values()]
            sales_data = [sum(i.mapped('amount_total')) for i in
                          get_year_data(invoice_obj, ['|', ('law_task_id', '!=', False),
                                                      ('calendar_id', '!=', False)]).values()]
            client_growth = [len(i) for i in get_year_data(partner_obj, [('is_law_client', '=', True)]).values()]

        else:
            raise UserError("Dashboard Not Loaded")

        dashboard_data = self.get_card_details(domain, last_domain)
        invoice_data = self.get_invoice_data(ds_time_frame)
        dashboard_data.update(invoice_data)

        for key, value in dashboard_data.items():
            value.update({'time_frame': time_frame})

        chart_data = {
            'chart_case_type':
                get_line_chart(
                    prepare_chart_data(labels, {
                        'Case': {'data': case_data, 'color': '#FFFFFF'},
                        'Matter': {'data': matter_data, 'color': '#349f4c'}
                    })),
            'chart_court_case_growth':
                get_line_chart(
                    prepare_chart_data(labels, {
                        'Court Case': {'data': chart_court_case_growth, 'color': '#FFFFFF'},
                    })),
            'chart_sales_growth':
                get_line_chart(
                    prepare_chart_data(labels, {
                        'Sales': {'data': sales_data, 'color': '#FFFFFF'}
                    })),
            'chart_client_growth':
                get_line_chart(
                    prepare_chart_data(labels, {
                        'Client': {'data': client_growth, 'color': '#FFFFFF'}
                    })),
        }

        return [dashboard_data, chart_data]

    def get_case_form_view_id(self, ev):
        return self.env.ref('law_firm_bits.view_case_form').id
