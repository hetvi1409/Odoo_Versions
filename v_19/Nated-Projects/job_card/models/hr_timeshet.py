from odoo import models, fields


class HrTimesheet(models.Model):
    _inherit = 'account.analytic.line'
    """Inheriting Hr Timesheet"""

    job_card_id = fields.Many2one('job.card')
