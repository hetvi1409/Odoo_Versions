from odoo import api, fields, models, _, _lt
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError


class Invoice(models.Model):
    _inherit = 'account.move'

    calendar_id = fields.Many2one("calendar.event")
    law_task_id = fields.Many2one("project.task")

    def button_add_deduction(self):
        return {
            'name': _('Invoice Deduction'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id':  self.partner_id.id},
            'res_model': "wizard.invoice.deduction",
        }

    @api.model
    def btn_view_payments(self, ds_time_frame):

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

        payment_reminder_domain = ['|', ('calendar_id', '!=', False), ('law_task_id', '!=', False)]

        for rec in domain:
            payment_reminder_domain.append(rec)

        return self.search(payment_reminder_domain).ids


class InvoiceLines(models.Model):
    _inherit = 'account.move.line'

    expense_id = fields.Many2one('hr.expense')
    trust_account_id = fields.Many2one('trust.account')

