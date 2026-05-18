from odoo import models, fields


class ResPartner(models.Model):
    _inherit='res.partner'

    is_job_location = fields.Boolean(string='Is Job Location?', default=False)