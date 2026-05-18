from odoo import api, fields, models
import json
from odoo.exceptions import ValidationError


class PmScoring(models.Model):
    _name = "pm.scoring"
    _description = "Project Scoring Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Profile Name", required=True, tracking=True)

    criterion_ids = fields.One2many(
        "pm.scoring.criterion", "scoring_id", string="Criteria"
    )

    weight_total = fields.Float(
        string="Total Weight",
        compute="_compute_weight_total",
        store=True,
    )

    method = fields.Selection(
        [
            ("weighted", "Weighted Average"),
            ("wsjf", "WSJF (Weighted Shortest Job First)"),
        ],
        string="Scoring Method",
        default="weighted",
        required=True,
    )

    @api.depends("criterion_ids.weight")
    def _compute_weight_total(self):
        for rec in self:
            rec.weight_total = sum(rec.criterion_ids.mapped("weight"))

class PmScoringCriterion(models.Model):
    _name = "pm.scoring.criterion"
    _description = "Scoring Criterion"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Criterion Name", required=True)
    code = fields.Char(string="Code")
    scoring_id = fields.Many2one("pm.scoring", string="Scoring Profile", ondelete="cascade")

    weight = fields.Float(
        string="Weight",
        help="Relative weight (0..1) if using Weighted method."
    )

    input_type = fields.Selection(
        [
            ("select", "Select"),
            ("integer", "Integer"),
            ("float", "Float"),
        ],
        string="Input Type",
        default="float",
        required=True,
    )

    options_json = fields.Text(
        string="Options (JSON)",
        help='For select input, e.g. {"High": 3, "Medium": 2, "Low": 1}'
    )
    value_ids = fields.One2many('pm.scoring.value', 'criterion_id')

class PmScoringValue(models.Model):
    _name = "pm.scoring.value"
    _description = "Scoring Value"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    project_id = fields.Many2one("project.project", string="Project", required=True, ondelete="cascade")
    criterion_id = fields.Many2one("pm.scoring.criterion", string="Criterion", required=True, ondelete="cascade")

    value_numeric = fields.Float(string="Numeric Value")
    value_option = fields.Char(string="Selected Option")

    contribution = fields.Float(
        string="Contribution",
        compute="_compute_contribution",
        store=True,
    )

    @api.depends("value_numeric", "value_option", "criterion_id.weight", "criterion_id.input_type")
    def _compute_contribution(self):
        for rec in self:
            score_val = 0.0
            if rec.criterion_id.input_type == "float":
                score_val = rec.value_numeric or 0.0
            elif rec.criterion_id.input_type == "integer":
                score_val = rec.value_numeric or 0.0
            elif rec.criterion_id.input_type == "select":
                if rec.value_option and rec.criterion_id.options_json:
                    try:
                        options = json.loads(rec.criterion_id.options_json or "{}")
                        score_val = options.get(rec.value_option, 0.0)
                    except Exception:
                        raise ValidationError("Invalid JSON in criterion options.")
            rec.contribution = (rec.criterion_id.weight or 0.0) * score_val
