from random import randint

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# the order is important
from odoo.tools.safe_eval import safe_eval

RISK_SCORES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('very_high', 'Very High'),
    ('missing', 'Incomplete'),
]


class Risk(models.Model):
    _name = 'oi_risk_management.risk'
    _description = 'Risks'
    _inherit = ['approval.record', 'mail.thread', 'mail.activity.mixin']

    @api.model
    def _create_approval_settings(self):
        return

    @api.model
    def _before_approval_states(self):
        return [('draft', 'Draft')]

    def _on_submit(self):
        str_val = ''
        if self.owner_id.id == False:
            str_val += 'Owner should be set before confirming.\n'
        if self.uncertainty == False:
            str_val += 'Uncertainty should be set before confirming.\n'
        if self.main_cause == False:
            str_val += 'Main cause should be set before confirming.\n'
        if self.consequences == False:
            str_val += 'Consequences should be set before confirming.\n'
        if self.is_assessment_complete == False:
            str_val += 'Evaluation must be done before confirming.\n'
        if str_val != '':
            raise ValidationError(str_val)

    def action_draft(self):
        super(Risk, self).action_draft()
        self.create_snapshot()

    def create_snapshot(self):
        snapshot_id = self.with_context(snapshot=True, mail_create_nolog=True, mail_notrack=True).copy({
            'original_risk_id': self.id,
            'state': 'snapshot',
            'name': '%s - %s' % (self.name, self.version),
            'version': self.version,
            'version_date': self.version_date,
            'active': False,
        })
        snapshot_id.sudo().message_follower_ids.unlink()
        self.write({
            'version': '%0.1f' % (float(self.version) + 0.1),
            'version_date': fields.Datetime.now()
        })

    @api.model
    def _after_approval_states(self):
        return [('approved', 'Approved'),
                ('snapshot', 'Snapshot'),
                ('rejected', 'Rejected')]

    snapshot_ids = fields.One2many('oi_risk_management.risk', 'original_risk_id')
    snapshots_count = fields.Integer(compute='_compute_snapshots_count')
    original_risk_id = fields.Many2one('oi_risk_management.risk', ondelete='cascade', readonly=True)

    # state = fields.Selection(selection_add=[('snapshot', 'Snapshot')])
    version = fields.Char(readonly=True, default='1.0', tracking=True, copy=False)
    version_date = fields.Datetime(readonly=True, default=fields.Datetime.now, copy=False)

    @api.depends('snapshot_ids')
    def _compute_snapshots_count(self):
        for record in self:
            record.snapshots_count = len(record.with_context(active_test=False).snapshot_ids)

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    description = fields.Text(compute='_compute_description')
    main_cause = fields.Text()
    owner_id = fields.Many2one('hr.job')
    employee_id = fields.Many2one('hr.employee')
    owner_employee_ids = fields.One2many('hr.employee', related='owner_id.employee_ids')
    target_date = fields.Date()

    @api.depends('name', 'main_cause', 'consequences')
    def _compute_description(self):
        for record in self:
            record.description = "%s: %s, due to %s, could leads to %s" % (
                record.name, record.uncertainty, record.main_cause or '(missing)', record.consequences or '(missing)',)

    uncertainty = fields.Text()
    consequences = fields.Text()

    is_board = fields.Boolean(default=False, groups='oi_risk_management.group_risk_ceo')

    activity_id = fields.Many2one('oi_risk_management.activity', required=True, ondelete='cascade')

    tag_ids = fields.Many2many('oi_risk_management.activity_tag', )
    category_id = fields.Many2one('oi_risk_management.activity_category')

    department_id = fields.Many2one('hr.department', required=True)

    # sources_ids = fields.Many2many('ir.attachment', string='Attachments')
    risk_analysis_line_ids = fields.One2many('oi_risk_management.risk_analysis_line', 'risk_id', copy=True)
    risk_evaluation_line_ids = fields.One2many('oi_risk_management.risk_evaluation_line', 'risk_id', copy=True)

    # related_risk_ids = fields.Many2many('oi_risk_management.risk', 'related_risks_rel', 'risk1', 'risk2')

    severity_line_id = fields.Many2one('oi_risk_management.risk_evaluation_line', compute='_compute_severity_line_id',
                                       store=True)
    likelihood_line_id = fields.Many2one('oi_risk_management.risk_evaluation_line',
                                         compute='_compute_likelihood_line_id', store=True)
    control_effectiveness_id = fields.Many2one('oi_risk_management.risk_criteria',
                                               domain=[('type', '=', 'control_effectiveness')])
    control_effectiveness_risk_criteria_ids = fields.Many2many('oi_risk_management.risk_criteria',
                                                               compute='_compute_control_effectiveness_risk_criteria_ids')

    # control_effectiveness_line_id = fields.Many2one('oi_risk_management.risk_evaluation_line',
    #                                                 compute='_compute_control_effectiveness_line_id', store=True)

    inherent_risk_total_score = fields.Selection(selection=RISK_SCORES, compute='_compute_inherent_risk_total_score',
                                                 store=True)
    current_risk_total_score = fields.Selection(selection=RISK_SCORES, compute='_compute_current_risk_total_score',
                                                store=True)
    residual_risk_total_score = fields.Selection(selection=RISK_SCORES, compute='_compute_residual_risk_total_score',
                                                 store=True)
    main_risk_total_score = fields.Selection(selection=RISK_SCORES, compute='_compute_main_risk_total_score',
                                             store=True)
    is_assessment_complete = fields.Boolean(compute='_compute_is_assessment_complete')

    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id.id == False:
            self.owner_id = False
            self.employee_id = False

    def _compute_control_effectiveness_risk_criteria_ids(self):
        for record in self:
            all_risk_criteria_ids = self.env['oi_risk_management.risk_criteria'].search(
                [('type', '=', 'control_effectiveness')])
            record.control_effectiveness_risk_criteria_ids = all_risk_criteria_ids

    @api.depends('severity_line_id.inherent_risk', 'severity_line_id.current_risk', 'severity_line_id.residual_risk',
                 'likelihood_line_id.inherent_risk', 'likelihood_line_id.current_risk',
                 'likelihood_line_id.residual_risk',
                 'control_effectiveness_id')
    def _compute_is_assessment_complete(self):
        to_check_fields = ['severity_line_id.inherent_risk', 'severity_line_id.current_risk',
                           'severity_line_id.residual_risk',
                           'likelihood_line_id.inherent_risk', 'likelihood_line_id.current_risk',
                           'likelihood_line_id.residual_risk',
                           'control_effectiveness_id']

        def is_complete(record):
            for field in to_check_fields:
                splits = field.split('.')
                if len(splits) == 2:
                    if record[splits[0]][splits[1]].id == False:
                        return False
                else:
                    if record[splits[0]].id == False:
                        return False
            return True

        for record in self:
            record.is_assessment_complete = is_complete(record)

    @api.depends('risk_evaluation_line_ids')
    def _compute_severity_line_id(self):
        for record in self:
            record.severity_line_id = record.risk_evaluation_line_ids.filtered(lambda line: line.type == 'severity')

    @api.depends('risk_evaluation_line_ids')
    def _compute_likelihood_line_id(self):
        for record in self:
            record.likelihood_line_id = record.risk_evaluation_line_ids.filtered(lambda line: line.type == 'likelihood')

    def _compute_risk_total_score(self, risk_type):
        for record in self:
            severity_line = record.risk_evaluation_line_ids.filtered(lambda r: r.type == 'severity')
            likelihood_line = record.risk_evaluation_line_ids.filtered(lambda r: r.type == 'likelihood')

            if len(severity_line[risk_type]) == 0 or len(likelihood_line[risk_type]) == 0:
                record[risk_type + '_total_score'] = 'missing'
                continue

            p = likelihood_line[risk_type].score
            s = severity_line[risk_type].score

            evaluation_criteria = self.env['oi_risk.asymmetric_evaluation_criteria'].search(
                [('p', '=', p), ('s', '=', s)])

            record[risk_type + '_total_score'] = evaluation_criteria.risk_type

    @api.depends('risk_evaluation_line_ids.inherent_risk')
    def _compute_inherent_risk_total_score(self):
        self._compute_risk_total_score('inherent_risk')

    @api.depends('risk_evaluation_line_ids.current_risk')
    def _compute_current_risk_total_score(self):
        self._compute_risk_total_score('current_risk')

    @api.depends('risk_evaluation_line_ids.residual_risk')
    def _compute_residual_risk_total_score(self):
        self._compute_risk_total_score('residual_risk')

    @api.depends('risk_evaluation_line_ids.inherent_risk', 'risk_evaluation_line_ids.current_risk',
                 'risk_evaluation_line_ids.residual_risk')
    def _compute_main_risk_total_score(self):
        main_risk_type = self.env['ir.config_parameter'].sudo().get_param('oi_risk_management.main_risk_type')
        for record in self:
            record.main_risk_total_score = record['%s_total_score' % (main_risk_type,)]

    @api.model
    def default_get(self, fields_list):
        res = super(Risk, self).default_get(fields_list)

        vals = [
            (0, 0, {'type': 'severity'}),
            (0, 0, {'type': 'likelihood'}),
        ]

        res.update({
            'risk_evaluation_line_ids': vals
        })

        return res

    def action_open_risk_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Risk Assessment',
            'res_model': 'oi_risk_management.risk',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('oi_risk_management.risk_form').id,
        }

    def action_open_versions(self):
        action = self.env.ref('oi_risk_management.list_of_risks_action').read()[0]
        context = safe_eval(action.get('context', '{}'))
        context.update({
            'button_edit_enabled': False,
            'active_test': False,
        })
        action.update({
            'context': context,
            'domain': [('original_risk_id', '=', self.id)],
            'display_name': _('Versions'),
        })

        return action


class RiskAnalysisLine(models.Model):
    _name = 'oi_risk_management.risk_analysis_line'
    _description = 'Risks Analysis Line'

    # Versioning
    original_analysis_line_id = fields.Many2one("oi_risk_management.risk_analysis_line",
                                                string='Original Analysis Line', readonly=True,
                                                ondelete='restrict', copy=False)
    snapshot_ids = fields.One2many('oi_risk_management.risk_analysis_line', 'original_analysis_line_id', readonly=True)
    snapshots_count = fields.Integer(compute='_compute_snapshots_count')

    @api.depends('snapshot_ids')
    def _compute_snapshots_count(self):
        for record in self:
            record.snapshots_count = len(record.snapshot_ids)

    version = fields.Char(related='risk_id.version')
    version_date = fields.Datetime(related='risk_id.version_date')

    def copy_data(self, default=None):
        default = default or {}
        if self._context.get('snapshot'):
            default['original_analysis_line_id'] = self.id
            default['active'] = False
        return super(RiskAnalysisLine, self).copy_data(default=default)

    active = fields.Boolean(default=True)
    contributing_factor = fields.Char(required=True)
    current_control_ids = fields.One2many('oi_risk_management.risk_line_current_control', 'risk_analysis_line_id',
                                          copy=True)
    current_control_str = fields.Text(compute='_compute_current_control_str', string='Current Controls')

    risk_treatment_ids = fields.One2many('oi_risk_management.risk_treatment', 'risk_analysis_line_id', copy=True)
    risk_treatment_str = fields.Text(compute='_compute_risk_treatment_str', string='Treatments')

    line_no = fields.Integer(compute='_compute_line_no')

    can_have_owner = fields.Boolean(compute='_compute_can_have_owner')
    risk_id = fields.Many2one('oi_risk_management.risk', ondelete='cascade')
    risk_owner_id = fields.Many2one('hr.job', related='risk_id.owner_id')
    risk_employee_id = fields.Many2one('hr.job', related='risk_id.employee_id')
    risk_state = fields.Selection(related='risk_id.state')

    @api.depends('current_control_ids')
    def _compute_current_control_str(self):
        for record in self:
            if len(record.current_control_ids) != 0:
                record.current_control_str = '\n'.join(
                    ['- %s' % current_control_id.name for current_control_id in record.current_control_ids])
            else:
                record.current_control_str = 'None'

    @api.depends('risk_treatment_ids')
    def _compute_risk_treatment_str(self):
        for record in self:
            if len(record.risk_treatment_ids) != 0:
                record.risk_treatment_str = '\n'.join(
                    ['- %s (%s)' % (risk_treatment_id.name, dict(risk_treatment_id._fields['status'].selection).get(risk_treatment_id.status),) for risk_treatment_id in
                     record.risk_treatment_ids])
            else:
                record.risk_treatment_str = 'None'

    def _compute_line_no(self):
        if self[0].id:
            for record in self:
                if record.id:
                    analysis_line = record.risk_id.risk_analysis_line_ids
                    record['line_no'] = analysis_line.ids.index(record.id) + 1
        else:
            for record in self:
                record['line_no'] = len(record.risk_id.risk_analysis_line_ids)

    @api.depends('risk_id')
    def _compute_can_have_owner(self):
        for record in self:
            record.can_have_owner = self.env['ir.config_parameter'].sudo().get_param(
                'oi_risk_management.do_risk_treatments_have_owner')


class RiskLineCurrentControl(models.Model):
    _name = 'oi_risk_management.risk_line_current_control'
    _description = 'Risk Line Current Control'

    # Versioning
    original_line_current_control_id = fields.Many2one("oi_risk_management.risk_line_current_control",
                                                       string='Original Current Control', readonly=True,
                                                       ondelete='restrict', copy=False)
    snapshot_ids = fields.One2many('oi_risk_management.risk_line_current_control', 'original_line_current_control_id',
                                   readonly=True)
    snapshots_count = fields.Integer(compute='_compute_snapshots_count')

    @api.depends('snapshot_ids')
    def _compute_snapshots_count(self):
        for record in self:
            record.snapshots_count = len(record.snapshot_ids)

    version = fields.Char(related='risk_analysis_line_id.risk_id.version')
    version_date = fields.Datetime(related='risk_analysis_line_id.risk_id.version_date')

    def copy_data(self, default=None):
        default = default or {}
        if self._context.get('snapshot'):
            default['original_line_current_control_id'] = self.id
            default['active'] = False
        return super(RiskLineCurrentControl, self).copy_data(default=default)

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, string='Details')
    risk_analysis_line_id = fields.Many2one('oi_risk_management.risk_analysis_line', required=True, ondelete='cascade')
    risk_id = fields.Many2one('oi_risk_management.risk', related='risk_analysis_line_id.risk_id')


class RiskTreatment(models.Model):
    _name = 'oi_risk_management.risk_treatment'
    _description = 'Risk Treatment'

    risk_state = fields.Selection(related='risk_id.state')

    # Versioning
    original_treatment_id = fields.Many2one("oi_risk_management.risk_treatment",
                                            string='Original Treatment', readonly=True,
                                            ondelete='restrict', copy=False)
    snapshot_ids = fields.One2many('oi_risk_management.risk_treatment', 'original_treatment_id',
                                   readonly=True)
    snapshots_count = fields.Integer(compute='_compute_snapshots_count')

    @api.depends('snapshot_ids')
    def _compute_snapshots_count(self):
        for record in self:
            record.snapshots_count = len(record.snapshot_ids)

    version = fields.Char(related='risk_id.version')
    version_date = fields.Datetime(related='risk_id.version_date')

    def copy_data(self, default=None):
        default = default or {}
        if self._context.get('snapshot'):
            default['original_treatment_id'] = self.id
            default['active'] = False
        return super(RiskTreatment, self).copy_data(default=default)

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, string='Details')
    target_date = fields.Date(required=True)
    status = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('close', 'Close'),
    ], default='open', required=True)
    owner_id = fields.Many2one('hr.job')
    comments = fields.Char()
    is_overdue = fields.Boolean(compute='_compute_is_overdue')
    is_overdue_str = fields.Char(compute='_compute_is_overdue_str')

    risk_analysis_line_id = fields.Many2one('oi_risk_management.risk_analysis_line', required=True, ondelete='cascade')

    risk_id = fields.Many2one('oi_risk_management.risk', related='risk_analysis_line_id.risk_id', store=True)
    risk_description = fields.Text(related='risk_id.description')
    risk_owner_id = fields.Many2one('hr.job', related='risk_id.owner_id')
    risk_employee_id = fields.Many2one('hr.job', related='risk_id.employee_id')
    risk_inherent_risk_total_score = fields.Selection(selection=RISK_SCORES,
                                                      related='risk_id.inherent_risk_total_score')
    risk_current_risk_total_score = fields.Selection(selection=RISK_SCORES, related='risk_id.current_risk_total_score')
    risk_residual_risk_total_score = fields.Selection(selection=RISK_SCORES,
                                                      related='risk_id.residual_risk_total_score')

    department_id = fields.Many2one('hr.department', related='risk_id.department_id', store=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.depends('target_date')
    def _compute_is_overdue(self):
        for record in self:
            record.is_overdue = record.status != 'close' and record.target_date < fields.Date.today()

    @api.depends('target_date')
    def _compute_is_overdue_str(self):
        for record in self:
            if record.is_overdue:
                record.is_overdue_str = 'Over due'
            else:
                record.is_overdue_str = ''

    def action_change_status(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Risk Treatment',
            'res_model': 'oi_risk_management.risk_treatment',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [[self.env.ref('oi_risk_management.risk_treatment_form').id, 'form']],
            'target': 'new',
        }


class RiskEvaluationLine(models.Model):
    _name = 'oi_risk_management.risk_evaluation_line'
    _description = 'Risks Evaluation Line'

    # Versioning
    original_evaluation_line_id = fields.Many2one("oi_risk_management.risk_evaluation_line",
                                                  string='Original Evaluation Line', readonly=True,
                                                  ondelete='restrict', copy=False)
    snapshot_ids = fields.One2many('oi_risk_management.risk_evaluation_line', 'original_evaluation_line_id',
                                   readonly=True)
    snapshots_count = fields.Integer(compute='_compute_snapshots_count')

    @api.depends('snapshot_ids')
    def _compute_snapshots_count(self):
        for record in self:
            record.snapshots_count = len(record.snapshot_ids)

    version = fields.Char(related='risk_id.version')
    version_date = fields.Datetime(related='risk_id.version_date')

    def copy_data(self, default=None):
        default = default or {}
        if self._context.get('snapshot'):
            default['original_evaluation_line_id'] = self.id
            default['active'] = False
        return super(RiskEvaluationLine, self).copy_data(default=default)

    active = fields.Boolean(default=True)
    type = fields.Selection([
        ('severity', 'Severity/Impact'),
        ('likelihood', 'Likelihood/Probability'),
    ], required=True)
    risk_id = fields.Many2one('oi_risk_management.risk', ondelete='cascade')

    risk_criteria_ids = fields.Many2many('oi_risk_management.risk_criteria', compute='_compute_risk_criteria_ids')

    inherent_risk = fields.Many2one('oi_risk_management.risk_criteria')
    inherent_risk_justification = fields.Text()

    current_risk = fields.Many2one('oi_risk_management.risk_criteria')
    current_risk_justification = fields.Text()

    residual_risk = fields.Many2one('oi_risk_management.risk_criteria')
    residual_risk_justification = fields.Text()

    @api.depends('type')
    def _compute_risk_criteria_ids(self):
        for record in self:
            all_risk_criteria_ids = self.env['oi_risk_management.risk_criteria'].search([('type', '=', record.type)])
            record.risk_criteria_ids = all_risk_criteria_ids


class RiskCriteria(models.Model):
    _name = 'oi_risk_management.risk_criteria'
    _description = 'Risks Analysis Criteria'
    _order = 'score desc'
    _rec_name = 'score'

    type = fields.Selection([
        ('severity', 'Severity'),
        ('likelihood', 'Likelihood'),
        ('control_effectiveness', 'Control Effectiveness'),
    ])
    name = fields.Char(string='Rating', required=True)
    score = fields.Integer(required=True)
    color = fields.Integer(default=lambda self: self._default_color())

    # for severity
    ehs = fields.Char(string='EHS')
    value = fields.Char(string='Cost')
    reputation = fields.Char()

    # for likelihood
    percentage = fields.Char()
    frequency = fields.Char()

    # for control effectiveness
    description = fields.Text()

    def _default_color(self):
        return randint(1, 11)

    def name_get(self):
        return [(criteria.id, "%s - %s" % (criteria.score, criteria.name,)) for criteria in self]
        # list = []
        # for record in self:
        #     if record.type == 'severity':
        #         list.append((record.id, "%s - %s - %s - %s - %s" % (
        #         record.score, record.name, record.ehs, record.value, record.reputation,)))
        #     if record.type == 'likelihood':
        #         list.append((record.id,
        #                      "%s - %s - %s - %s" % (record.score, record.name, record.percentage, record.frequency,)))
        #     if record.type == 'control_effectiveness':
        #         list.append((record.id, "%s - %s - %s" % (record.score, record.name, record.description,)))
        # 
        # return list
