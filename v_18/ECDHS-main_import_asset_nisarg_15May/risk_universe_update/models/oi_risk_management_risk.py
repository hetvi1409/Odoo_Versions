from odoo import models, fields, api, _


class Risk(models.Model):
    _inherit = 'oi_risk_management.risk'

    oi_risk_type = fields.Selection(
        [('strategic', 'Strategic Risk Register'), ('operational', 'Operational Risk Register'),
         ('fraud', 'Fraud Risk Register'), ('project', 'Project Risk Register'), ('business', 'Business Unit Risks'),
         ('process', 'Process Risks'),('emerging','Emerging Risk Register')],string='Type', related="risk_type_id.oi_risk_type")
    risk_type_id = fields.Many2one('risk.type')


    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'oi_risk_type' in fields_list:
            oi_risk_type =  self._context.get('default_oi_risk_type')
            if oi_risk_type == 'strategic':
                defaults['risk_type_id'] = self.env.ref('risk_universe_update.risk_type_strategic').id
            if oi_risk_type == 'operational':
                defaults['risk_type_id'] = self.env.ref('risk_universe_update.risk_type_operational').id
            if oi_risk_type == 'fraud':
                defaults['risk_type_id'] = self.env.ref('risk_universe_update.risk_type_fraud').id
            if oi_risk_type == 'project':
                defaults['risk_type_id'] = self.env.ref('risk_universe_update.risk_type_project').id
            if oi_risk_type == 'business':
                defaults['risk_type_id'] = self.env.ref('risk_universe_update.risk_type_business').id
            if oi_risk_type == 'process':
                defaults['risk_type_id'] = self.env.ref('risk_universe_update.risk_type_process').id
            if oi_risk_type == 'emerging':
                defaults['risk_type_id'] = self.env.ref('risk_universe_update.risk_type_emerging').id
        return defaults
