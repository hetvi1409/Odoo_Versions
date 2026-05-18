from odoo.exceptions import ValidationError
from odoo import api, fields, models, tools, _


class DocumentsFolder(models.Model):
    _inherit = 'documents.document'

    # New field to indicate retention or permanence
    is_permanent = fields.Boolean(string="Permanent", default=False,
                                  help="If checked, the folder and its contents will not be subject to automatic deletion based on retention policies.")
    enabled = fields.Boolean(string="Enabled")
    retention_periods = fields.Float(string="Retention Frame")
    retention_duration_unit = fields.Selection(
        [('days', 'Days'), ('months', 'Months'), ('years', 'Years')],
        string='Duration Unit', default='months',
        help='Select the unit for the retention duration.')
    retention_duration_in_days = fields.Float(
        string='Retention Duration in Days',
        compute='_compute_retention_duration_in_days')

    @api.depends('retention_periods', 'retention_duration_unit')
    def _compute_retention_duration_in_days(self):
        for record in self:
            record.retention_duration_in_days = False
            if not record.is_permanent:
                if record.retention_duration_unit == 'years':
                    record.retention_duration_in_days = record.retention_periods * 365
                elif record.retention_duration_unit == 'months':
                    record.retention_duration_in_days = record.retention_periods * 30
                else:
                    record.retention_duration_in_days = record.retention_periods
    disposal_periods = fields.Float(string="Disposal Period")
