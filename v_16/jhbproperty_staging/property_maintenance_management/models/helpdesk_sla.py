from odoo import api, fields, models, _


class Maintenance(models.Model):
    _inherit = 'helpdesk.sla'

    issue_type = fields.Selection(
        [('emergency', 'Emergency'), ('minor', 'Minor'), ('major', 'Major')],
        string='Issue Type')
