from odoo import models, fields, api
from werkzeug import urls


class RiskRegister(models.Model):
    _name = 'risk.register'
    _description = 'Risk Register'
    _inherit = ['approval.record', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Register Name", required=True)
    # Financial Year
    fy_start_date = fields.Date(string="Financial Year Start")
    fy_end_date = fields.Date(string="Financial Year End")
    # Project
    project_name = fields.Char(string="Project Name")
    project_amount = fields.Char(string="Project Amount")
    project_start_date = fields.Date(string="Project Start Date")
    project_end_date = fields.Date(string="Project End Date")
    line_ids = fields.One2many(
        'risk.register.line',
        'register_id',
        string="Risk Lines"
    )
    risk_register_state = fields.Selection([('draft', 'Draft'), ('prepared', 'Prepared'),
                                            ('reviewed', 'Reviewed'), ('approved', 'Approved'),
                                            ('reverted', 'Reverted'),
                                            ('rejected', 'Rejected')],
                                           string="State", copy=False, default="draft")

    def _get_preparer_id(self):
        """Get the ID"""
        return int(self.env['ir.config_parameter'].sudo().get_param('oi_risk_workflow.preparer_id')) if self.env[
            'ir.config_parameter'].sudo().get_param('oi_risk_workflow.preparer_id') else False

    def _get_reviewer_id(self):
        """Get the ID of the currently logged-in employee"""
        return int(self.env['ir.config_parameter'].sudo().get_param('oi_risk_workflow.reviewer_id')) if self.env[
            'ir.config_parameter'].sudo().get_param('oi_risk_workflow.reviewer_id') else False

    def _get_approver_id(self):
        """Get the ID of the currently logged-in employee"""
        return int(self.env['ir.config_parameter'].sudo().get_param('oi_risk_workflow.approver_id')) if self.env[
            'ir.config_parameter'].sudo().get_param('oi_risk_workflow.approver_id') else False

    preparer_id = fields.Many2one('res.users', string="Preparer", default=_get_preparer_id)
    reviewer_id = fields.Many2one('res.users', string="Reviewer", default=_get_reviewer_id)
    approver_id = fields.Many2one('res.users', string="Approver", default=_get_approver_id)
    feedback = fields.Char(string="Complaince Reverts/ Review Notes", tracking=True)
    can_edit = fields.Boolean(
        string="Can Edit",
        compute="_compute_can_edit", default=True
    )

    def _compute_can_edit(self):
        current_user = self.env.user
        for record in self:
            # Default → cannot edit
            record.can_edit = False

            # Approved → nobody can edit
            if record.risk_register_state in ['approved', 'rejected']:
                continue

            # Draft → only Preparer
            if record.risk_register_state == 'draft' and current_user == record.preparer_id:
                record.can_edit = True

            # Preparer Stage → Reviewer 1
            elif record.risk_register_state == 'prepared' and current_user == record.reviewer_id:
                record.can_edit = True

            # Second Reviewer Stage → Approver
            elif record.risk_register_state == 'reviewed' and current_user == record.approver_id:
                record.can_edit = True

    def action_risk_register_prepare(self):
        self.risk_register_state = 'prepared'

    def action_risk_register_reviewed(self):
        self.risk_register_state = 'reviewed'

    def action_risk_register_approved(self):
        self.risk_register_state = 'approved'

    def action_risk_register_rejected(self):
        self.risk_register_state = 'rejected'

    def action_register_revert(self):
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'risk.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_risk_register_details': self.id,
                'default_oi_risk_register_risk': self.name,
                'default_risk_type': 'register',
            },
        }

    def action_view_records(self):
        """Method for view records"""
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'audit.revert',
            'domain': [('res_id', '=', self.id), ('res_model', '=', self._name)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=oi_risk_management.risk&view_type=form' % self.id)

        return Urls


class RiskRegisterLine(models.Model):
    _name = 'risk.register.line'
    _description = 'Risk Register Line'
    _order = 'sequence'

    register_id = fields.Many2one(
        'risk.register',
        string="Risk Register",
        ondelete="cascade"
    )
    sequence = fields.Integer(string="Risk No", default=1)
    risk_description = fields.Char(string="Risk Description")
    probability_id = fields.Many2one('risk.register.criteria', string="P (Probability)")
    impact_id = fields.Many2one(
        'risk.register.criteria',
        string="I (Impact)"
    )
    inherent_risk = fields.Integer(
        string="Inherent Risk",
        compute="_compute_inherent_risk",
        store=True
    )
    controls = fields.Text(string="Controls")
    control_effectiveness_id = fields.Many2one(
        'risk.register.control',
        string="Control Effectiveness"
    )
    residual_risk = fields.Many2one('risk.register.rating', string="Residual Risk")
    action_plans = fields.Char(string="Action Plans")
    matrix_html = fields.Html(string="Risk Matrix", compute="_compute_matrix_html", sanitize=False)
    control_effectiveness_html = fields.Html(string="Control Effectiveness Reference",
                                             compute="_compute_control_effectiveness_html", sanitize=False)
    residual_risk_html = fields.Html(string="Residual Risk Rating Reference", compute="_compute_residual_risk_html",
                                     sanitize=False)

    @api.depends()
    def _compute_matrix_html(self):
        matrix = """
            <style>
            .risk-table{
                border-collapse: collapse;
                width:100%;
                text-align:center;
            }
            .risk-table td,.risk-table th{
                border:1px solid #999;
                padding:6px;
            }

            .green{background:#00b050;color:white;}
            .yellow{background:#ffff00;}
            .red{background:#ff0000;color:white;}
            </style>

            <table class="risk-table">
            <tr>
                <th rowspan="2">Probability</th>
                <th colspan="5">Impact</th>
            </tr>
            <tr>
                <th>1 Insignificant</th>
                <th>2 Minor</th>
                <th>3 Moderate</th>
                <th>4 Major</th>
                <th>5 Critical</th>
            </tr>

            <tr>
                <td>1 Rare</td>
                <td class="green">1</td>
                <td class="green">2</td>
                <td class="green">3</td>
                <td class="green">4</td>
                <td class="green">5</td>
            </tr>

            <tr>
                <td>2 Possible</td>
                <td class="green">2</td>
                <td class="green">4</td>
                <td class="green">6</td>
                <td class="yellow">8</td>
                <td class="yellow">10</td>
            </tr>

            <tr>
                <td>3 Moderate</td>
                <td class="green">3</td>
                <td class="green">6</td>
                <td class="yellow">9</td>
                <td class="yellow">12</td>
                <td class="red">15</td>
            </tr>

            <tr>
                <td>4 Likely</td>
                <td class="green">4</td>
                <td class="yellow">8</td>
                <td class="yellow">12</td>
                <td class="red">16</td>
                <td class="red">20</td>
            </tr>

            <tr>
                <td>5 Certain</td>
                <td class="green">5</td>
                <td class="yellow">10</td>
                <td class="red">15</td>
                <td class="red">20</td>
                <td class="red">25</td>
            </tr>

            </table>
            """

        for rec in self:
            rec.matrix_html = matrix

    @api.depends()
    def _compute_control_effectiveness_html(self):

        table = """
        <style>
        .control-table{
            border-collapse: collapse;
            width:100%;
        }

        .control-table th,.control-table td{
            border:1px solid #999;
            padding:8px;
        }

        .header{
            background:#d9d9d9;
            font-weight:bold;
        }

        .verygood{background:#c6efce;}
        .good{background:#d9ead3;}
        .satisfactory{background:#fff2cc;}
        .weak{background:#f4cccc;}
        .unsatisfactory{background:#ea9999;}

        </style>

        <table class="control-table">

        <tr class="header">
            <th>Control Level</th>
            <th>Description</th>
            <th>Effectiveness</th>
        </tr>

        <tr class="verygood">
            <td><b>Very Good</b></td>
            <td>Risk exposure is effectively controlled and managed</td>
            <td align="center"><b>90%</b></td>
        </tr>

        <tr class="good">
            <td><b>Good</b></td>
            <td>Majority of risk exposures is effectively controlled and managed</td>
            <td align="center"><b>70%</b></td>
        </tr>

        <tr class="satisfactory">
            <td><b>Satisfactory</b></td>
            <td>There is room for some improvement in the control system</td>
            <td align="center"><b>45%</b></td>
        </tr>

        <tr class="weak">
            <td><b>Weak</b></td>
            <td>Some of the risk exposures appears to be controlled, but there are major deficiencies</td>
            <td align="center"><b>20%</b></td>
        </tr>

        <tr class="unsatisfactory">
            <td><b>Unsatisfactory</b></td>
            <td>Control measures are ineffective</td>
            <td align="center"><b>10%</b></td>
        </tr>

        </table>
        """

        for rec in self:
            rec.control_effectiveness_html = table

    @api.depends()
    def _compute_residual_risk_html(self):

        table = """
            <style>

            .residual-table{
                border-collapse: collapse;
                width:100%;
            }

            .residual-table th,.residual-table td{
                border:1px solid #999;
                padding:8px;
            }

            .header{
                background:#d9d9d9;
                font-weight:bold;
                text-align:center;
            }

            .critical{
                background:#ff0000;
                color:white;
            }

            .moderate{
                background:#ffff00;
            }

            .insignificant{
                background:#00b050;
                color:white;
            }

            </style>

            <table class="residual-table">

            <tr class="header">
                <th colspan="3">Residual Risk Rating</th>
            </tr>

            <tr class="critical">
                <td><b>Critical</b></td>
                <td>Management should reduce residual risk exposure to an acceptable level</td>
                <td align="center"><b>15 - 25</b></td>
            </tr>

            <tr class="moderate">
                <td><b>Moderate</b></td>
                <td>Management should monitor the risk exposure and related control effectiveness</td>
                <td align="center"><b>8 to 14</b></td>
            </tr>

            <tr class="insignificant">
                <td><b>Insignificant</b></td>
                <td>The residual risk exposure is acceptable to the Municipality</td>
                <td align="center"><b>1 to 7</b></td>
            </tr>

            </table>
            """

        for rec in self:
            rec.residual_risk_html = table

    @api.depends('probability_id', 'impact_id')
    def _compute_inherent_risk(self):
        for rec in self:
            p = rec.probability_id.value if rec.probability_id else 0
            i = rec.impact_id.value if rec.impact_id else 0
            rec.inherent_risk = p * i


class RiskRegisterCriteria(models.Model):
    _name = 'risk.register.criteria'
    _description = 'Risk Criteria'
    _rec_name = 'value'

    name = fields.Char(string="Criteria")
    value = fields.Integer(string="Value")


class RiskRegisterControl(models.Model):
    _name = 'risk.register.control'
    _description = 'Control Effectiveness'
    _rec_name = 'effectiveness_percentage'

    name = fields.Char(string="Control Level")
    description = fields.Text(string="Description")
    effectiveness_percentage = fields.Char(string="Effectiveness %")


class RiskRegisterRating(models.Model):
    _name = 'risk.register.rating'
    _description = 'Residual Risk Rating'
    _rec_name = 'value'
    _order = 'value asc'

    name = fields.Char(string="Rating")
    description = fields.Text(string="Description")
    value = fields.Integer(string="Value")
    range_from = fields.Integer()
    range_to = fields.Integer()
