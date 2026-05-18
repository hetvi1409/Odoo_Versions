from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'

    seta_lab_api_key = fields.Char('SETA Lab API Key')

class SETALabAPIKeyWizard(models.TransientModel):
    _name = 'seta.lab.api.key.wizard'
    _description = 'SETA Lab API Key Wizard'

    seta_lab_api_key = fields.Char('SETA Lab API Key')

    # Default Get
    def default_get(self, fields):
        res = super(SETALabAPIKeyWizard, self).default_get(fields)
        company = self.env.user.company_id
        res['seta_lab_api_key'] = company.seta_lab_api_key
        return res

    def action_update_seta_lab_api_key(self):
        company = self.env.user.company_id
        company.seta_lab_api_key = self.seta_lab_api_key
        return True
    
    def action_access_seta_lab(self):
        seta_lab_url = self.env['ir.config_parameter'].sudo().get_param('seta_lab_url')
        return {
            'type': 'ir.actions.act_url',
            'url': seta_lab_url + '/web/login',
            'target': 'new',
        }

    