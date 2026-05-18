import os
import re
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from markupsafe import Markup, escape

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


PROGRAMME_FALLBACK = {
    "1": "Administration",
    "2": "Integrated Human Settlements Development",
    "3": "Housing Development",
    "4": "Housing Asset Management",
}

SUB_PROGRAMME_FALLBACK = {
    "1.1": "Executive Leadership",
    "1.2": "Corporate Governance and Risk Management",
    "1.3": "Financial Management",
    "1.4": "Strategic Management and ICT",
    "1.5": "Human Resources and Legal Services",
    "2.1": "Research and Policy Development",
    "2.2": "Human Settlements Delivery Planning",
    "2.3": "Capacity Building and Municipal Support",
    "3.1": "Beneficiary Management and Social Facilitation",
    "3.2": "Housing Programmes",
    "3.3": "Project Management and Grant Services",
    "4.1": "Sales, Transfer and Asset Management",
    "4.2": "Land Acquisition and Tenure Services",
    "4.3": "Social and Rental Housing",
}

MEASUREMENT_TYPE_SELECTION = [
    ("number", "Number"),
    ("percentage", "Percentage"),
    ("date", "Date"),
    ("boolean", "Yes/No"),
    ("milestone", "Milestone"),
    ("text", "Text"),
]

AGGREGATION_RULE_SELECTION = [
    ("sum", "Sum (Cumulative)"),
    ("count", "Count Submissions"),
    ("latest", "Latest Submission"),
    ("max", "Maximum / Latest Date"),
    ("min", "Minimum / Earliest Date"),
    ("average", "Average"),
    ("any", "Any Yes"),
    ("all", "All Yes"),
    ("standalone", "Per Period (Non-Cumulative)"),
]

TARGET_STATUS_SELECTION = [
    ("unknown", "No Target"),
    ("behind", "Not-Achieved"),
    ("met", "Achieved Target"),
    ("exceeded", "Exceeded Target"),
]

COMPARISON_DIRECTION_SELECTION = [
    ("higher", "Higher is Better"),
    ("lower", "Lower is Better"),
    ("exact", "Exact Match"),
]


def _slugify_for_path(value):
    text = (value or "unknown").strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "_", text)
    return text[:120] or "unknown"


def _open_action(self, xmlid, domain):
    self.ensure_one()
    action = self.env.ref(xmlid).sudo().read()[0]
    action["domain"] = domain
    return action


def _fiscal_year_label(fiscal_year):
    return fiscal_year.name or fiscal_year.display_name if fiscal_year else ""


def _text_value(value):
    if value in (None, False):
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _parse_number(value):
    text = _text_value(value)
    if not text:
        return None
    normalized = re.sub(r"[,%\s]", "", text)
    try:
        return float(normalized)
    except (TypeError, ValueError):
        return None


def _extract_number_unit(value):
    text = _text_value(value)
    if not text:
        return None
    match = re.match(r"^\s*[-+]?\d+(?:[.,]\d+)?\s*([a-zA-Z][a-zA-Z0-9 _/%-]*)\s*$", text)
    if not match:
        return None
    return _text_value(match.group(1))


def _parse_date_value(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = _text_value(value)
    if not text:
        return None

    for format_string in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(text, format_string).date()
        except ValueError:
            continue

    try:
        return fields.Date.to_date(text)
    except Exception:
        return None


def _parse_boolean_value(value):
    text = _text_value(value).lower()
    if not text:
        return None
    if text in {"1", "true", "yes", "y", "achieved", "done", "completed"}:
        return True
    if text in {"0", "false", "no", "n", "not achieved", "pending", "not done"}:
        return False
    return None


def _format_number(value):
    if value is None:
        return "-"

    # Try to parse numeric value from string (handles pre-formatted values like "15 days")
    parsed = _parse_number(value) if isinstance(value, str) else value

    # If parsing failed and it's a string, return as-is (might be pre-formatted)
    if parsed is None:
        text = _text_value(value)
        return text if text else "-"

    # Format the numeric value
    try:
        if float(parsed).is_integer():
            return str(int(parsed))
        return ("%.2f" % parsed).rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        # Fallback: return text representation
        return _text_value(value) or "-"


def _format_value_for_type(value, measurement_type):
    if value in (None, False, ""):
        return "-"

    try:
        if measurement_type in ("number", "percentage"):
            formatted = _format_number(value)
            return f"{formatted}%" if measurement_type == "percentage" and formatted != "-" else formatted
        if measurement_type == "date":
            parsed_date = _parse_date_value(value)
            return parsed_date.strftime("%d/%m/%Y") if parsed_date else _text_value(value) or "-"
        if measurement_type == "boolean":
            parsed_boolean = _parse_boolean_value(value) if not isinstance(value, bool) else value
            if parsed_boolean is None:
                return _text_value(value) or "-"
            return "Yes" if parsed_boolean else "No"
        return _text_value(value) or "-"
    except Exception:
        # Graceful fallback for any parsing errors
        return _text_value(value) or "-"


def _normalize_compare_text(value):
    return re.sub(r"\s+", " ", _text_value(value)).strip().lower()


def _default_aggregation_rule(measurement_type):
    defaults = {
        "number": "sum",
        "percentage": "average",
        "date": "latest",
        "boolean": "latest",
        "milestone": "latest",
        "text": "latest",
    }
    return defaults.get(measurement_type or "text", "latest")


def _default_comparison_direction(measurement_type):
    defaults = {
        "number": "higher",
        "percentage": "higher",
        "date": "lower",
        "boolean": "exact",
        "milestone": "exact",
        "text": "exact",
    }
    return defaults.get(measurement_type or "text", "exact")


def _validate_value_for_measurement_type(value, measurement_type, field_label):
    text = _text_value(value)
    if not text:
        return

    # Allow explicit placeholders when no target is intentionally set.
    if text.lower() in {"-", "n/a", "na", "not applicable", "none"}:
        return

    if measurement_type in ("number", "percentage"):
        if _parse_number(text) is None:
            raise ValidationError(
                f"{field_label} must be numeric for this indicator type. "
                "Examples: 30, 95, 95%."
            )
        return

    if measurement_type == "date":
        if _parse_date_value(text) is None:
            raise ValidationError(
                f"{field_label} must be a valid date for this indicator type. "
                "Examples: 2026-02-28 or 28/02/2026."
            )
        return

    if measurement_type == "boolean":
        if _parse_boolean_value(text) is None:
            raise ValidationError(
                f"{field_label} must be a yes/no value for this indicator type. "
                "Examples: yes, no, true, false, 1, 0."
            )
        return


def _build_target_value_guidance_html(measurement_type, measurement_unit=""):
    measurement_type = measurement_type or "text"
    unit = _text_value(measurement_unit)
    if measurement_type == "number":
        unit_hint = f" Unit (if applicable): <b>{escape(unit)}</b>." if unit else ""
        return (
            "<p class='text-muted'>"
            "Enter a numeric target only (no words in the value field). "
            "Examples: <b>30</b>, <b>1250</b>, <b>12.5</b>."
            f"{unit_hint}</p>"
        )
    if measurement_type == "percentage":
        return (
            "<p class='text-muted'>"
            "Enter a numeric percentage target. "
            "Examples: <b>87.5</b>, <b>100</b>, <b>95%</b>."
            "</p>"
        )
    if measurement_type == "date":
        return (
            "<p class='text-muted'>"
            "Enter a date target. Recommended backend format: <b>YYYY-MM-DD</b> "
            "(example: <b>2026-04-25</b>). "
            "Also accepted: <b>25/04/2026</b>, <b>25-04-2026</b>, <b>25 Apr 2026</b>."
            "</p>"
        )
    if measurement_type == "boolean":
        return (
            "<p class='text-muted'>"
            "Enter a yes/no target. "
            "Accepted values: <b>yes</b>, <b>no</b>, <b>true</b>, <b>false</b>, <b>1</b>, <b>0</b>."
            "</p>"
        )
    if measurement_type == "milestone":
        return (
            "<p class='text-muted'>"
            "Enter the exact milestone text expected. "
            "Example: <b>Phase 1 Complete</b>."
            "</p>"
        )
    return (
        "<p class='text-muted'>"
        "Enter descriptive text target. "
        "Example: <b>Policy approved and communicated</b>."
        "</p>"
    )


class ResUsers(models.Model):
    _inherit = "res.users"
    _description = "Users (OPMS Group Flags Extension)"

    opms_is_submissions_user = fields.Boolean(
        string="OPMS Submissions Users",
        compute="_compute_opms_group_flags",
        inverse="_inverse_opms_is_submissions_user",
    )
    opms_is_manager = fields.Boolean(
        string="OPMS Managers",
        compute="_compute_opms_group_flags",
        inverse="_inverse_opms_is_manager",
    )

    @api.depends("groups_id")
    def _compute_opms_group_flags(self):
        submissions_group = self.env.ref("opms_ecdhs.group_opms_submissions_user", raise_if_not_found=False)
        managers_group = self.env.ref("opms_ecdhs.group_opms_manager", raise_if_not_found=False)
        submissions_group_id = submissions_group.id if submissions_group else 0
        managers_group_id = managers_group.id if managers_group else 0

        for record in self:
            user_group_ids = set(record.groups_id.ids)
            record.opms_is_submissions_user = submissions_group_id in user_group_ids
            record.opms_is_manager = managers_group_id in user_group_ids

    def _set_opms_group_membership(self, group_xmlid, enabled):
        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        if not group:
            return
        command = (4, group.id) if enabled else (3, group.id)
        for record in self:
            super(ResUsers, record).write({"groups_id": [command]})

    def _inverse_opms_is_submissions_user(self):
        for record in self:
            record._set_opms_group_membership("opms_ecdhs.group_opms_submissions_user", record.opms_is_submissions_user)

    def _inverse_opms_is_manager(self):
        for record in self:
            record._set_opms_group_membership("opms_ecdhs.group_opms_manager", record.opms_is_manager)


class OpmsAppPlan(models.Model):
    _name = "opms.app.plan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS APP Plan"
    _rec_name = "name"

    name = fields.Char(required=True)
    code = fields.Char()
    financial_year = fields.Many2one("account.fiscal.year", required=True, ondelete="restrict")
    active = fields.Boolean(default=True)
    status = fields.Selection(
        [("active", "Active"), ("inactive", "Inactive")],
        compute="_compute_status",
        store=True,
    )
    notes = fields.Text()

    annual_target_ids = fields.One2many("opms.annual.target", "app_plan_id")
    quarter_ids = fields.One2many("opms.quarter", "app_plan_id")
    quarterly_target_ids = fields.One2many("opms.quarterly.target", "app_plan_id")
    narrative_ids = fields.One2many("opms.narrative", "app_plan_id")
    evidence_ids = fields.One2many("opms.evidence", "app_plan_id")
    reporting_submission_ids = fields.One2many("opms.reporting.submission", "app_plan_id")

    annual_target_count = fields.Integer(compute="_compute_counts")
    quarter_count = fields.Integer(compute="_compute_counts")
    quarterly_target_count = fields.Integer(compute="_compute_counts")
    narrative_count = fields.Integer(compute="_compute_counts")
    evidence_count = fields.Integer(compute="_compute_counts")
    submission_count = fields.Integer(compute="_compute_counts")

    @api.depends(
        "annual_target_ids",
        "quarter_ids",
        "quarterly_target_ids",
        "narrative_ids",
        "evidence_ids",
        "reporting_submission_ids",
    )
    def _compute_counts(self):
        for record in self:
            record.annual_target_count = len(record.annual_target_ids)
            record.quarter_count = len(record.quarter_ids)
            record.quarterly_target_count = len(record.quarterly_target_ids)
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            record.submission_count = len(record.reporting_submission_ids)

    @api.depends("active")
    def _compute_status(self):
        for record in self:
            record.status = "active" if record.active else "inactive"

    def action_view_quarters(self):
        return _open_action(self, "opms_ecdhs.action_opms_quarter", [("app_plan_id", "=", self.id)])

    def action_view_annual_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_annual_target", [("app_plan_id", "=", self.id)])

    def action_view_quarterly_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_quarterly_target", [("app_plan_id", "=", self.id)])

    def action_view_narratives(self):
        return _open_action(self, "opms_ecdhs.action_opms_narrative", [("app_plan_id", "=", self.id)])

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("app_plan_id", "=", self.id)])

    def action_view_submissions(self):
        return _open_action(self, "opms_ecdhs.action_opms_reporting_submission", [("app_plan_id", "=", self.id)])

    @api.model
    def _ensure_opms_fiscal_years(self, start_year=2020, end_year=None):
        fiscal_year_model = self.env["account.fiscal.year"].sudo()
        # account_accountant prevents fiscal years on child companies.
        companies = self.env["res.company"].sudo().search([("parent_id", "=", False)])

        if end_year is None:
            today = fields.Date.context_today(self)
            current_start_year = today.year if today.month >= 4 else today.year - 1
            end_year = current_start_year

        for company in companies:
            for year in range(start_year, end_year + 1):
                date_from = date(year, 4, 1)
                date_to = date(year + 1, 3, 31)
                fiscal_year = fiscal_year_model.search(
                    [
                        ("company_id", "=", company.id),
                        ("date_from", "=", date_from),
                        ("date_to", "=", date_to),
                    ],
                    limit=1,
                )
                if not fiscal_year:
                    fiscal_year_model.create(
                        {
                            "name": f"{year}-{str(year + 1)[-2:]}",
                            "date_from": date_from,
                            "date_to": date_to,
                            "company_id": company.id,
                        }
                    )
        return True

    def write(self, vals):
        # Keep child records intact on APP Plan activate/deactivate.
        # Cascading active-state updates made linked data appear deleted.
        return super().write(vals)

    def unlink(self):
        """Override unlink to cascade-delete associated versioned Excel files."""
        self._cleanup_versioned_excel_files()
        return super().unlink()

    def _cleanup_versioned_excel_files(self):
        """Delete versioned Excel files associated with this APP Plan from the module's data directory."""
        try:
            import odoo.modules as odoo_modules
            module_path = odoo_modules.get_module_path("opms_ecdhs")
            if not module_path:
                return
            data_dir = os.path.join(module_path, "data")
            if not os.path.exists(data_dir):
                return

            # Find all import history records linked to this APP Plan
            import_histories = self.env["opms.import.history"].search([("app_plan_id", "in", self.ids)])

            for history in import_histories:
                if history.versioned_excel_filename:
                    file_path = os.path.join(data_dir, history.versioned_excel_filename)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except (OSError, IOError):
                            # Log but don't fail if file can't be deleted
                            pass
        except Exception:
            # Graceful degradation: if cleanup fails, don't block the APP Plan deletion
            pass

    _sql_constraints = [
        ("opms_app_plan_name_year_uniq", "unique(name, financial_year)", "APP Plan already exists for this year."),
    ]


class OpmsProgramme(models.Model):
    _name = "opms.programme"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Programme"

    name = fields.Char(required=True)
    code = fields.Char()

    sub_programme_ids = fields.One2many("opms.sub.programme", "programme_id")
    directorate_ids = fields.One2many("opms.directorate", "programme_id")
    output_ids = fields.One2many("opms.output", "programme_id")
    output_indicator_ids = fields.One2many("opms.output.indicator", "programme_id")
    annual_target_ids = fields.One2many("opms.annual.target", "programme_id")
    quarterly_target_ids = fields.One2many("opms.quarterly.target", "programme_id")
    narrative_ids = fields.One2many("opms.narrative", "programme_id")
    evidence_ids = fields.One2many("opms.evidence", "programme_id")
    reporting_submission_ids = fields.One2many("opms.reporting.submission", "programme_id")
    sub_programme_count = fields.Integer(compute="_compute_sub_programme_count")
    directorate_count = fields.Integer(compute="_compute_sub_programme_count")
    output_count = fields.Integer(compute="_compute_sub_programme_count")
    output_indicator_count = fields.Integer(compute="_compute_sub_programme_count")
    annual_target_count = fields.Integer(compute="_compute_sub_programme_count")
    quarterly_target_count = fields.Integer(compute="_compute_sub_programme_count")
    narrative_count = fields.Integer(compute="_compute_sub_programme_count")
    evidence_count = fields.Integer(compute="_compute_sub_programme_count")
    submission_count = fields.Integer(compute="_compute_sub_programme_count")

    @api.depends(
        "sub_programme_ids",
        "directorate_ids",
        "output_ids",
        "output_indicator_ids",
        "annual_target_ids",
        "quarterly_target_ids",
        "narrative_ids",
        "evidence_ids",
        "reporting_submission_ids",
    )
    def _compute_sub_programme_count(self):
        for record in self:
            record.sub_programme_count = len(record.sub_programme_ids)
            record.directorate_count = len(record.directorate_ids)
            record.output_count = len(record.output_ids)
            record.output_indicator_count = len(record.output_indicator_ids)
            record.annual_target_count = len(record.annual_target_ids)
            record.quarterly_target_count = len(record.quarterly_target_ids)
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            record.submission_count = len(record.reporting_submission_ids)

    def action_view_sub_programmes(self):
        return _open_action(self, "opms_ecdhs.action_opms_sub_programme", [("programme_id", "=", self.id)])

    def action_view_directorates(self):
        return _open_action(self, "opms_ecdhs.action_opms_directorate", [("programme_id", "=", self.id)])

    def action_view_outputs(self):
        return _open_action(self, "opms_ecdhs.action_opms_output", [("programme_id", "=", self.id)])

    def action_view_output_indicators(self):
        return _open_action(self, "opms_ecdhs.action_opms_output_indicator", [("programme_id", "=", self.id)])

    def action_view_annual_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_annual_target", [("programme_id", "=", self.id)])

    def action_view_quarterly_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_quarterly_target", [("programme_id", "=", self.id)])

    def action_view_narratives(self):
        return _open_action(self, "opms_ecdhs.action_opms_narrative", [("programme_id", "=", self.id)])

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("programme_id", "=", self.id)])

    def action_view_submissions(self):
        return _open_action(self, "opms_ecdhs.action_opms_reporting_submission", [("programme_id", "=", self.id)])

    _sql_constraints = [
        ("opms_programme_uniq", "unique(code, name)", "Programme already exists."),
    ]


class OpmsSubProgramme(models.Model):
    _name = "opms.sub.programme"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Sub-Programme"

    name = fields.Char(required=True)
    code = fields.Char()
    programme_id = fields.Many2one("opms.programme", required=True, ondelete="restrict")

    directorate_ids = fields.One2many("opms.directorate", "sub_programme_id")
    output_ids = fields.One2many("opms.output", "sub_programme_id")
    output_indicator_ids = fields.One2many("opms.output.indicator", "sub_programme_id")
    annual_target_ids = fields.One2many("opms.annual.target", "sub_programme_id")
    quarterly_target_ids = fields.One2many("opms.quarterly.target", "sub_programme_id")
    narrative_ids = fields.One2many("opms.narrative", "sub_programme_id")
    evidence_ids = fields.One2many("opms.evidence", "sub_programme_id")
    reporting_submission_ids = fields.One2many("opms.reporting.submission", "sub_programme_id")
    directorate_count = fields.Integer(compute="_compute_directorate_count")
    output_count = fields.Integer(compute="_compute_directorate_count")
    output_indicator_count = fields.Integer(compute="_compute_directorate_count")
    annual_target_count = fields.Integer(compute="_compute_directorate_count")
    quarterly_target_count = fields.Integer(compute="_compute_directorate_count")
    narrative_count = fields.Integer(compute="_compute_directorate_count")
    evidence_count = fields.Integer(compute="_compute_directorate_count")
    submission_count = fields.Integer(compute="_compute_directorate_count")

    @api.depends(
        "directorate_ids",
        "output_ids",
        "output_indicator_ids",
        "annual_target_ids",
        "quarterly_target_ids",
        "narrative_ids",
        "evidence_ids",
        "reporting_submission_ids",
    )
    def _compute_directorate_count(self):
        for record in self:
            record.directorate_count = len(record.directorate_ids)
            record.output_count = len(record.output_ids)
            record.output_indicator_count = len(record.output_indicator_ids)
            record.annual_target_count = len(record.annual_target_ids)
            record.quarterly_target_count = len(record.quarterly_target_ids)
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            record.submission_count = len(record.reporting_submission_ids)

    def action_view_directorates(self):
        return _open_action(self, "opms_ecdhs.action_opms_directorate", [("sub_programme_id", "=", self.id)])

    def action_view_outputs(self):
        return _open_action(self, "opms_ecdhs.action_opms_output", [("sub_programme_id", "=", self.id)])

    def action_view_output_indicators(self):
        return _open_action(self, "opms_ecdhs.action_opms_output_indicator", [("sub_programme_id", "=", self.id)])

    def action_view_annual_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_annual_target", [("sub_programme_id", "=", self.id)])

    def action_view_quarterly_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_quarterly_target", [("sub_programme_id", "=", self.id)])

    def action_view_narratives(self):
        return _open_action(self, "opms_ecdhs.action_opms_narrative", [("sub_programme_id", "=", self.id)])

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("sub_programme_id", "=", self.id)])

    def action_view_submissions(self):
        return _open_action(self, "opms_ecdhs.action_opms_reporting_submission", [("sub_programme_id", "=", self.id)])

    _sql_constraints = [
        (
            "opms_sub_programme_uniq",
            "unique(programme_id, code, name)",
            "Sub-Programme already exists in this Programme.",
        ),
    ]


class OpmsDirectorate(models.Model):
    _name = "opms.directorate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Directorate"

    name = fields.Char(required=True)
    code = fields.Char()
    sub_programme_id = fields.Many2one("opms.sub.programme", required=True, ondelete="restrict")

    programme_id = fields.Many2one(related="sub_programme_id.programme_id", store=True)

    output_ids = fields.One2many("opms.output", "directorate_id")
    output_indicator_ids = fields.One2many("opms.output.indicator", "directorate_id")
    annual_target_ids = fields.One2many("opms.annual.target", "directorate_id")
    quarterly_target_ids = fields.One2many("opms.quarterly.target", "directorate_id")
    narrative_ids = fields.One2many("opms.narrative", "directorate_id")
    evidence_ids = fields.One2many("opms.evidence", "directorate_id")
    reporting_submission_ids = fields.One2many("opms.reporting.submission", "directorate_id")
    output_count = fields.Integer(compute="_compute_output_count")
    output_indicator_count = fields.Integer(compute="_compute_output_count")
    annual_target_count = fields.Integer(compute="_compute_output_count")
    quarterly_target_count = fields.Integer(compute="_compute_output_count")
    narrative_count = fields.Integer(compute="_compute_output_count")
    evidence_count = fields.Integer(compute="_compute_output_count")
    submission_count = fields.Integer(compute="_compute_output_count")

    @api.depends(
        "output_ids",
        "output_indicator_ids",
        "annual_target_ids",
        "quarterly_target_ids",
        "narrative_ids",
        "evidence_ids",
        "reporting_submission_ids",
    )
    def _compute_output_count(self):
        for record in self:
            record.output_count = len(record.output_ids)
            record.output_indicator_count = len(record.output_indicator_ids)
            record.annual_target_count = len(record.annual_target_ids)
            record.quarterly_target_count = len(record.quarterly_target_ids)
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            record.submission_count = len(record.reporting_submission_ids)

    def action_view_outputs(self):
        return _open_action(self, "opms_ecdhs.action_opms_output", [("directorate_id", "=", self.id)])

    def action_view_output_indicators(self):
        return _open_action(self, "opms_ecdhs.action_opms_output_indicator", [("directorate_id", "=", self.id)])

    def action_view_annual_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_annual_target", [("directorate_id", "=", self.id)])

    def action_view_quarterly_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_quarterly_target", [("directorate_id", "=", self.id)])

    def action_view_narratives(self):
        return _open_action(self, "opms_ecdhs.action_opms_narrative", [("directorate_id", "=", self.id)])

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("directorate_id", "=", self.id)])

    def action_view_submissions(self):
        return _open_action(self, "opms_ecdhs.action_opms_reporting_submission", [("directorate_id", "=", self.id)])

    _sql_constraints = [
        (
            "opms_directorate_uniq",
            "unique(sub_programme_id, code, name)",
            "Directorate already exists in this Sub-Programme.",
        ),
    ]


class OpmsOutput(models.Model):
    _name = "opms.output"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Output"

    name = fields.Char(required=True)
    code = fields.Char()
    directorate_id = fields.Many2one("opms.directorate", required=True, ondelete="restrict")

    sub_programme_id = fields.Many2one(related="directorate_id.sub_programme_id", store=True)
    programme_id = fields.Many2one(related="directorate_id.programme_id", store=True)

    output_indicator_ids = fields.One2many("opms.output.indicator", "output_id")
    annual_target_ids = fields.One2many("opms.annual.target", "output_id")
    quarterly_target_ids = fields.One2many("opms.quarterly.target", "output_id")
    narrative_ids = fields.One2many("opms.narrative", "output_id")
    evidence_ids = fields.One2many("opms.evidence", "output_id")
    reporting_submission_ids = fields.One2many("opms.reporting.submission", "output_id")
    output_indicator_count = fields.Integer(compute="_compute_output_indicator_count")
    annual_target_count = fields.Integer(compute="_compute_output_indicator_count")
    quarterly_target_count = fields.Integer(compute="_compute_output_indicator_count")
    narrative_count = fields.Integer(compute="_compute_output_indicator_count")
    evidence_count = fields.Integer(compute="_compute_output_indicator_count")
    submission_count = fields.Integer(compute="_compute_output_indicator_count")

    @api.depends(
        "output_indicator_ids",
        "annual_target_ids",
        "quarterly_target_ids",
        "narrative_ids",
        "evidence_ids",
        "reporting_submission_ids",
    )
    def _compute_output_indicator_count(self):
        for record in self:
            record.output_indicator_count = len(record.output_indicator_ids)
            record.annual_target_count = len(record.annual_target_ids)
            record.quarterly_target_count = len(record.quarterly_target_ids)
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            record.submission_count = len(record.reporting_submission_ids)

    def action_view_output_indicators(self):
        return _open_action(self, "opms_ecdhs.action_opms_output_indicator", [("output_id", "=", self.id)])

    def action_view_annual_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_annual_target", [("output_id", "=", self.id)])

    def action_view_quarterly_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_quarterly_target", [("output_id", "=", self.id)])

    def action_view_narratives(self):
        return _open_action(self, "opms_ecdhs.action_opms_narrative", [("output_id", "=", self.id)])

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("output_id", "=", self.id)])

    def action_view_submissions(self):
        return _open_action(self, "opms_ecdhs.action_opms_reporting_submission", [("output_id", "=", self.id)])

    _sql_constraints = [
        ("opms_output_uniq", "unique(directorate_id, code, name)", "Output already exists in this Directorate."),
    ]


class OpmsOutputIndicator(models.Model):
    _name = "opms.output.indicator"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Output Indicator"

    name = fields.Char(required=True)
    indicator_type = fields.Selection([("app", "APP"), ("aop", "AOP")], default="aop", required=True)
    measurement_type = fields.Selection(MEASUREMENT_TYPE_SELECTION, default="number", required=True)
    measurement_unit = fields.Char(
        string="Measurement Unit",
        help="Optional unit for numeric indicators, e.g. days, houses, km.",
    )
    aggregation_rule = fields.Selection(AGGREGATION_RULE_SELECTION, default="sum", required=True)
    comparison_direction = fields.Selection(COMPARISON_DIRECTION_SELECTION, default="higher", required=True)
    output_id = fields.Many2one("opms.output", required=True, ondelete="restrict")

    directorate_id = fields.Many2one(related="output_id.directorate_id", store=True)
    sub_programme_id = fields.Many2one(related="output_id.sub_programme_id", store=True)
    programme_id = fields.Many2one(related="output_id.programme_id", store=True)

    annual_target_ids = fields.One2many("opms.annual.target", "output_indicator_id")
    quarterly_target_ids = fields.One2many("opms.quarterly.target", "output_indicator_id")
    narrative_ids = fields.One2many("opms.narrative", "output_indicator_id")
    evidence_ids = fields.One2many("opms.evidence", "output_indicator_id")
    reporting_submission_ids = fields.One2many("opms.reporting.submission", "output_indicator_id")
    annual_target_count = fields.Integer(compute="_compute_annual_count")
    quarterly_target_count = fields.Integer(compute="_compute_annual_count")
    narrative_count = fields.Integer(compute="_compute_annual_count")
    evidence_count = fields.Integer(compute="_compute_annual_count")
    submission_count = fields.Integer(compute="_compute_annual_count")

    @api.depends(
        "annual_target_ids",
        "quarterly_target_ids",
        "narrative_ids",
        "evidence_ids",
        "reporting_submission_ids",
    )
    def _compute_annual_count(self):
        for record in self:
            record.annual_target_count = len(record.annual_target_ids)
            record.quarterly_target_count = len(record.quarterly_target_ids)
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            record.submission_count = len(record.reporting_submission_ids)

    def action_view_annual_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_annual_target", [("output_indicator_id", "=", self.id)])

    def action_view_quarterly_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_quarterly_target", [("output_indicator_id", "=", self.id)])

    def action_view_narratives(self):
        return _open_action(self, "opms_ecdhs.action_opms_narrative", [("output_indicator_id", "=", self.id)])

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("output_indicator_id", "=", self.id)])

    def action_view_submissions(self):
        return _open_action(self, "opms_ecdhs.action_opms_reporting_submission", [("output_indicator_id", "=", self.id)])

    def action_compute_quarterly_targets(self):
        self.annual_target_ids._generate_quarterly_targets(overwrite=True)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            measurement_type = vals.get("measurement_type") or "number"
            vals.setdefault("aggregation_rule", _default_aggregation_rule(measurement_type))
            vals.setdefault("comparison_direction", _default_comparison_direction(measurement_type))
        return super().create(vals_list)

    def write(self, vals):
        if "measurement_type" in vals:
            if "aggregation_rule" not in vals:
                vals["aggregation_rule"] = _default_aggregation_rule(vals["measurement_type"])
            if "comparison_direction" not in vals:
                vals["comparison_direction"] = _default_comparison_direction(vals["measurement_type"])
        return super().write(vals)

    @api.onchange("measurement_type")
    def _onchange_measurement_type(self):
        for record in self:
            record.aggregation_rule = _default_aggregation_rule(record.measurement_type)
            record.comparison_direction = _default_comparison_direction(record.measurement_type)
            if record.measurement_type != "number":
                record.measurement_unit = False

    def _get_effective_unit(self, planned_value=None):
        self.ensure_one()
        if (self.measurement_type or "text") != "number":
            return ""
        configured = _text_value(self.measurement_unit)
        if configured:
            return configured
        return _extract_number_unit(planned_value)

    def _get_display_unit(self, planned_value=None):
        """Return unit string for display (empty string if none, or unit text)."""
        unit = self._get_effective_unit(planned_value)
        return unit.strip() if unit else ""

    def _format_value_for_indicator(self, value, planned_value=None):
        """Format value according to measurement type. Values are stored as pure
        types (numbers, dates, etc.) and displayed without any unit text appended."""
        self.ensure_one()
        measurement_type = self.measurement_type or "text"
        return _format_value_for_type(value, measurement_type)

    def _parse_target_value(self, value):
        self.ensure_one()
        measurement_type = self.measurement_type or "text"
        if measurement_type in ("number", "percentage"):
            return _parse_number(value)
        if measurement_type == "date":
            return _parse_date_value(value)
        if measurement_type == "boolean":
            return _parse_boolean_value(value)
        return _text_value(value) or None

    def _parse_submission_actual(self, submission):
        self.ensure_one()
        return self._parse_target_value(submission.actual_value)

    def _aggregate_submission_actuals(self, submissions, preview_actual=None):
        self.ensure_one()
        relevant_submissions = submissions.filtered(lambda rec: rec.workflow_status != "rejected")
        measurement_type = self.measurement_type or "text"
        aggregation_rule = self.aggregation_rule or _default_aggregation_rule(measurement_type)

        # Standalone (per-period / non-cumulative): each quarter is evaluated against the
        # same target independently.  For cross-period summary we resolve to a type-appropriate
        # rule: number/percentage → average; boolean → all; date/milestone/text → latest.
        if aggregation_rule == "standalone":
            if measurement_type in ("number", "percentage"):
                aggregation_rule = "average"
            elif measurement_type == "boolean":
                aggregation_rule = "all"
            else:
                aggregation_rule = "latest"

        if aggregation_rule == "count":
            preview_count = 1 if preview_actual not in (None, False, "") else 0
            return len(relevant_submissions) + preview_count

        parsed_values = []
        for submission in relevant_submissions.sorted(lambda rec: (rec.submission_date or fields.Datetime.now(), rec.id)):
            parsed_value = self._parse_submission_actual(submission)
            if parsed_value is not None:
                parsed_values.append(parsed_value)

        preview_parsed = self._parse_target_value(preview_actual)
        if preview_parsed is not None:
            parsed_values.append(preview_parsed)

        if not parsed_values:
            return None

        if measurement_type in ("number", "percentage"):
            if aggregation_rule == "sum":
                return sum(parsed_values)
            if aggregation_rule == "average":
                return sum(parsed_values) / len(parsed_values)
            if aggregation_rule == "max":
                return max(parsed_values)
            if aggregation_rule == "min":
                return min(parsed_values)
            return parsed_values[-1]

        if measurement_type == "date":
            if aggregation_rule == "max":
                return max(parsed_values)
            if aggregation_rule == "min":
                return min(parsed_values)
            return parsed_values[-1]

        if measurement_type == "boolean":
            if aggregation_rule == "any":
                return any(parsed_values)
            if aggregation_rule == "all":
                return all(parsed_values)
            return parsed_values[-1]

        return parsed_values[-1]

    def _compare_target_and_actual(self, planned_value, actual_value):
        self.ensure_one()
        measurement_type = self.measurement_type or "text"
        parsed_planned = self._parse_target_value(planned_value)
        parsed_actual = self._parse_target_value(actual_value)

        result = {
            "planned_display": self._format_value_for_indicator(planned_value, planned_value=planned_value),
            "actual_display": self._format_value_for_indicator(actual_value, planned_value=planned_value),
            "variance_display": "-",
            "status": "unknown",
            "note": "",
        }

        if parsed_planned is None or parsed_actual is None:
            result["note"] = "Planned and actual values must both be set before comparison is available."
            return result

        if measurement_type in ("number", "percentage"):
            difference = parsed_actual - parsed_planned
            result["variance_display"] = _format_number(difference)
            if measurement_type == "percentage" and result["variance_display"] != "-":
                result["variance_display"] = f"{result['variance_display']}%"

            direction = self.comparison_direction or _default_comparison_direction(measurement_type)
            if direction == "lower":
                if difference < 0:
                    result["status"] = "exceeded"
                elif difference > 0:
                    result["status"] = "behind"
                else:
                    result["status"] = "met"
            elif direction == "exact":
                result["status"] = "met" if difference == 0 else "behind"
            elif difference > 0:
                result["status"] = "exceeded"
            elif difference < 0:
                result["status"] = "behind"
            else:
                result["status"] = "met"

            return result

        if measurement_type == "date":
            delta_days = (parsed_actual - parsed_planned).days
            if delta_days == 0:
                result["variance_display"] = "On target date"
                result["status"] = "met"
            elif delta_days < 0:
                result["variance_display"] = f"{abs(delta_days)} day(s) early"
                result["status"] = "exceeded"
            else:
                result["variance_display"] = f"{delta_days} day(s) late"
                result["status"] = "behind"
            return result

        if measurement_type == "boolean":
            matches = parsed_planned == parsed_actual
            result["variance_display"] = "Matches target" if matches else "Does not match target"
            result["status"] = "met" if matches else "behind"
            return result

        planned_text = _normalize_compare_text(parsed_planned)
        actual_text = _normalize_compare_text(parsed_actual)
        if not planned_text or not actual_text:
            result["note"] = "Text-based comparison requires both planned and actual values."
            return result
        if planned_text == actual_text:
            result["variance_display"] = "Matches target"
            result["status"] = "met"
        else:
            result["variance_display"] = "Manual review required"
            result["status"] = "behind" if measurement_type == "milestone" else "unknown"
            result["note"] = "Text and milestone indicators compare by exact value match unless you define a stricter rubric."
        return result

    _sql_constraints = [
        (
            "opms_output_indicator_uniq",
            "unique(output_id, name, indicator_type)",
            "Output Indicator already exists for this Output.",
        ),
    ]


class OpmsAnnual(models.Model):
    _name = "opms.annual"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Indicator Year"

    name = fields.Char(compute="_compute_name", store=True)
    active = fields.Boolean(default=True)
    financial_year = fields.Many2one("account.fiscal.year", required=True, ondelete="cascade")
    app_plan_id = fields.Many2one("opms.app.plan", required=True, ondelete="cascade")
    output_indicator_id = fields.Many2one("opms.output.indicator", required=True, ondelete="cascade")

    output_id = fields.Many2one(related="output_indicator_id.output_id", store=True)
    directorate_id = fields.Many2one(related="output_indicator_id.directorate_id", store=True)
    sub_programme_id = fields.Many2one(related="output_indicator_id.sub_programme_id", store=True)
    programme_id = fields.Many2one(related="output_indicator_id.programme_id", store=True)

    annual_target_ids = fields.One2many("opms.annual.target", "annual_id")
    quarterly_target_ids = fields.One2many("opms.quarterly.target", "annual_id")
    narrative_ids = fields.One2many("opms.narrative", "annual_id")
    evidence_ids = fields.One2many("opms.evidence", "annual_id")
    reporting_submission_ids = fields.One2many("opms.reporting.submission", "annual_id")
    annual_target_count = fields.Integer(compute="_compute_annual_target_count")
    quarterly_target_count = fields.Integer(compute="_compute_annual_target_count")
    narrative_count = fields.Integer(compute="_compute_annual_target_count")
    evidence_count = fields.Integer(compute="_compute_annual_target_count")
    submission_count = fields.Integer(compute="_compute_annual_target_count")

    @api.depends("output_indicator_id", "financial_year")
    def _compute_name(self):
        for record in self:
            indicator_name = record.output_indicator_id.name or "Indicator"
            year_value = _fiscal_year_label(record.financial_year) or "Year"
            record.name = f"{indicator_name} - {year_value}"

    @api.depends(
        "annual_target_ids",
        "quarterly_target_ids",
        "narrative_ids",
        "evidence_ids",
        "reporting_submission_ids",
    )
    def _compute_annual_target_count(self):
        for record in self:
            record.annual_target_count = len(record.annual_target_ids)
            record.quarterly_target_count = len(record.quarterly_target_ids)
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            record.submission_count = len(record.reporting_submission_ids)

    def action_view_annual_targets(self):
        return _open_action(
            self,
            "opms_ecdhs.action_opms_annual_target",
            [("output_indicator_id", "=", self.output_indicator_id.id), ("financial_year", "=", self.financial_year.id)],
        )

    def action_view_quarterly_targets(self):
        return _open_action(
            self,
            "opms_ecdhs.action_opms_quarterly_target",
            [("output_indicator_id", "=", self.output_indicator_id.id), ("financial_year", "=", self.financial_year.id)],
        )

    def action_view_narratives(self):
        return _open_action(
            self,
            "opms_ecdhs.action_opms_narrative",
            [("output_indicator_id", "=", self.output_indicator_id.id), ("financial_year", "=", self.financial_year.id)],
        )

    def action_view_evidence(self):
        return _open_action(
            self,
            "opms_ecdhs.action_opms_evidence",
            [("output_indicator_id", "=", self.output_indicator_id.id), ("financial_year", "=", self.financial_year.id)],
        )

    def action_view_submissions(self):
        return _open_action(
            self,
            "opms_ecdhs.action_opms_reporting_submission",
            [("output_indicator_id", "=", self.output_indicator_id.id), ("financial_year", "=", self.financial_year.id)],
        )

    _sql_constraints = [
        (
            "opms_annual_uniq",
            "unique(output_indicator_id, app_plan_id, financial_year)",
            "Annual record already exists for this indicator and year.",
        ),
    ]


class OpmsAnnualTarget(models.Model):
    _name = "opms.annual.target"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Annual Target"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    active = fields.Boolean(default=True)

    annual_id = fields.Many2one("opms.annual", ondelete="set null")
    output_indicator_id = fields.Many2one("opms.output.indicator", ondelete="restrict")
    financial_year = fields.Many2one("account.fiscal.year", required=True, ondelete="restrict")
    app_plan_id = fields.Many2one("opms.app.plan", required=True, ondelete="cascade")
    target_value = fields.Char(
        required=True,
        help=(
            "Format must match the indicator measurement type. "
            "Examples: number/percentage (30, 95%), date (2026-03-31), boolean (yes/no), text/milestone (free text)."
        ),
    )
    target_value_guidance = fields.Html(compute="_compute_target_value_guidance")
    actual_value_display = fields.Char(compute="_compute_actual_progress")
    variance_display = fields.Char(string="Deviation", compute="_compute_actual_progress")
    achievement_status = fields.Selection(TARGET_STATUS_SELECTION, compute="_compute_actual_progress")
    comparison_note = fields.Text(compute="_compute_actual_progress")

    output_id = fields.Many2one(related="output_indicator_id.output_id", store=True)
    directorate_id = fields.Many2one(related="output_indicator_id.directorate_id", store=True)
    sub_programme_id = fields.Many2one(related="output_indicator_id.sub_programme_id", store=True)
    programme_id = fields.Many2one(related="output_indicator_id.programme_id", store=True)

    quarterly_target_ids = fields.One2many("opms.quarterly.target", "annual_target_id")
    narrative_ids = fields.One2many("opms.narrative", "annual_target_id")
    evidence_ids = fields.One2many("opms.evidence", "annual_target_id")
    reporting_submission_ids = fields.One2many("opms.reporting.submission", "annual_target_id")
    quarterly_target_count = fields.Integer(compute="_compute_quarterly_target_count")
    narrative_count = fields.Integer(compute="_compute_quarterly_target_count")
    evidence_count = fields.Integer(compute="_compute_quarterly_target_count")
    submission_count = fields.Integer(compute="_compute_quarterly_target_count")

    @api.depends("output_indicator_id.name", "financial_year.name", "target_value")
    def _compute_name(self):
        for record in self:
            indicator_name = record.output_indicator_id.name or "Indicator"
            year_name = record.financial_year.name or "No Year"
            target_value = record.target_value or "-"
            record.name = f"{indicator_name} - {year_name} (Target: {target_value})"

    @api.depends("output_indicator_id.measurement_type", "output_indicator_id.measurement_unit")
    def _compute_target_value_guidance(self):
        for record in self:
            indicator = record.output_indicator_id
            measurement_type = indicator.measurement_type if indicator else "text"
            measurement_unit = indicator.measurement_unit if indicator else ""
            record.target_value_guidance = _build_target_value_guidance_html(
                measurement_type,
                measurement_unit,
            )

    @api.depends("quarterly_target_ids", "narrative_ids", "evidence_ids", "reporting_submission_ids")
    def _compute_quarterly_target_count(self):
        for record in self:
            record.quarterly_target_count = len(record.quarterly_target_ids)
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            record.submission_count = len(record.reporting_submission_ids)

    @api.depends(
        "target_value",
        "output_indicator_id.measurement_type",
        "output_indicator_id.aggregation_rule",
        "reporting_submission_ids.actual_value",
        "reporting_submission_ids.workflow_status",
        "reporting_submission_ids.submission_date",
    )
    def _compute_actual_progress(self):
        for record in self:
            indicator = record.output_indicator_id
            if not indicator:
                record.actual_value_display = "-"
                record.variance_display = "-"
                record.achievement_status = "unknown"
                record.comparison_note = ""
                continue

            actual_value = indicator._aggregate_submission_actuals(record.reporting_submission_ids)
            comparison = indicator._compare_target_and_actual(record.target_value, actual_value)
            record.actual_value_display = comparison["actual_display"]
            record.variance_display = comparison["variance_display"]
            record.achievement_status = comparison["status"]
            record.comparison_note = comparison["note"]

    def action_view_quarterly_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_quarterly_target", [("annual_target_id", "=", self.id)])

    def action_view_narratives(self):
        return _open_action(self, "opms_ecdhs.action_opms_narrative", [("annual_target_id", "=", self.id)])

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("annual_target_id", "=", self.id)])

    def action_view_submissions(self):
        return _open_action(self, "opms_ecdhs.action_opms_reporting_submission", [("annual_target_id", "=", self.id)])

    def _get_or_create_annual(self):
        self.ensure_one()
        if not self.output_indicator_id or not self.financial_year or not self.app_plan_id:
            return self.env["opms.annual"]

        annual = self.env["opms.annual"].search(
            [
                ("output_indicator_id", "=", self.output_indicator_id.id),
                ("app_plan_id", "=", self.app_plan_id.id),
                ("financial_year", "=", self.financial_year.id),
            ],
            limit=1,
        )
        if annual:
            return annual

        return self.env["opms.annual"].create(
            {
                "output_indicator_id": self.output_indicator_id.id,
                "app_plan_id": self.app_plan_id.id,
                "financial_year": self.financial_year.id,
            }
        )

    def _sync_annual_id(self):
        for record in self:
            annual = record._get_or_create_annual()
            if annual and record.annual_id != annual:
                record.annual_id = annual.id

    @api.model
    def _backfill_annual_links(self):
        targets = self.search([])
        targets._sync_annual_id()
        return True

    def _split_quarter_values(self):
        self.ensure_one()
        text_value = (self.target_value or "").strip()
        if not text_value:
            return ["-", "-", "-", "-"]
        try:
            numeric_total = int(float(text_value))
        except (TypeError, ValueError):
            return [text_value, text_value, text_value, text_value]

        base = numeric_total // 4
        remainder = numeric_total % 4
        return [str(base + (1 if index < remainder else 0)) for index in range(4)]

    def _generate_quarterly_targets(self, overwrite=False):
        quarter_codes = ["q1", "q2", "q3", "q4"]
        quarter_cache = {}

        for annual_target in self:
            if not annual_target.app_plan_id or not annual_target.financial_year:
                continue

            quarter_values = annual_target._split_quarter_values()
            for index, code in enumerate(quarter_codes):
                cache_key = (annual_target.app_plan_id.id, annual_target.financial_year.id, code)
                quarter = quarter_cache.get(cache_key)
                if not quarter:
                    quarter = self.env["opms.quarter"].search(
                        [
                            ("app_plan_id", "=", annual_target.app_plan_id.id),
                            ("financial_year", "=", annual_target.financial_year.id),
                            ("code", "=", code),
                        ],
                        limit=1,
                    )
                    if not quarter:
                        quarter = self.env["opms.quarter"].create(
                            {
                                "app_plan_id": annual_target.app_plan_id.id,
                                "financial_year": annual_target.financial_year.id,
                                "code": code,
                                "name": code.upper(),
                            }
                        )
                    quarter_cache[cache_key] = quarter

                domain = [("annual_target_id", "=", annual_target.id), ("quarter_id", "=", quarter.id)]
                quarter_target = self.env["opms.quarterly.target"].search(domain, limit=1)
                planned_target = quarter_values[index]

                if quarter_target:
                    if overwrite:
                        quarter_target.write({"planned_target": planned_target})
                else:
                    self.env["opms.quarterly.target"].create(
                        {
                            "annual_target_id": annual_target.id,
                            "quarter_id": quarter.id,
                            "planned_target": planned_target,
                        }
                    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_annual_id()
        if not self.env.context.get("import_file"):
            records._generate_quarterly_targets(overwrite=False)
        return records

    def write(self, vals):
        result = super().write(vals)
        if {"annual_id", "output_indicator_id", "financial_year"}.intersection(vals.keys()):
            self._sync_annual_id()
        return result

    _sql_constraints = [
        (
            "opms_annual_target_indicator_year_uniq",
            "unique(output_indicator_id, financial_year)",
            "Only one annual target is allowed per output indicator and year.",
        ),
    ]

    @api.constrains("target_value", "output_indicator_id")
    def _check_target_value_matches_measurement_type(self):
        for record in self:
            indicator = record.output_indicator_id
            if not indicator:
                continue
            label = f"Annual target value for '{record.name or indicator.name}'"
            _validate_value_for_measurement_type(
                record.target_value,
                indicator.measurement_type,
                label,
            )


class OpmsQuarter(models.Model):
    _name = "opms.quarter"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Quarter"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    code = fields.Selection([("q1", "Q1"), ("q2", "Q2"), ("q3", "Q3"), ("q4", "Q4")], required=True)
    financial_year = fields.Many2one("account.fiscal.year", required=True, ondelete="restrict")
    app_plan_id = fields.Many2one("opms.app.plan", required=True, ondelete="cascade")
    start_date = fields.Date()
    end_date = fields.Date()
    submission_open_date = fields.Date(tracking=True)
    submission_close_date = fields.Date(tracking=True)
    submission_period_state = fields.Selection(
        [("closed", "Closed"), ("open", "Open")],
        default="closed",
        required=True,
        tracking=True,
    )
    submission_manual_override = fields.Boolean(
        string="Manual Submission Control",
        default=False,
        tracking=True,
        help="When enabled, auto open/close does not apply. Automatically resets on the Override Expires On date.",
    )
    manual_override_until = fields.Date(
        string="Override Expires On",
        tracking=True,
        help=(
            "The manual override automatically clears on this date and automatic scheduling resumes.\n"
            "Force-Open sets this to the day after submission_close_date so the window still auto-closes.\n"
            "Force-Close sets this to submission_open_date so the window still auto-opens."
        ),
    )
    reminder_15_sent_on = fields.Date(copy=False)
    reminder_25_sent_on = fields.Date(copy=False)
    reminder_1day_sent_on = fields.Date(copy=False)
    reminder_open_day_sent_on = fields.Date(copy=False)
    reminder_close_1day_sent_on = fields.Date(copy=False)
    reminder_close_day_sent_on = fields.Date(copy=False)

    quarterly_target_ids = fields.One2many("opms.quarterly.target", "quarter_id")
    narrative_ids = fields.One2many("opms.narrative", "quarter_id")
    evidence_ids = fields.One2many("opms.evidence", "quarter_id")
    reporting_submission_ids = fields.One2many("opms.reporting.submission", "quarter_id")
    quarterly_target_count = fields.Integer(compute="_compute_quarterly_target_count")
    narrative_count = fields.Integer(compute="_compute_quarterly_target_count")
    evidence_count = fields.Integer(compute="_compute_quarterly_target_count")
    submission_count = fields.Integer(compute="_compute_quarterly_target_count")

    @api.depends("quarterly_target_ids", "narrative_ids", "evidence_ids", "reporting_submission_ids")
    def _compute_quarterly_target_count(self):
        for record in self:
            record.quarterly_target_count = len(record.quarterly_target_ids)
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            record.submission_count = len(record.reporting_submission_ids)

    def _compute_default_submission_open_date(self):
        self.ensure_one()
        base_date = self.start_date
        if not base_date and self.financial_year and self.financial_year.date_from:
            quarter_index = {"q1": 0, "q2": 1, "q3": 2, "q4": 3}.get((self.code or "").lower(), 0)
            base_date = self.financial_year.date_from + relativedelta(months=quarter_index * 3)
        if not base_date:
            return False
        return base_date.replace(day=1)

    def _apply_default_submission_window(self):
        for record in self:
            if record.submission_open_date and record.submission_close_date:
                continue
            open_date = record._compute_default_submission_open_date()
            if not open_date:
                continue
            close_date = open_date + timedelta(days=8)
            vals = {}
            if not record.submission_open_date:
                vals["submission_open_date"] = open_date
            if not record.submission_close_date:
                vals["submission_close_date"] = close_date
            if vals:
                super(OpmsQuarter, record).write(vals)

    def _format_human_date(self, value):
        if not value:
            return "-"
        return value.strftime("%d/%m/%Y")

    def _is_submission_open(self, check_date=None):
        self.ensure_one()
        today = check_date or fields.Date.context_today(self)
        if self.submission_manual_override:
            return self.submission_period_state == "open"
        if not self.submission_open_date or not self.submission_close_date:
            return False
        return self.submission_open_date <= today <= self.submission_close_date

    def _raise_if_submission_closed(self):
        self.ensure_one()
        if self._is_submission_open():
            return
        open_text = self._format_human_date(self.submission_open_date)
        close_text = self._format_human_date(self.submission_close_date)
        raise ValidationError(
            "Submissions are currently closed for this quarter. "
            f"Submission window: {open_text} to {close_text}."
        )

    def _sync_submission_period_state(self, today=None):
        today = today or fields.Date.context_today(self)
        for record in self:
            if record.submission_manual_override:
                # Auto-expire the override when its expiry date is reached
                if record.manual_override_until and today >= record.manual_override_until:
                    super(OpmsQuarter, record).write({
                        "submission_manual_override": False,
                        "manual_override_until": False,
                    })
                else:
                    continue
            desired_state = "open" if record._is_submission_open(check_date=today) else "closed"
            if record.submission_period_state != desired_state:
                super(OpmsQuarter, record).write({"submission_period_state": desired_state})

    def _get_submission_notification_users(self):
        group_xmlids = [
            "opms_ecdhs.group_opms_submissions_user",
            "opms_ecdhs.group_opms_manager",
            "opms_ecdhs.group_opms_director",
        ]
        group_ids = []
        for xmlid in group_xmlids:
            grp = self.env.ref(xmlid, raise_if_not_found=False)
            if grp:
                group_ids.append(grp.id)

        if not group_ids:
            return self.env["res.users"]

        users = self.env["res.users"].sudo().search(
            [
                ("active", "=", True),
                ("groups_id", "in", group_ids),
            ]
        )
        public_user = self.env.ref("base.public_user", raise_if_not_found=False)
        if public_user:
            users -= public_user
        return users

    def _get_submission_reminder_schedule(self):
        self.ensure_one()
        if not self.submission_open_date:
            return {}

        previous_month = self.submission_open_date + relativedelta(months=-1)
        schedule = {
            "pre_open_15": previous_month.replace(day=15),
            "pre_open_25": previous_month.replace(day=25),
            "before_open": self.submission_open_date + timedelta(days=-1),
            "open_day": self.submission_open_date,
        }
        if self.submission_close_date:
            schedule["before_close"] = self.submission_close_date + timedelta(days=-1)
            schedule["close_day"] = self.submission_close_date
        return schedule

    def _get_submission_reminder_label(self, reminder_key):
        labels = {
            "pre_open_15": "15th Of Prior Month Reminder",
            "pre_open_25": "25th Of Prior Month Reminder",
            "before_open": "One Day Before Opening Reminder",
            "open_day": "Opening Day Reminder",
            "before_close": "One Day Before Closing Reminder",
            "close_day": "Closing Day Reminder",
            "custom": "Manual Reminder",
        }
        return labels.get(reminder_key, "Submission Reminder")

    def _compose_submission_reminder_content(self, reminder_key, notification_date=None, custom_note=None):
        self.ensure_one()
        quarter_code = (self.code or self.name or "Quarter").upper()
        financial_year_name = self.financial_year.name or "" if self.financial_year else ""
        quarter_label = f"{quarter_code} - {financial_year_name}" if financial_year_name else quarter_code
        reminder_label = self._get_submission_reminder_label(reminder_key)
        open_text = self._format_human_date(self.submission_open_date)
        close_text = self._format_human_date(self.submission_close_date)
        notification_text = self._format_human_date(notification_date)

        reminder_label_html = escape(reminder_label)
        quarter_label_html = escape(quarter_label)
        notification_text_html = escape(notification_text)
        open_text_html = escape(open_text)
        close_text_html = escape(close_text)
        custom_note_html = escape(custom_note) if custom_note else ""

        custom_note_row = ""
        if custom_note:
            custom_note_row = (
                "<tr>"
                "<td style='font-weight:bold;padding:7px 14px 7px 8px;border:1px solid #b0c4e8;color:#8a3a00;'>Additional Note</td>"
                f"<td style='padding:7px 8px;border:1px solid #b0c4e8;'>{custom_note_html}</td>"
                "</tr>"
            )

        subject = f"OPMS Submission Reminder \u2013 {quarter_code}: {reminder_label}"
        body = (
            "<div style='background-color:#e8f0fe;border:1px solid #aac0e8;border-radius:8px;"
            "padding:18px 24px;color:#1a2b4a;font-family:Arial,Helvetica,sans-serif;max-width:680px;'>"
            "<h3 style='margin:0 0 4px 0;color:#1a2b4a;font-size:17px;font-weight:bold;'>"
            "ECDHS OPMS &ndash; Submission Reminder</h3>"
            "<p style='margin:0 0 14px 0;font-size:13px;color:#4a5a6a;'>Operational Performance Management System</p>"
            "<p style='margin:0 0 12px 0;'>Please be advised of the following submission window notification:</p>"
            "<table border='0' cellpadding='7' cellspacing='0' style='margin:12px 0;border-collapse:collapse;width:100%;font-size:14px;'>"
            "<tr style='background-color:#d0ddf8;'>"
            "<td style='font-weight:bold;width:220px;padding:7px 14px 7px 8px;border:1px solid #b0c4e8;'>Reminder Type</td>"
            f"<td style='padding:7px 8px;border:1px solid #b0c4e8;'>{reminder_label_html}</td></tr>"
            "<tr>"
            "<td style='font-weight:bold;padding:7px 14px 7px 8px;border:1px solid #b0c4e8;'>Quarter</td>"
            f"<td style='padding:7px 8px;border:1px solid #b0c4e8;'>{quarter_label_html}</td></tr>"
            "<tr style='background-color:#d0ddf8;'>"
            "<td style='font-weight:bold;padding:7px 14px 7px 8px;border:1px solid #b0c4e8;'>Notification Date</td>"
            f"<td style='padding:7px 8px;border:1px solid #b0c4e8;'>{notification_text_html}</td></tr>"
            "<tr>"
            "<td style='font-weight:bold;padding:7px 14px 7px 8px;border:1px solid #b0c4e8;'>Submission Opens</td>"
            f"<td style='padding:7px 8px;border:1px solid #b0c4e8;'><strong>{open_text_html}</strong></td></tr>"
            "<tr style='background-color:#d0ddf8;'>"
            "<td style='font-weight:bold;padding:7px 14px 7px 8px;border:1px solid #b0c4e8;'>Submission Closes</td>"
            f"<td style='padding:7px 8px;border:1px solid #b0c4e8;'><strong>{close_text_html}</strong></td></tr>"
            f"{custom_note_row}"
            "</table>"
            "<p style='margin:12px 0;'>Please ensure all reporting submissions are completed within the submission window.</p>"
            "<p style='margin:20px 0 0 0;font-size:13px;'>Kind regards,<br/>"
            "<strong>ECDHS OPMS System</strong><br/>"
            "<em>Eastern Cape Department of Human Settlements</em></p>"
            "</div>"
        )
        return subject, body
    def _get_submission_reminder_template(self):
        return self.env.ref("opms_ecdhs.mail_template_opms_submission_reminder", raise_if_not_found=False)

    def _send_submission_window_notification(
        self,
        reminder_key,
        notification_date=None,
        custom_note=None,
        custom_subject=None,
        custom_body_html=None,
    ):
        self.ensure_one()
        users = self._get_submission_notification_users()
        notification_date = notification_date or fields.Date.context_today(self)
        subject, body_html = self._compose_submission_reminder_content(
            reminder_key=reminder_key,
            notification_date=notification_date,
            custom_note=custom_note,
        )
        if custom_subject:
            subject = custom_subject
        if custom_body_html:
            body_html = custom_body_html

        partners = users.mapped("partner_id").filtered(lambda p: p and p.active)
        emails = sorted({email.strip() for email in users.mapped("email") if email})

        if emails:
            mail = self.env["mail.mail"].sudo().create(
                {
                    "subject": subject,
                    "body_html": body_html,
                    "email_to": ",".join(emails),
                    "auto_delete": False,
                }
            )
            mail.send()

        recipients_text = ", ".join(partners.mapped("display_name")) if partners else "No recipients matched group"
        chatter_body = Markup("%s<p><i>Recipients: %s</i></p>") % (Markup(body_html), escape(recipients_text))
        self.message_post(
            subject=subject,
            body=chatter_body,
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )

    def _process_submission_reminders(self, today=None):
        today = today or fields.Date.context_today(self)
        sent_field_by_key = {
            "pre_open_15": "reminder_15_sent_on",
            "pre_open_25": "reminder_25_sent_on",
            "before_open": "reminder_1day_sent_on",
            "open_day": "reminder_open_day_sent_on",
            "before_close": "reminder_close_1day_sent_on",
            "close_day": "reminder_close_day_sent_on",
        }

        for record in self:
            schedule = record._get_submission_reminder_schedule()
            for reminder_key, scheduled_day in schedule.items():
                if today != scheduled_day:
                    continue
                sent_field = sent_field_by_key.get(reminder_key)
                if sent_field and getattr(record, sent_field):
                    continue

                record._send_submission_window_notification(reminder_key=reminder_key, notification_date=today)
                if sent_field:
                    super(OpmsQuarter, record).write({sent_field: today})

    def action_open_submission_reminder_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Send Submission Reminder",
            "res_model": "opms.submission.reminder.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_quarter_id": self.id,
                "default_notification_date": fields.Date.context_today(self),
            },
        }

    def action_send_submission_reminder(self, reminder_key, notification_date=False, custom_note=False, custom_subject=False):
        self.ensure_one()
        supported_reminders = {
            "pre_open_15",
            "pre_open_25",
            "before_open",
            "open_day",
            "before_close",
            "close_day",
            "custom",
        }
        if reminder_key not in supported_reminders:
            raise ValidationError("Unsupported reminder type selected.")

        self._send_submission_window_notification(
            reminder_key=reminder_key,
            notification_date=notification_date or fields.Date.context_today(self),
            custom_note=custom_note,
            custom_subject=custom_subject,
        )
        return True

    def action_open_submission_period(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Open Submission Period",
            "res_model": "opms.submission.period.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_quarter_id": self.id,
                "default_action_type": "open",
            },
        }

    def _get_effective_override_until(self, action_type):
        """Return a per-record override expiry date that keeps immediate manual
        open/close stable and still allows schedule-driven behavior to resume.

        For force-open:
        - Prefer day after submission_close_date, but never in the past.

        For force-close:
        - Prefer submission_open_date, but never in the past.
        """
        self.ensure_one()
        today = fields.Date.context_today(self)

        # Ensure default window fields are present when possible.
        self._apply_default_submission_window()

        if action_type == "open":
            candidate = self.submission_close_date + timedelta(days=1) if self.submission_close_date else False
        else:
            candidate = self.submission_open_date or False

        # Keep override valid for at least one day so the manual action is visible
        # immediately and does not auto-expire in the same transaction.
        minimum = today + timedelta(days=1)
        if not candidate:
            return minimum
        return candidate if candidate > today else minimum

    def _apply_manual_submission_state(self, action_type):
        """Apply manual open/close state immediately to every record in self.

        This writes values per record so each quarter can carry its own
        manual_override_until date.
        """
        if action_type not in {"open", "close"}:
            raise ValidationError("Unsupported submission period action.")

        desired_state = "open" if action_type == "open" else "closed"
        for record in self:
            override_until = record._get_effective_override_until(action_type)
            # Intentionally bypass model write() side effects for deterministic
            # immediate backend state updates per selected quarter.
            super(OpmsQuarter, record).write(
                {
                    "submission_period_state": desired_state,
                    "submission_manual_override": True,
                    "manual_override_until": override_until,
                }
            )
        return True

    def action_force_open_selected_quarters(self):
        """List-view multi action: open selected quarters immediately."""
        return self._apply_manual_submission_state("open")

    def action_force_close_selected_quarters(self):
        """List-view multi action: close selected quarters immediately."""
        return self._apply_manual_submission_state("close")

    def action_close_submission_period(self):
        self.ensure_one()
        # Align single-record close behavior with list bulk close semantics.
        return self._apply_manual_submission_state("close")

    def action_reset_submission_automation(self):
        self.ensure_one()
        self.write({"submission_manual_override": False, "manual_override_until": False})
        self._apply_default_submission_window()
        self._sync_submission_period_state()
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._apply_default_submission_window()
        records._sync_submission_period_state()
        return records

    def write(self, vals):
        result = super().write(vals)
        window_keys = {
            "start_date",
            "code",
            "financial_year",
            "submission_open_date",
            "submission_close_date",
            "submission_manual_override",
            "manual_override_until",
            "submission_period_state",
        }
        if window_keys.intersection(vals.keys()):
            self._apply_default_submission_window()
            self._sync_submission_period_state()
        return result

    @api.model
    def _cron_process_submission_periods(self):
        today = fields.Date.context_today(self)
        quarters = self.search([("active", "=", True), ("app_plan_id.active", "=", True)])
        quarters._apply_default_submission_window()
        quarters._sync_submission_period_state(today=today)
        quarters._process_submission_reminders(today=today)
        return True

    def action_view_quarterly_targets(self):
        return _open_action(self, "opms_ecdhs.action_opms_quarterly_target", [("quarter_id", "=", self.id)])

    def action_view_narratives(self):
        return _open_action(self, "opms_ecdhs.action_opms_narrative", [("quarter_id", "=", self.id)])

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("quarter_id", "=", self.id)])

    def action_view_submissions(self):
        return _open_action(self, "opms_ecdhs.action_opms_reporting_submission", [("quarter_id", "=", self.id)])

    _sql_constraints = [
        ("opms_quarter_uniq", "unique(app_plan_id, financial_year, code)", "Quarter already exists for this APP plan and year."),
    ]


class OpmsQuarterlyTarget(models.Model):
    _name = "opms.quarterly.target"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Quarterly Target"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    active = fields.Boolean(default=True)

    annual_target_id = fields.Many2one("opms.annual.target", required=True, ondelete="cascade")
    quarter_id = fields.Many2one("opms.quarter", required=True, ondelete="restrict")
    planned_target = fields.Char(
        required=True,
        help=(
            "Format must match the indicator measurement type. "
            "Examples: number/percentage (30, 95%), date (2026-03-31), boolean (yes/no), text/milestone (free text)."
        ),
    )
    planned_target_guidance = fields.Html(compute="_compute_planned_target_guidance")
    actual_value_display = fields.Char(compute="_compute_actual_progress")
    variance_display = fields.Char(string="Deviation", compute="_compute_actual_progress")
    achievement_status = fields.Selection(TARGET_STATUS_SELECTION, compute="_compute_actual_progress")
    comparison_note = fields.Text(compute="_compute_actual_progress")

    annual_id = fields.Many2one(related="annual_target_id.annual_id", store=True)
    output_indicator_id = fields.Many2one(related="annual_target_id.output_indicator_id", store=True)
    output_id = fields.Many2one(related="annual_target_id.output_id", store=True)
    directorate_id = fields.Many2one(related="annual_target_id.directorate_id", store=True)
    sub_programme_id = fields.Many2one(related="annual_target_id.sub_programme_id", store=True)
    programme_id = fields.Many2one(related="annual_target_id.programme_id", store=True)
    app_plan_id = fields.Many2one(related="annual_target_id.app_plan_id", store=True)
    financial_year = fields.Many2one(related="annual_target_id.financial_year", store=True)

    narrative_ids = fields.One2many("opms.narrative", "quarterly_target_id")
    evidence_ids = fields.One2many("opms.evidence", "quarterly_target_id")
    reporting_submission_ids = fields.One2many("opms.reporting.submission", "quarterly_target_id")
    narrative_count = fields.Integer(compute="_compute_counts")
    evidence_count = fields.Integer(compute="_compute_counts")
    reporting_submission_count = fields.Integer(compute="_compute_counts")

    @api.depends("output_indicator_id.name", "quarter_id.code", "quarter_id.name", "financial_year.name", "planned_target")
    def _compute_name(self):
        for record in self:
            indicator_name = record.output_indicator_id.name or "Indicator"
            quarter_label = (record.quarter_id.code or record.quarter_id.name or "Quarter").upper()
            year_name = record.financial_year.name or "No Year"
            planned_target = record.planned_target or "-"
            record.name = f"{indicator_name} - {quarter_label} {year_name} (Planned: {planned_target})"

    @api.depends("output_indicator_id.measurement_type", "output_indicator_id.measurement_unit")
    def _compute_planned_target_guidance(self):
        for record in self:
            indicator = record.output_indicator_id
            measurement_type = indicator.measurement_type if indicator else "text"
            measurement_unit = indicator.measurement_unit if indicator else ""
            record.planned_target_guidance = _build_target_value_guidance_html(
                measurement_type,
                measurement_unit,
            )

    @api.depends("narrative_ids", "evidence_ids", "reporting_submission_ids")
    def _compute_counts(self):
        for record in self:
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            record.reporting_submission_count = len(record.reporting_submission_ids)

    @api.depends(
        "planned_target",
        "output_indicator_id.measurement_type",
        "output_indicator_id.aggregation_rule",
        "reporting_submission_ids.actual_value",
        "reporting_submission_ids.workflow_status",
        "reporting_submission_ids.submission_date",
    )
    def _compute_actual_progress(self):
        for record in self:
            indicator = record.output_indicator_id
            if not indicator:
                record.actual_value_display = "-"
                record.variance_display = "-"
                record.achievement_status = "unknown"
                record.comparison_note = ""
                continue

            actual_value = indicator._aggregate_submission_actuals(record.reporting_submission_ids)
            comparison = indicator._compare_target_and_actual(record.planned_target, actual_value)
            record.actual_value_display = comparison["actual_display"]
            record.variance_display = comparison["variance_display"]
            record.achievement_status = comparison["status"]
            record.comparison_note = comparison["note"]

    def action_view_narratives(self):
        return _open_action(self, "opms_ecdhs.action_opms_narrative", [("quarterly_target_id", "=", self.id)])

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("quarterly_target_id", "=", self.id)])

    def action_view_reporting_submissions(self):
        return _open_action(self, "opms_ecdhs.action_opms_reporting_submission", [("quarterly_target_id", "=", self.id)])

    _sql_constraints = [
        (
            "opms_quarterly_target_uniq",
            "unique(annual_target_id, quarter_id)",
            "Quarterly target already exists for this annual target and quarter.",
        ),
    ]

    @api.constrains("planned_target", "output_indicator_id")
    def _check_planned_target_matches_measurement_type(self):
        for record in self:
            indicator = record.output_indicator_id
            if not indicator:
                continue
            label = f"Quarterly planned target for '{record.name or indicator.name}'"
            _validate_value_for_measurement_type(
                record.planned_target,
                indicator.measurement_type,
                label,
            )


class OpmsNarrative(models.Model):
    _name = "opms.narrative"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Narrative"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    quarterly_target_id = fields.Many2one("opms.quarterly.target", required=True, ondelete="cascade")
    narrative_text = fields.Text(required=True)

    annual_target_id = fields.Many2one("opms.annual.target", ondelete="set null", index=True)
    annual_id = fields.Many2one("opms.annual", ondelete="set null", index=True)
    output_indicator_id = fields.Many2one("opms.output.indicator", ondelete="set null", index=True)
    output_id = fields.Many2one("opms.output", ondelete="set null", index=True)
    directorate_id = fields.Many2one("opms.directorate", ondelete="set null", index=True)
    sub_programme_id = fields.Many2one("opms.sub.programme", ondelete="set null", index=True)
    programme_id = fields.Many2one("opms.programme", ondelete="set null", index=True)
    app_plan_id = fields.Many2one("opms.app.plan", ondelete="set null", index=True)
    quarter_id = fields.Many2one("opms.quarter", ondelete="set null", index=True)
    financial_year = fields.Many2one("account.fiscal.year", ondelete="set null", index=True)

    reporting_submission_id = fields.Many2one("opms.reporting.submission", ondelete="set null")
    evidence_ids = fields.One2many("opms.evidence", "narrative_id")
    evidence_count = fields.Integer(compute="_compute_evidence_count")

    @api.depends("evidence_ids")
    def _compute_evidence_count(self):
        for record in self:
            record.evidence_count = len(record.evidence_ids)

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("narrative_id", "=", self.id)])


class OpmsEvidence(models.Model):
    _name = "opms.evidence"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Evidence"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    quarterly_target_id = fields.Many2one("opms.quarterly.target", required=True, ondelete="cascade")
    narrative_id = fields.Many2one("opms.narrative", ondelete="set null")

    file = fields.Binary(required=True)
    file_name = fields.Char(required=True)
    storage_path = fields.Char(readonly=True)

    annual_target_id = fields.Many2one(related="quarterly_target_id.annual_target_id", store=True)
    annual_id = fields.Many2one(related="quarterly_target_id.annual_id", store=True)
    output_indicator_id = fields.Many2one(related="quarterly_target_id.output_indicator_id", store=True)
    output_id = fields.Many2one(related="quarterly_target_id.output_id", store=True)
    directorate_id = fields.Many2one(related="quarterly_target_id.directorate_id", store=True)
    sub_programme_id = fields.Many2one(related="quarterly_target_id.sub_programme_id", store=True)
    programme_id = fields.Many2one(related="quarterly_target_id.programme_id", store=True)
    app_plan_id = fields.Many2one(related="quarterly_target_id.app_plan_id", store=True)
    quarter_id = fields.Many2one(related="quarterly_target_id.quarter_id", store=True)
    financial_year = fields.Many2one(related="quarterly_target_id.financial_year", store=True)

    reporting_submission_id = fields.Many2one("opms.reporting.submission", ondelete="set null")

    def _ensure_storage_path(self):
        param = self.env["ir.config_parameter"].sudo().get_param("opms_ecdhs.evidence_root")
        base_root = param or os.path.join(tools.config.get("data_dir") or "/tmp", "opms_evidence")

        for record in self:
            year_value = _fiscal_year_label(record.financial_year) or "unknown-year"
            quarter_value = (record.quarter_id.code or "qx").upper()
            directorate_value = _slugify_for_path(record.directorate_id.name)

            directory = os.path.join(base_root, "evidence", year_value, quarter_value, directorate_value)
            os.makedirs(directory, exist_ok=True)

            file_name = record.file_name or f"evidence_{record.id}.bin"
            record.storage_path = os.path.join(directory, file_name)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._ensure_storage_path()
        linked_submissions = records.mapped("reporting_submission_id")
        if linked_submissions:
            linked_submissions._sync_workflow_status_with_evidence()
        return records

    def write(self, vals):
        previous_submissions = self.mapped("reporting_submission_id")
        result = super().write(vals)
        path_fields = {"quarterly_target_id", "file_name"}
        if path_fields.intersection(vals.keys()):
            self._ensure_storage_path()
        linked_submissions = previous_submissions | self.mapped("reporting_submission_id")
        if linked_submissions:
            linked_submissions._sync_workflow_status_with_evidence()
        return result

    def unlink(self):
        linked_submissions = self.mapped("reporting_submission_id").exists()
        result = super().unlink()
        if linked_submissions:
            linked_submissions._sync_workflow_status_with_evidence()
        return result

    def action_open_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/my/opms/evidence/{self.id}/file",
            "target": "new",
        }

    def action_download_file(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/my/opms/evidence/{self.id}/file?download=true",
            "target": "new",
        }


class OpmsReportingSubmission(models.Model):
    _name = "opms.reporting.submission"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Reporting Submission"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    quarterly_target_id = fields.Many2one("opms.quarterly.target", required=True, ondelete="cascade")
    submitted_by = fields.Many2one("res.users", default=lambda self: self.env.user, required=True, ondelete="restrict")
    submission_date = fields.Datetime(default=fields.Datetime.now, required=True)
    workflow_status = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("director_review", "Director Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    rejection_reason = fields.Text(string="Rejection Reason", readonly=True)
    comments = fields.Text(string="Progress", required=True)
    reason_for_deviation = fields.Text(string="Reason for Deviation")
    remedial_actions = fields.Text(string="Remedial Actions")
    actual_value = fields.Char(
        string="Actual Output Value",
        help=(
            "Enter a value using the indicator measurement type. "
            "Examples: number (30), percentage (92), date (2026-02-28), "
            "boolean (yes/no), milestone/text (free text)."
        ),
    )
    actual_value_display = fields.Char(compute="_compute_counts")
    actual_value_guidance = fields.Html(compute="_compute_actual_value_guidance")

    annual_target_id = fields.Many2one(related="quarterly_target_id.annual_target_id", store=True)
    annual_id = fields.Many2one(related="quarterly_target_id.annual_id", store=True)
    output_indicator_id = fields.Many2one(related="quarterly_target_id.output_indicator_id", store=True)
    measurement_type = fields.Selection(related="output_indicator_id.measurement_type", readonly=True)
    measurement_unit = fields.Char(related="output_indicator_id.measurement_unit", readonly=True)
    output_id = fields.Many2one(related="quarterly_target_id.output_id", store=True)
    directorate_id = fields.Many2one(related="quarterly_target_id.directorate_id", store=True)
    sub_programme_id = fields.Many2one(related="quarterly_target_id.sub_programme_id", store=True)
    programme_id = fields.Many2one(related="quarterly_target_id.programme_id", store=True)
    app_plan_id = fields.Many2one(related="quarterly_target_id.app_plan_id", store=True)
    quarter_id = fields.Many2one(related="quarterly_target_id.quarter_id", store=True)
    financial_year = fields.Many2one(related="quarterly_target_id.financial_year", store=True)

    narrative_ids = fields.One2many("opms.narrative", "reporting_submission_id")
    evidence_ids = fields.One2many("opms.evidence", "reporting_submission_id")
    narrative_count = fields.Integer(compute="_compute_counts")
    evidence_count = fields.Integer(compute="_compute_counts")

    @api.depends("narrative_ids", "evidence_ids", "actual_value", "output_indicator_id.measurement_type")
    def _compute_counts(self):
        for record in self:
            record.narrative_count = len(record.narrative_ids)
            record.evidence_count = len(record.evidence_ids)
            indicator = record.output_indicator_id
            if indicator:
                record.actual_value_display = indicator._format_value_for_indicator(
                    record.actual_value,
                    planned_value=record.quarterly_target_id.planned_target,
                )
            else:
                record.actual_value_display = _format_value_for_type(record.actual_value, "text")

    @api.depends(
        "measurement_type",
        "measurement_unit",
        "quarterly_target_id.planned_target",
        "quarterly_target_id.output_indicator_id.name",
    )
    def _compute_actual_value_guidance(self):
        for record in self:
            measurement_type = record.measurement_type or "text"
            unit = _text_value(record.measurement_unit)
            planned = _text_value(record.quarterly_target_id.planned_target)

            if measurement_type == "number":
                example_1 = "1"
                example_2 = "30"
                record.actual_value_guidance = (
                    "<p class='text-muted'>Enter a numeric value only (no words or unit text). "
                    f"Examples: <b>{example_1}</b>, <b>{example_2}</b>."
                    f"{f' Planned target: <b>{planned}</b>.' if planned else ''}</p>"
                )
                continue

            if measurement_type == "percentage":
                record.actual_value_guidance = (
                    "<p class='text-muted'>Enter a numeric percentage value (no text needed). "
                    "Examples: <b>87.5</b>, <b>100</b>.</p>"
                )
                continue

            if measurement_type == "date":
                record.actual_value_guidance = (
                    "<p class='text-muted'>Enter a date value. "
                    "Preferred format: <b>YYYY-MM-DD</b> (example: <b>2026-02-28</b>).</p>"
                )
                continue

            if measurement_type == "boolean":
                record.actual_value_guidance = (
                    "<p class='text-muted'>Enter a yes/no outcome. "
                    "Accepted values include <b>yes/no</b>, <b>true/false</b>, or <b>1/0</b>.</p>"
                )
                continue

            if measurement_type == "milestone":
                record.actual_value_guidance = (
                    "<p class='text-muted'>Enter milestone text exactly as achieved. "
                    "Comparison is exact text match unless a rubric is defined.</p>"
                )
                continue

            record.actual_value_guidance = (
                "<p class='text-muted'>Enter descriptive text for this indicator. "
                "Comparison for text indicators is informational and may require manual review.</p>"
            )

    def _prepare_hierarchy_link_vals(self):
        self.ensure_one()
        quarterly_target = self.quarterly_target_id
        if not quarterly_target:
            return {
                "annual_target_id": False,
                "annual_id": False,
                "output_indicator_id": False,
                "output_id": False,
                "directorate_id": False,
                "sub_programme_id": False,
                "programme_id": False,
                "app_plan_id": False,
                "quarter_id": False,
                "financial_year": False,
            }

        return {
            "annual_target_id": quarterly_target.annual_target_id.id,
            "annual_id": quarterly_target.annual_id.id,
            "output_indicator_id": quarterly_target.output_indicator_id.id,
            "output_id": quarterly_target.output_id.id,
            "directorate_id": quarterly_target.directorate_id.id,
            "sub_programme_id": quarterly_target.sub_programme_id.id,
            "programme_id": quarterly_target.programme_id.id,
            "app_plan_id": quarterly_target.app_plan_id.id,
            "quarter_id": quarterly_target.quarter_id.id,
            "financial_year": quarterly_target.financial_year.id,
        }

    def _normalize_actual_value_for_indicator(self, actual_value, indicator):
        text = _text_value(actual_value)
        if not text:
            return text
        if not indicator:
            return text

        measurement_type = indicator.measurement_type or "text"
        if measurement_type in ("number", "percentage"):
            parsed = _parse_number(text)
            if parsed is not None:
                return _format_number(parsed)

            # Legacy cleanup: values like "12 houses" are converted to "12".
            legacy_match = re.match(r"^\s*([-+]?\d+(?:[.,]\d+)?)", text)
            if legacy_match:
                try:
                    return _format_number(float(legacy_match.group(1).replace(",", "")))
                except (TypeError, ValueError):
                    pass
            return text
        if measurement_type == "date":
            parsed = _parse_date_value(text)
            return parsed.strftime("%Y-%m-%d") if parsed else text
        if measurement_type == "boolean":
            parsed = _parse_boolean_value(text)
            if parsed is None:
                return text
            return "Yes" if parsed else "No"
        return text

    def _normalize_submission_vals(self, vals, existing_record=None):
        normalized = dict(vals)
        if "actual_value" not in normalized:
            return normalized

        quarterly_target = None
        qt_id = normalized.get("quarterly_target_id")
        if qt_id:
            quarterly_target = self.env["opms.quarterly.target"].sudo().browse(qt_id)
        elif existing_record:
            quarterly_target = existing_record.quarterly_target_id

        indicator = quarterly_target.output_indicator_id if quarterly_target else (existing_record.output_indicator_id if existing_record else False)
        normalized["actual_value"] = self._normalize_actual_value_for_indicator(
            normalized.get("actual_value"),
            indicator,
        )
        return normalized

    @api.model
    def _backfill_hierarchy_fields(self):
        submissions = self.search([])
        submissions._sync_hierarchy_fields()
        return True

    def _sync_hierarchy_fields(self):
        for record in self:
            vals = record._prepare_hierarchy_link_vals()
            super(OpmsReportingSubmission, record).write(vals)

    def _sync_parent_submission_links(self):
        parent_records = {
            "quarterly_target_id": self.mapped("quarterly_target_id"),
            "annual_target_id": self.mapped("annual_target_id"),
            "annual_id": self.mapped("annual_id"),
            "output_indicator_id": self.mapped("output_indicator_id"),
            "output_id": self.mapped("output_id"),
            "directorate_id": self.mapped("directorate_id"),
            "sub_programme_id": self.mapped("sub_programme_id"),
            "programme_id": self.mapped("programme_id"),
            "app_plan_id": self.mapped("app_plan_id"),
            "quarter_id": self.mapped("quarter_id"),
        }
        for records in parent_records.values():
            if records:
                records.invalidate_recordset()

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._normalize_submission_vals(vals) for vals in vals_list]
        if self.env.context.get("opms_allow_closed_submission_seed"):
            records = super().create(vals_list)
            records._sync_hierarchy_fields()
            records._sync_parent_submission_links()
            records._sync_workflow_status_with_evidence()
            return records

        QuarterlyTarget = self.env["opms.quarterly.target"].sudo()
        for vals in vals_list:
            qt_id = vals.get("quarterly_target_id")
            if not qt_id:
                continue
            quarter = QuarterlyTarget.browse(qt_id).quarter_id
            if quarter:
                quarter._raise_if_submission_closed()

        records = super().create(vals_list)
        records._sync_hierarchy_fields()
        records._sync_parent_submission_links()
        records._sync_workflow_status_with_evidence()
        return records

    def write(self, vals):
        if "actual_value" in vals:
            if len(self) == 1:
                vals = self._normalize_submission_vals(vals, existing_record=self)
            else:
                same_measurement_type = len(set(self.mapped("measurement_type"))) <= 1
                if same_measurement_type:
                    vals = self._normalize_submission_vals(vals, existing_record=self[0])
        if self.env.context.get("opms_allow_closed_submission_seed"):
            result = super().write(vals)
            if {"quarterly_target_id", "workflow_status", "actual_value", "submission_date"}.intersection(vals.keys()):
                if "quarterly_target_id" in vals:
                    self._sync_hierarchy_fields()
                self._sync_parent_submission_links()
            self._sync_workflow_status_with_evidence()
            return result

        # Capture which records are transitioning TO submitted so we can notify after all syncs.
        manually_submitted_ids = set()
        manually_rejected_ids = set()
        if vals.get("workflow_status") == "submitted":
            for record in self:
                quarter = record.quarter_id
                if quarter:
                    quarter._raise_if_submission_closed()
                if record.workflow_status != "submitted":
                    manually_submitted_ids.add(record.id)
        if vals.get("workflow_status") == "rejected":
            for record in self:
                if record.workflow_status != "rejected":
                    manually_rejected_ids.add(record.id)

        result = super().write(vals)
        if {"quarterly_target_id", "workflow_status", "actual_value", "submission_date"}.intersection(vals.keys()):
            if "quarterly_target_id" in vals:
                self._sync_hierarchy_fields()
            self._sync_parent_submission_links()
        self._sync_workflow_status_with_evidence()

        # Notify managers for records that ended up as submitted via a manual status change.
        # (_sync_workflow_status_with_evidence handles portal/evidence-driven transitions.)
        if manually_submitted_ids:
            newly_submitted = self.filtered(
                lambda r: r.id in manually_submitted_ids and r.workflow_status == "submitted"
            )
            if newly_submitted:
                newly_submitted._notify_managers_submission_completed()

        if manually_rejected_ids:
            newly_rejected = self.filtered(
                lambda r: r.id in manually_rejected_ids and r.workflow_status == "rejected"
            )
            if newly_rejected:
                newly_rejected._notify_submitter_submission_rejected()

        return result

    def _notify_managers_submission_completed(self, custom_note=False):
        """Send an email notification to matching OPMS managers for each submission in self."""
        # Only active OPMS manager profiles linked to at least one directorate are eligible.
        manager_profiles = self.env["opms.user.management"].sudo().search([
            ("active", "=", True),
            ("is_opms_manager", "=", True),
            ("user_id.active", "=", True),
            ("directorate_ids", "!=", False),
        ])
        if not manager_profiles:
            return

        for record in self:
            directorate = record.directorate_id
            if not directorate:
                continue

            manager_partners = manager_profiles.filtered(
                lambda profile: directorate in profile.directorate_ids
            ).mapped("user_id.partner_id").filtered(lambda partner: partner)
            if not manager_partners:
                continue

            email_partners = manager_partners.filtered(lambda partner: partner.email)

            submitted_by = record.submitted_by.name or "Unknown"
            indicator_name = record.output_indicator_id.name or "-"
            quarter_name = (
                (record.quarter_id.code or "").upper() + (
                    f" – {record.financial_year.name}" if record.financial_year else ""
                )
            ) or "-"
            directorate_name = record.directorate_id.name or "-"
            programme_name = record.programme_id.name or "-"
            sub_programme_name = record.sub_programme_id.name or "-"
            output_name = record.output_id.name or "-"
            actual_value = record.actual_value_display or record.actual_value or "-"
            submission_date = (
                fields.Datetime.context_timestamp(
                    self.env.user, record.submission_date
                ).strftime("%d %b %Y %H:%M")
                if record.submission_date
                else "-"
            )

            subject = f"OPMS: Submission Submitted – {indicator_name} ({quarter_name})"

            rows = [
                ("Submitted By", submitted_by),
                ("Submission Date", submission_date),
                ("Quarter", quarter_name),
                ("Programme", programme_name),
                ("Sub-Programme", sub_programme_name),
                ("Directorate", directorate_name),
                ("Output", output_name),
                ("Output Indicator", indicator_name),
                ("Actual Value", actual_value),
            ]
            rows_html = ""
            for i, (label, value) in enumerate(rows):
                bg = ' style="background-color:#d0ddf8;"' if i % 2 == 0 else ""
                rows_html += (
                    f'<tr{bg}><td style="font-weight:bold;padding:7px 14px 7px 8px;'
                    f'border:1px solid #b0c4e8;width:200px;">{label}</td>'
                    f'<td style="padding:7px 8px;border:1px solid #b0c4e8;">{value}</td></tr>'
                )
            if custom_note:
                rows_html += (
                    f'<tr><td style="font-weight:bold;padding:7px 14px 7px 8px;'
                    f'border:1px solid #b0c4e8;color:#8a3a00;">Note</td>'
                    f'<td style="padding:7px 8px;border:1px solid #b0c4e8;">{custom_note}</td></tr>'
                )

            body_html = f"""
<div style="background-color:#e8f0fe;border:1px solid #aac0e8;border-radius:8px;
            padding:18px 24px;color:#1a2b4a;font-family:Arial,Helvetica,sans-serif;max-width:680px;">
    <h3 style="margin:0 0 4px 0;color:#1a2b4a;font-size:17px;font-weight:bold;">
        ECDHS OPMS &ndash; New Submission Submitted
    </h3>
    <p style="margin:0 0 14px 0;font-size:13px;color:#4a5a6a;">Operational Performance Management System</p>
    <p style="margin:0 0 12px 0;">A reporting submission has been submitted and is awaiting your review:</p>
    <table border="0" cellpadding="7" cellspacing="0"
           style="margin:12px 0;border-collapse:collapse;width:100%;font-size:14px;">
        {rows_html}
    </table>
    <p style="margin:20px 0 8px 0;">
        <a href="/odoo/action-opms_ecdhs.action_opms_reporting_submission"
           style="display:inline-block;padding:9px 20px;background-color:#3b5ea6;color:#ffffff;
                  text-decoration:none;border-radius:4px;font-weight:bold;
                  font-family:Arial,sans-serif;font-size:14px;">Review in OPMS</a>
    </p>
    <p style="margin:20px 0 0 0;font-size:13px;">Kind regards,<br/>
       <strong>ECDHS OPMS System</strong><br/>
       <em>Eastern Cape Department of Human Settlements</em></p>
</div>"""

            if email_partners:
                email_from = (
                    self.env.user.email_formatted
                    or self.env.company.email_formatted
                    or self.env.company.email
                    or False
                )
                mail_values = {
                    "subject": subject,
                    "body_html": body_html,
                    "email_to": ",".join(email_partners.mapped("email")),
                    "auto_delete": False,
                    "recipient_ids": [(6, 0, email_partners.ids)],
                }
                if email_from:
                    mail_values["email_from"] = email_from
                # Queue mail for cron delivery to keep submissions/portal actions non-blocking.
                self.env["mail.mail"].sudo().create(mail_values)

            record.with_context(mail_notify_force_send=False).message_post(
                body=Markup(body_html),
                subject=subject,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                partner_ids=manager_partners.ids,
            )

    def _notify_submitter_submission_rejected(self, custom_note=False):
        """Notify the submitter by email and log a rejection audit trail in chatter."""
        for record in self:
            submitter_user = record.submitted_by
            submitter_partner = submitter_user.partner_id if submitter_user else self.env["res.partner"]
            submitter_email = (
                (submitter_partner.email if submitter_partner else False)
                or (submitter_user.email if submitter_user else False)
            )

            rejected_by = self.env.user.name or "System"
            rejected_on = fields.Datetime.context_timestamp(
                self.env.user, fields.Datetime.now()
            ).strftime("%d %b %Y %H:%M")
            rejection_reason = (custom_note or record.rejection_reason or "").strip() or "No reason provided."

            indicator_name = record.output_indicator_id.name or "-"
            quarter_name = (
                (record.quarter_id.code or "").upper() + (
                    f" – {record.financial_year.name}" if record.financial_year else ""
                )
            ) or "-"
            subject = f"OPMS: Submission Rejected – {indicator_name} ({quarter_name})"

            submission_name = escape(record.name or "-")
            quarter_label = escape(
                ((record.quarter_id.code or "").upper() if record.quarter_id and record.quarter_id.code else (record.quarter_id.name or "-"))
                + (f" - {record.financial_year.name}" if record.financial_year else "")
            )
            indicator_label = escape(indicator_name)
            rejected_by_label = escape(rejected_by)
            rejected_on_label = escape(rejected_on)
            reason_label = escape(rejection_reason)

            body_html = f"""
<div style="background-color:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:18px 24px;color:#1f2937;font-family:Arial,Helvetica,sans-serif;max-width:680px;">
    <h3 style="margin:0 0 4px 0;color:#991b1b;font-size:17px;font-weight:bold;">ECDHS OPMS &ndash; Submission Rejected</h3>
    <p style="margin:0 0 14px 0;font-size:13px;color:#4b5563;">Operational Performance Management System</p>

    <p style="margin:0 0 12px 0;">Your reporting submission has been marked as <strong>Rejected</strong>. Please review the details below and resubmit after corrections.</p>

    <table border="0" cellpadding="7" cellspacing="0" style="margin:12px 0;border-collapse:collapse;width:100%;font-size:14px;">
        <tr style="background-color:#fee2e2;">
            <td style="font-weight:bold;width:220px;padding:7px 14px 7px 8px;border:1px solid #fecaca;">Submission</td>
            <td style="padding:7px 8px;border:1px solid #fecaca;">{submission_name}</td>
        </tr>
        <tr>
            <td style="font-weight:bold;padding:7px 14px 7px 8px;border:1px solid #fecaca;">Quarter</td>
            <td style="padding:7px 8px;border:1px solid #fecaca;">{quarter_label}</td>
        </tr>
        <tr style="background-color:#fee2e2;">
            <td style="font-weight:bold;padding:7px 14px 7px 8px;border:1px solid #fecaca;">Output Indicator</td>
            <td style="padding:7px 8px;border:1px solid #fecaca;">{indicator_label}</td>
        </tr>
        <tr>
            <td style="font-weight:bold;padding:7px 14px 7px 8px;border:1px solid #fecaca;">Rejected By</td>
            <td style="padding:7px 8px;border:1px solid #fecaca;">{rejected_by_label}</td>
        </tr>
        <tr style="background-color:#fee2e2;">
            <td style="font-weight:bold;padding:7px 14px 7px 8px;border:1px solid #fecaca;">Rejected On</td>
            <td style="padding:7px 8px;border:1px solid #fecaca;">{rejected_on_label}</td>
        </tr>
        <tr>
            <td style="font-weight:bold;padding:7px 14px 7px 8px;border:1px solid #fecaca;color:#7f1d1d;">Reason</td>
            <td style="padding:7px 8px;border:1px solid #fecaca;">{reason_label}</td>
        </tr>
    </table>

    <p style="margin:20px 0 8px 0;">
        <a href="/my/opms/submit" style="display:inline-block;padding:9px 20px;background-color:#b91c1c;color:#ffffff;text-decoration:none;border-radius:4px;font-weight:bold;font-family:Arial,sans-serif;font-size:14px;">Open OPMS Portal</a>
    </p>

    <p style="margin:20px 0 0 0;font-size:13px;">Kind regards,<br/><strong>ECDHS OPMS System</strong><br/><em>Eastern Cape Department of Human Settlements</em></p>
</div>
            """

            if submitter_email:
                email_from = (
                    self.env.user.email_formatted
                    or self.env.company.email_formatted
                    or self.env.company.email
                    or False
                )

                mail_values = {
                    "subject": subject,
                    "body_html": body_html,
                    "email_to": submitter_email,
                    "auto_delete": False,
                }
                if email_from:
                    mail_values["email_from"] = email_from
                if submitter_partner:
                    mail_values["recipient_ids"] = [(6, 0, [submitter_partner.id])]

                # Queue mail for cron delivery to keep actions non-blocking.
                self.env["mail.mail"].sudo().create(mail_values)

            record.with_context(mail_notify_force_send=False).message_post(
                body=Markup(body_html),
                subject=subject,
                message_type="comment",
                subtype_xmlid="mail.mt_note",
                partner_ids=submitter_partner.ids,
            )

    def action_open_submission_notification_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "opms.submission.notification.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_submission_ids": [(6, 0, self.ids)],
            },
        }

    def action_open_rejection_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Reject Submission",
            "res_model": "opms.rejection.reason.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_submission_id": self.id,
            },
        }

    def action_reset_to_draft(self):
        rejected = self.filtered(lambda rec: rec.workflow_status == "rejected")
        if not rejected:
            raise ValidationError("Only rejected submissions can be reset to draft.")

        rejected.with_context(opms_skip_submission_auto_status_sync=True).write(
            {
                "workflow_status": "draft",
                "rejection_reason": False,
            }
        )
        return True

    def _sync_workflow_status_with_evidence(self):
        if self.env.context.get("opms_skip_submission_auto_status_sync"):
            return

        Evidence = self.env["opms.evidence"].sudo()
        for record in self.exists():
            evidence_count = Evidence.search_count([
                ("reporting_submission_id", "=", record.id),
                ("active", "=", True),
            ])
            target_status = "submitted" if evidence_count else "draft"
            if record.workflow_status in {"draft", "submitted"} and record.workflow_status != target_status:
                super(OpmsReportingSubmission, record).write({"workflow_status": target_status})
                if target_status == "submitted":
                    record._notify_managers_submission_completed()

    def init(self):
        submissions = self.search([])
        if submissions:
            submissions._sync_hierarchy_fields()
            for submission in submissions:
                normalized_value = submission._normalize_actual_value_for_indicator(
                    submission.actual_value,
                    submission.output_indicator_id,
                )
                if normalized_value != submission.actual_value:
                    super(OpmsReportingSubmission, submission).write({"actual_value": normalized_value})

        self.env.cr.execute(
            """
            UPDATE opms_evidence e
               SET reporting_submission_id = NULL
             WHERE reporting_submission_id IS NOT NULL
               AND NOT EXISTS (
                   SELECT 1
                     FROM opms_reporting_submission s
                    WHERE s.id = e.reporting_submission_id
               )
            """
        )
        self.env.cr.execute(
            """
            UPDATE opms_narrative n
               SET reporting_submission_id = NULL
             WHERE reporting_submission_id IS NOT NULL
               AND NOT EXISTS (
                   SELECT 1
                     FROM opms_reporting_submission s
                    WHERE s.id = n.reporting_submission_id
               )
            """
        )
        self.env.cr.execute(
            """
            DELETE FROM mail_message m
             WHERE m.model = 'opms.reporting.submission'
               AND NOT EXISTS (
                   SELECT 1
                     FROM opms_reporting_submission s
                    WHERE s.id = m.res_id
               )
            """
        )
        self.env.cr.execute(
            """
            DELETE FROM mail_followers f
             WHERE f.res_model = 'opms.reporting.submission'
               AND NOT EXISTS (
                   SELECT 1
                     FROM opms_reporting_submission s
                    WHERE s.id = f.res_id
               )
            """
        )
        self.env.cr.execute(
            """
            DELETE FROM ir_model_data d
             WHERE d.model = 'opms.reporting.submission'
               AND NOT EXISTS (
                   SELECT 1
                     FROM opms_reporting_submission s
                    WHERE s.id = d.res_id
               )
            """
        )

    def action_view_narratives(self):
        return _open_action(self, "opms_ecdhs.action_opms_narrative", [("reporting_submission_id", "=", self.id)])

    def action_view_evidence(self):
        return _open_action(self, "opms_ecdhs.action_opms_evidence", [("reporting_submission_id", "=", self.id)])

    @api.constrains("actual_value", "output_indicator_id")
    def _check_actual_value_matches_measurement_type(self):
        for record in self:
            indicator = record.output_indicator_id
            if not indicator:
                continue
            label = f"Actual value for '{record.name or indicator.name}'"
            _validate_value_for_measurement_type(
                record.actual_value,
                indicator.measurement_type,
                label,
            )


class OpmsImportHistory(models.Model):
    _name = "opms.import.history"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Import History"

    name = fields.Char(required=True)
    import_datetime = fields.Datetime(default=fields.Datetime.now, required=True)
    imported_by = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)
    financial_year = fields.Many2one("account.fiscal.year", required=True, ondelete="restrict")
    app_plan_id = fields.Many2one("opms.app.plan", string="APP Plan", ondelete="set null")
    import_mode = fields.Selection(
        [("create", "Create New"), ("update", "Update Existing"), ("skip", "Skip Existing")],
        required=True,
    )
    total_rows = fields.Integer(default=0)
    success_rows = fields.Integer(default=0)
    failed_rows = fields.Integer(default=0)
    warning_rows = fields.Integer(compute="_compute_warning_rows")
    log = fields.Text()
    versioned_excel_filename = fields.Char(
        string="Versioned Excel File",
        readonly=True,
        help="Name of the auto-corrected Excel file generated during this import.",
    )

    line_ids = fields.One2many("opms.import.history.line", "history_id")

    @api.depends("line_ids.message")
    def _compute_warning_rows(self):
        for record in self:
            warnings = 0
            for line in record.line_ids:
                message = (line.message or "").lower()
                if "warning:" in message:
                    warnings += 1
            record.warning_rows = warnings


class OpmsImportHistoryLine(models.Model):
    _name = "opms.import.history.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "OPMS Import History Line"

    history_id = fields.Many2one("opms.import.history", required=True, ondelete="cascade")
    row_number = fields.Integer(required=True)
    row_reference = fields.Char()
    status = fields.Selection([("success", "Success"), ("failed", "Failed"), ("skipped", "Skipped")], required=True)
    message = fields.Text()
