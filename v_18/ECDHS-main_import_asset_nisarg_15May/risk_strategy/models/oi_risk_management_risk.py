from odoo import api, fields, models

from dateutil.relativedelta import relativedelta

class Risk(models.Model):
    """Risk"""
    _inherit = 'oi_risk_management.risk'

    strategy_id = fields.Many2one('strategic.planning',
                                    string="Strategy")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    year_id = fields.Many2one('arp.year', string="Financial Year")
    internal_audit_id = fields.Many2one('project.project', domain="[('is_internal_project', '=', False)]")

    @api.onchange('year_id')
    def onchange_year_id(self):
        """On change year date"""
        self.start_date = self.year_id.start_date
        self.end_date = self.year_id.end_date


class Year(models.Model):
    _inherit = 'arp.year'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    @api.onchange('start_date')
    def onchange_start_date(self):
        """On change start date"""

        if self.start_date:
            self.end_date = self.start_date + relativedelta(years=1) - relativedelta(days=1)
