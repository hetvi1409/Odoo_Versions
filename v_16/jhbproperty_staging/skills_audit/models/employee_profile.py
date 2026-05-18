from odoo import models, fields, api, _

class ScsEmployeeProfile(models.Model):
    _name = 'scs.employee.profile'
    _description = 'Employee SCM Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', required=True)
    role_id = fields.Many2one('scs.job.role', required=True)

    requirement_ids = fields.One2many('scs.role.requirement', compute='_compute_requirements', string='Requirements', store=False)
    assessment_ids = fields.One2many('scs.assessment', 'profile_id', string='Assessments')
    training_actions_ids = fields.One2many('scs.training.action', 'training_actions_employee_profile_id', string='Training Actions', store=True)

    total_competencies = fields.Integer(compute='_compute_kpis', store=True)
    met_count = fields.Integer(compute='_compute_kpis', store=True)
    gap_count = fields.Integer(compute='_compute_kpis', store=True)
    gap_percent = fields.Float(compute='_compute_kpis', store=True)

    @api.depends('employee_id', 'role_id')
    def _compute_name(self):
        for rec in self:
            rec.name = '%s - %s' % (rec.employee_id.name or '', rec.role_id.name or '')

    @api.depends('role_id')
    def _compute_requirements(self):
        for rec in self:
            rec.requirement_ids = rec.role_id.requirement_ids

    @api.depends('assessment_ids.state', 'assessment_ids.line_ids.final_level', 'role_id.requirement_ids')
    def _compute_kpis(self):
        level_rank = {'basic':1, 'intermediate':2, 'advanced':3, 'expert':4}
        for rec in self:
            reqs = rec.role_id.requirement_ids
            rec.total_competencies = len(reqs)
            met = 0
            # Use latest done assessment if any
            assess = rec.assessment_ids.filtered(lambda a: a.state=='done')
            latest = assess and assess[-1] or False
            level_map = {}
            if latest:
                for l in latest.line_ids:
                    if l.competency_id:
                        level_map[l.competency_id.id] = l.final_level
            for r in reqs:
                final = level_map.get(r.competency_id.id)
                if final and level_rank.get(final,0) >= level_rank.get(r.required_level,0):
                    met += 1
            rec.met_count = met
            rec.gap_count = max(len(reqs) - met, 0)
            # store as fraction so widget="percentage" in views works correctly
            rec.gap_percent = (rec.gap_count / len(reqs)) if reqs else 0.0

    def action_create_assessment(self):
        self.ensure_one()
        vals = {'profile_id': self.id}
        assess = self.env['scs.assessment'].create(vals)
        assess._populate_lines_from_role()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'scs.assessment',
            'view_mode': 'form',
            'res_id': assess.id,
            'target': 'new',  # This opens the form in a popup/modal window
        }

    def action_generate_training_suggestions(self):
        self.ensure_one()
        # create suggested training actions for gaps in latest done assessment
        assessment = self.assessment_ids.filtered(lambda a: a.state=='done')
        latest = assessment and assessment[-1] or False
        if not latest:
            return True
        for line in latest.line_ids:
            if line.gap_delta > 0:
                self.env['scs.training.action'].sudo().create({
                    'employee_id': self.employee_id.id,
                    'competency_id': line.competency_id.id,
                    'training_actions_employee_profile_id': self.id,
                    'state': 'draft',
                    'name': _('Training for %s') % (line.competency_id.name,),
                    'suggested': True,
                })
        return True
