from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class AppReport(models.AbstractModel):
    _name = 'report.performance_management.report_template_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        outcome = self.env['performance.outcome'].search([
            ('portfolio_id', '=', data['portfolio_id'])])

        return{
            'docids': docids,
            'portfolio_name': data['portfolio_name'],
            'description': data['description'],
            'outcomes':outcome
        }