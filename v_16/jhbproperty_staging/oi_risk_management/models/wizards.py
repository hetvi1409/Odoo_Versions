from odoo import models, fields, api

class ListOfRisksDepartmentWizard(models.TransientModel):
    _name = 'oi_risk.list_of_risks_department_wizard'
    _description = 'List of Risks Department Wizard'

    department_id = fields.Many2one('hr.department')

    def generate(self):
        return {
            'name': '%s List of Risks' % (self.department_id.name,),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form,graph,pivot,activity",
            "res_model": 'oi_risk_management.risk',
            'domain': [('department_id', '=', self.department_id.id)],
        }


class RiskDashboardDepartmentWizard(models.TransientModel):
    _name = 'oi_risk.risk_dashboard_department_wizard'
    _description = 'Risk Dashboard Department Wizard'

    department_id = fields.Many2one('hr.department')

    def generate(self):
        return {
            'name': '%s Risk Dashboard' % (self.department_id.name,),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form,graph,pivot,activity",
            "res_model": 'oi_risk_management.risk_treatment',
            'domain': [('department_id', '=', self.department_id.id)],
            'context': {'search_default_risk': 1},
        }


class RiskProfileWizard(models.TransientModel):
    _name = 'oi_risk.risk_profile_wizard'
    _description = 'Risk Profile Configuration'

    group_class = fields.Selection([
        ('board', 'Board'),
        ('exco', 'Exco'),
        ('department', 'Department'),
    ], default='department', required=True)
    department_id = fields.Many2one('hr.department')
    evaluation_risk_type = fields.Selection([
        ('inherent_risk', 'Inherent Risk'),
        ('current_risk', 'Current Risk'),
        ('residual_risk', 'Residual Risk'),
    ])

    @api.model
    def edit(self):
        return {
            'name': 'Generate a Risk Profile',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'oi_risk.risk_profile_wizard',
            'view_id': self.env.ref('oi_risk_management.risk_profile_wizard').id,
            'views': [(self.env.ref('oi_risk_management.risk_profile_wizard').id, 'form')],
            'target': 'new',
            'context': {}
        }

    def get_domain(self, evaluation_risk_type, department_id,group_class):
        active_id = self._context.get('active_id')
        record = self
        all_evaluation_risk_type = []
        
        domain = [('control_effectiveness_id', '!=', False)]
        
        if not evaluation_risk_type:
            all_evaluation_risk_type = ['inherent_risk','current_risk','residual_risk']
            
        if evaluation_risk_type:
            domain += [('severity_line_id.%s' % (evaluation_risk_type,), '!=', False),('likelihood_line_id.%s' % (evaluation_risk_type,), '!=', False)]
            
        elif all_evaluation_risk_type:
            domain += ['|','|',]
            for eval_risk_type in all_evaluation_risk_type:
                domain += ['&',('severity_line_id.%s' % (eval_risk_type,), '!=', False),('likelihood_line_id.%s' % (eval_risk_type,), '!=', False)]
            
        if department_id:
            domain += [('department_id', '=', department_id)]
        elif group_class == 'exco':
            
            if evaluation_risk_type:
                domain += [("%s_total_score" % (evaluation_risk_type), 'in', ['very_high', 'high'])]
                
            elif all_evaluation_risk_type:
                domain += ['|','|',]
                
                for eval_risk_type in all_evaluation_risk_type:
                    domain += [("%s_total_score" % (eval_risk_type), 'in', ['very_high', 'high'])]
                    
        elif group_class == 'board':
            domain += [('is_board', '=', True)]

        return domain
           
    def get_evaluation_system(self, evaluation_risk_type,department_id,group_class):
        active_id = self._context.get('active_id')
        record = self
        
        return_values = {
            'evaluation_system': {},
            'risk_ids': [],
            'evaluation_risk_type': evaluation_risk_type,
            'evaluation_risk_type_string': dict(self._fields['evaluation_risk_type'].selection).get(evaluation_risk_type),
            }
        
        evaluation_type_names = {
            'very_high': self.env['oi_risk.asymmetric_evaluation_criteria'].search([]).filtered(
                lambda risk: risk.risk_type == 'very_high'),
            'high': self.env['oi_risk.asymmetric_evaluation_criteria'].search([]).filtered(
                lambda risk: risk.risk_type == 'high'),
            'medium': self.env['oi_risk.asymmetric_evaluation_criteria'].search([]).filtered(
                lambda risk: risk.risk_type == 'medium'),
            'low': self.env['oi_risk.asymmetric_evaluation_criteria'].search([]).filtered(
                lambda risk: risk.risk_type == 'low'),
        }

        domain = self.get_domain(evaluation_risk_type,department_id, group_class)
        risk_ids = self.env['oi_risk_management.risk'].search(domain)        
        return_values['risk_ids'] = risk_ids.ids or []

        for eval_type in evaluation_type_names:
            for evaluation_criteria in evaluation_type_names[eval_type]:
                p = evaluation_criteria.p
                s = evaluation_criteria.s

                return_values['evaluation_system'][evaluation_criteria.name] = {
                    'type': eval_type,
                    'risk_ids': risk_ids.filtered(
                        lambda risk: risk.severity_line_id[evaluation_risk_type].score == s and
                                     risk.likelihood_line_id[evaluation_risk_type].score == p
                    ).ids or [],
                }
        
        return return_values
                  
    def _prepare_qcontext(self):
        active_id = self._context.get('active_id')
        record = self
        record.ensure_one()
        
        domain = self.get_domain(record.evaluation_risk_type,record.department_id.id, record.group_class)

        risk_ids = self.env['oi_risk_management.risk'].search(domain).mapped('id')
        return_values = {
            'wizard': {
                'group_class' : record.group_class,
                'department_id': record.department_id.id,
                'department': record.department_id.name,
                'evaluation_risk_type' : record.evaluation_risk_type,
                'risk_ids': risk_ids,
                'risk_action_id': self.env.ref('oi_risk_management.risks_view').id,
            },
            
        }

        return return_values

    def generate(self):
        datas = self._prepare_qcontext()
        
        return self.env.ref('oi_risk_management.report_risk_profile').report_action(self, data=datas)
