import base64
import json
import mimetypes
import os
import re
from urllib.parse import quote_plus, urlencode
from io import BytesIO
from datetime import date, datetime

from odoo import _, fields, http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors


class OpmsPortalSubmission(http.Controller):
    _MAX_FILE_COUNT = 10
    _MAX_FILE_BYTES = 10 * 1024 * 1024
    _MAX_TOTAL_UPLOAD_BYTES = 25 * 1024 * 1024
    _MAX_TEXT_LEN = 2000
    _MAX_ACTUAL_VALUE_LEN = 100
    _SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._\- ]+")
    _ALLOWED_FILE_EXTENSIONS = {".pdf"}

    def _check_portal_user(self):
        user = request.env.user
        has_access = (
            user.has_group("base.group_portal")
            or user.has_group("base.group_system")
            or user.has_group("base.group_user")
            or user.has_group("opms_ecdhs.group_opms_submissions_user")
            or user.has_group("opms_ecdhs.group_opms_manager")
            or user.has_group("opms_ecdhs.group_opms_director")
        )
        if not has_access:
            raise AccessError(_("Only portal users or authorized OPMS users can access this page."))
        return user

    def _is_user_management_admin(self, user=None):
        user = user or request.env.user
        return bool(
            user.has_group("base.group_system")
            or user.has_group("base.group_erp_manager")
        )

    def _check_user_management_admin(self):
        user = self._check_portal_user()
        if not self._is_user_management_admin(user):
            raise AccessError(_("Only Administration Settings or Access Rights users can access OPMS User Management."))
        return user

    def _parse_int_list(self, values):
        result = []
        for raw in values or []:
            try:
                value = int(raw)
            except (TypeError, ValueError):
                continue
            if value not in result:
                result.append(value)
        return result

    def _user_label_for_management(self, user, public_user_id=None):
        user_type = "Public" if user.id == public_user_id else ("Portal" if user.share else "Internal")
        status = "Active" if user.active else "Inactive"
        login = user.login or "-"
        name = user.name or login
        return f"{name} ({login}) [{user_type} | {status}]"

    def _get_user_management_options(self):
        public_user = request.env.ref("base.public_user", raise_if_not_found=False)
        public_user_id = public_user.id if public_user else None

        users = request.env["res.users"].with_context(active_test=False).sudo().search([], order="name asc, login asc")
        companies = request.env["res.company"].sudo().search([], order="name asc")
        programmes = request.env["opms.programme"].sudo().search([], order="code asc, name asc")
        sub_programmes = request.env["opms.sub.programme"].sudo().search([], order="code asc, name asc")
        directorates = request.env["opms.directorate"].sudo().search([], order="code asc, name asc")

        return {
            "users": [
                {
                    "id": user.id,
                    "label": self._user_label_for_management(user, public_user_id=public_user_id),
                    "company_id": user.company_id.id or False,
                }
                for user in users
            ],
            "companies": [{"id": c.id, "name": c.name or "-"} for c in companies],
            "programmes": [
                {
                    "id": p.id,
                    "name": self._hierarchy_label(p),
                }
                for p in programmes
            ],
            "sub_programmes": [
                {
                    "id": sp.id,
                    "name": self._hierarchy_label(sp),
                    "programme_id": sp.programme_id.id,
                }
                for sp in sub_programmes
            ],
            "directorates": [
                {
                    "id": d.id,
                    "name": self._hierarchy_label(d),
                    "sub_programme_id": d.sub_programme_id.id,
                }
                for d in directorates
            ],
        }

    def _get_user_management_list_rows(self, search_query="", status_filter="", group_filter=""):
        links = request.env["opms.user.management"].with_context(active_test=False).sudo().search([], order="active desc, id desc")
        rows = []
        for link in links:
            user = link.user_id.with_context(active_test=False)
            rows.append(
                {
                    "id": link.id,
                    "active": bool(link.active),
                    "user_name": user.name or "-",
                    "login": user.login or "-",
                    "user_active": bool(user.active),
                    "company_name": link.company_id.name or "-",
                    "programme_names": ", ".join(link.programme_ids.mapped("name")) or "-",
                    "sub_programme_names": ", ".join(link.sub_programme_ids.mapped("name")) or "-",
                    "directorate_names": ", ".join(link.directorate_ids.mapped("name")) or "-",
                    "is_opms_submissions_user": bool(link.is_opms_submissions_user),
                    "is_opms_manager": bool(link.is_opms_manager),
                    "is_opms_director": bool(link.is_opms_director),
                }
            )

        # Apply search filter
        if search_query:
            search_lower = search_query.lower()
            rows = [
                row for row in rows
                if (search_lower in row["user_name"].lower()
                    or search_lower in row["login"].lower()
                    or search_lower in row["company_name"].lower()
                    or search_lower in row["programme_names"].lower()
                    or search_lower in row["sub_programme_names"].lower()
                    or search_lower in row["directorate_names"].lower())
            ]

        # Apply status filter
        if status_filter == "linked":
            rows = [row for row in rows if row["active"]]
        elif status_filter == "blocked":
            rows = [row for row in rows if not row["active"]]
        elif status_filter == "user_inactive":
            rows = [row for row in rows if not row["user_active"]]

        # Apply group filter
        if group_filter == "submissions_user":
            rows = [row for row in rows if row["is_opms_submissions_user"]]
        elif group_filter == "manager":
            rows = [row for row in rows if row["is_opms_manager"]]
        elif group_filter == "director":
            rows = [row for row in rows if row["is_opms_director"]]

        return rows

    def _build_user_management_form_values(self, link=None, error=None):
        options = self._get_user_management_options()
        link = link.sudo() if link else request.env["opms.user.management"]
        return {
            "page_name": "opms_portal_user_management",
            "error": error,
            "is_edit": bool(link and link.id),
            "link": link,
            "options": options,
            "selected_programme_ids": set(link.programme_ids.ids) if link else set(),
            "selected_sub_programme_ids": set(link.sub_programme_ids.ids) if link else set(),
            "selected_directorate_ids": set(link.directorate_ids.ids) if link else set(),
        }

    def _extract_user_management_vals(self, post):
        user_id = self._int_or_none(post.get("user_id"))
        if not user_id:
            raise ValidationError(_("User is required."))

        company_id = self._int_or_none(post.get("company_id"))
        programme_ids = self._parse_int_list(request.httprequest.form.getlist("programme_ids"))
        sub_programme_ids = self._parse_int_list(request.httprequest.form.getlist("sub_programme_ids"))
        directorate_ids = self._parse_int_list(request.httprequest.form.getlist("directorate_ids"))

        if not company_id:
            raise ValidationError(_("Region/Office (Company) is required."))
        if not programme_ids:
            raise ValidationError(_("At least one Programme is required."))
        if not sub_programme_ids:
            raise ValidationError(_("At least one Sub-Programme is required."))
        if not directorate_ids:
            raise ValidationError(_("At least one Directorate is required."))

        return {
            "user_id": user_id,
            "company_id": company_id or False,
            "programme_ids": [(6, 0, programme_ids)],
            "sub_programme_ids": [(6, 0, sub_programme_ids)],
            "directorate_ids": [(6, 0, directorate_ids)],
            "is_opms_submissions_user": post.get("is_opms_submissions_user") in {"on", "1", "true", "True"},
            "is_opms_manager": post.get("is_opms_manager") in {"on", "1", "true", "True"},
            "is_opms_director": post.get("is_opms_director") in {"on", "1", "true", "True"},
            "active": post.get("active") in {"on", "1", "true", "True"},
        }

    def _redirect_with_notice(self, path, success=None, error=None, warning=None):
        params = {}
        if success:
            params["success"] = success
        if error:
            params["error"] = error
        if warning:
            params["warning"] = warning
        if not params:
            return request.redirect(path)
        return request.redirect("%s?%s" % (path, urlencode(params)))

    def _int_or_none(self, value):
        if value in (None, "", False):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _safe_text(self, value, max_len):
        clean = (value or "").strip()
        if len(clean) > max_len:
            raise ValidationError(_("Input exceeds the maximum allowed length."))
        return clean

    def _safe_filename(self, filename):
        base_name = os.path.basename((filename or "").strip())
        sanitized = self._SAFE_FILENAME_RE.sub("_", base_name)
        sanitized = sanitized[:255]
        if not sanitized:
            raise ValidationError(_("Uploaded file name is invalid."))
        _, ext = os.path.splitext(sanitized.lower())
        if ext not in self._ALLOWED_FILE_EXTENSIONS:
            raise ValidationError(_("Unsupported file type uploaded: %s") % (ext or "unknown"))
        return sanitized

    def _validate_pdf_content(self, content):
        if not content or not content.startswith(b"%PDF"):
            raise ValidationError(_("Only valid PDF files are allowed for evidence uploads."))

    def _format_display_date(self, value):
        if not value:
            return "-"
        parsed_date = None
        try:
            if isinstance(value, datetime):
                local_dt = fields.Datetime.context_timestamp(request.env.user, value)
                parsed_date = local_dt.date()
            elif isinstance(value, date):
                parsed_date = value
            else:
                parsed_dt = fields.Datetime.to_datetime(value)
                if parsed_dt:
                    parsed_date = fields.Datetime.context_timestamp(request.env.user, parsed_dt).date()
                else:
                    parsed_date = fields.Date.to_date(value)
        except Exception:
            try:
                parsed_date = fields.Date.to_date(value)
            except Exception:
                parsed_date = None

        if not parsed_date:
            return "-"
        return parsed_date.strftime("%d/%m/%Y")

    def _format_indicator_target_value(self, indicator, value):
        if value in (None, False, ""):
            return "-"
        if not indicator or (indicator.measurement_type or "") != "date":
            return value
        try:
            parsed = indicator._parse_target_value(value)
            return self._format_display_date(parsed)
        except Exception:
            return self._format_display_date(value)

    def _validate_target_matches_posted_scope(self, quarterly_target, post):
        scope_mapping = {
            "financial_year_id": quarterly_target.financial_year.id,
            "programme_id": quarterly_target.programme_id.id,
            "sub_programme_id": quarterly_target.sub_programme_id.id,
            "directorate_id": quarterly_target.directorate_id.id,
            "output_id": quarterly_target.output_id.id,
            "output_indicator_id": quarterly_target.output_indicator_id.id,
            "annual_target_id": quarterly_target.annual_target_id.id,
            "quarter_id": quarterly_target.quarter_id.id,
        }
        for key, expected_value in scope_mapping.items():
            posted_value = self._int_or_none(post.get(key))
            if posted_value and posted_value != expected_value:
                raise ValidationError(_("Selection tampering detected. Please refresh and try again."))

    def _json_response(self, payload):
        return request.make_response(
            json.dumps(payload),
            headers=[
                ("Content-Type", "application/json"),
                ("Cache-Control", "no-store"),
                ("X-Content-Type-Options", "nosniff"),
            ],
        )

    def _get_portal_owned_submission(self, submission_id):
        """Return submission only when it belongs to the current portal user."""
        sub = request.env["opms.reporting.submission"].sudo().browse(submission_id)
        if not sub.exists() or not sub.active:
            return request.env["opms.reporting.submission"]
        if sub.submitted_by.id != request.env.user.id:
            return request.env["opms.reporting.submission"]
        return sub

    def _get_portal_owned_evidence(self, evidence_id):
        """Return evidence only when it belongs to the current portal user via its submission."""
        evidence = request.env["opms.evidence"].sudo().browse(evidence_id)
        if not evidence.exists() or not evidence.active:
            return request.env["opms.evidence"]
        submission = evidence.reporting_submission_id
        if not submission.exists() or not submission.active:
            return request.env["opms.evidence"]
        if submission.submitted_by.id != request.env.user.id:
            return request.env["opms.evidence"]
        return evidence

    def _get_current_financial_year_id(self):
        AppPlan = request.env["opms.app.plan"]
        active_plans = AppPlan.search([("active", "=", True)])
        today = fields.Date.context_today(request.env.user)

        if active_plans:
            active_years = active_plans.mapped("financial_year")
            current_years = active_years.filtered(lambda fy: fy.date_from and fy.date_to and fy.date_from <= today <= fy.date_to)
            if current_years:
                return current_years.sorted(lambda fy: fy.date_from or fy.date_to, reverse=True)[0].id

            latest_years = active_years.sorted(lambda fy: fy.date_to or fy.date_from, reverse=True)
            if latest_years:
                return latest_years[0].id

        FiscalYear = request.env["account.fiscal.year"].sudo()
        user_companies = request.env.user.company_ids.ids or [request.env.company.id]
        fiscal_year = FiscalYear.search(
            [
                ("company_id", "in", user_companies),
                ("date_from", "<=", today),
                ("date_to", ">=", today),
            ],
            order="date_from desc",
            limit=1,
        )
        if not fiscal_year:
            fiscal_year = FiscalYear.search(
                [("company_id", "in", user_companies)],
                order="date_to desc",
                limit=1,
            )
        return fiscal_year.id if fiscal_year else None

    def _build_qt_domain(self, params):
        domain = [("active", "=", True), ("app_plan_id.active", "=", True)]
        mappings = {
            "financial_year_id": "financial_year",
            "programme_id": "programme_id",
            "sub_programme_id": "sub_programme_id",
            "directorate_id": "directorate_id",
            "output_id": "output_id",
            "output_indicator_id": "output_indicator_id",
            "annual_target_id": "annual_target_id",
            "quarter_id": "quarter_id",
        }
        for key, field_name in mappings.items():
            value = self._int_or_none(params.get(key))
            if value:
                domain.append((field_name, "=", value))
        return domain

    def _option_list(self, records, label_getter=None):
        label_getter = label_getter or (lambda rec: rec.display_name)
        return [{"id": rec.id, "name": label_getter(rec)} for rec in records]

    def _hierarchy_option_list(self, records, label_getter=None):
        """Build option list with hierarchy parent references for backfill logic."""
        label_getter = label_getter or (lambda rec: rec.display_name)
        result = []
        for rec in records:
            entry = {"id": rec.id, "name": label_getter(rec)}

            # Include relevant parent hierarchy IDs for backfill
            if hasattr(rec, 'financial_year') and rec.financial_year:
                entry["financial_year_id"] = rec.financial_year.id
            if hasattr(rec, 'programme_id') and rec.programme_id:
                entry["programme_id"] = rec.programme_id.id
            if hasattr(rec, 'sub_programme_id') and rec.sub_programme_id:
                entry["sub_programme_id"] = rec.sub_programme_id.id
            if hasattr(rec, 'directorate_id') and rec.directorate_id:
                entry["directorate_id"] = rec.directorate_id.id
            if hasattr(rec, 'output_id') and rec.output_id:
                entry["output_id"] = rec.output_id.id
            if hasattr(rec, 'output_indicator_id') and rec.output_indicator_id:
                entry["output_indicator_id"] = rec.output_indicator_id.id

            result.append(entry)
        return result

    def _hierarchy_label(self, record):
        code = (record.code or "").strip()
        name = (record.name or "-").strip()
        if not code:
            return name
        if name.startswith(code):
            return name
        return f"{code} {name}"

    def _quarter_label(self, quarter):
        if not quarter:
            return "-"
        quarter_code = (quarter.code or quarter.name or _("Quarter")).upper()
        fy_name = quarter.financial_year.name or ""
        if fy_name:
            return f"{quarter_code} - {fy_name}"
        return quarter_code

    def _build_metric_summary(self, title, target_record, planned_value, preview_actual=None):
        indicator = target_record.output_indicator_id
        preview_value = preview_actual
        if indicator.aggregation_rule == "count" and preview_value is None:
            preview_value = "__count_preview__"
        current_actual = indicator._aggregate_submission_actuals(target_record.reporting_submission_ids)
        projected_actual = indicator._aggregate_submission_actuals(target_record.reporting_submission_ids, preview_value)
        current_comparison = indicator._compare_target_and_actual(planned_value, current_actual)
        projected_comparison = indicator._compare_target_and_actual(planned_value, projected_actual)

        return {
            "title": title,
            "planned_display": current_comparison["planned_display"],
            "actual_display": current_comparison["actual_display"],
            "variance_display": current_comparison["variance_display"],
            "status": current_comparison["status"],
            "projected_actual_display": projected_comparison["actual_display"],
            "projected_variance_display": projected_comparison["variance_display"],
            "projected_status": projected_comparison["status"],
            "note": projected_comparison["note"] or current_comparison["note"],
            "measurement_type": indicator.measurement_type,
            "aggregation_rule": indicator.aggregation_rule,
        }

    def _get_target_input(self, quarterly_target):
        if not quarterly_target:
            return {"visible": False}

        indicator = quarterly_target.output_indicator_id
        measurement_type = indicator.measurement_type or "text"
        input_mode = {
            "number": "number",
            "percentage": "number",
            "date": "date",
            "boolean": "boolean",
            "milestone": "text",
            "text": "textarea",
        }.get(measurement_type, "text")

        placeholder = _("Enter the actual value you are submitting")
        help_text = _("This value will be aggregated using the indicator rule: %s.") % (indicator.aggregation_rule or "latest")
        if measurement_type == "date":
            placeholder = _("Select date using calendar (DD/MM/YYYY)")
            help_text = _(
                "This is a date indicator. Click to open the calendar picker. "
                "Selected dates are formatted as DD/MM/YYYY."
            )

        return {
            "visible": True,
            "measurement_type": measurement_type,
            "aggregation_rule": indicator.aggregation_rule,
            "input_mode": input_mode,
            "label": _("Actual Output value for this submission"),
            "placeholder": placeholder,
            "help_text": help_text,
        }

    def _get_target_summary(self, params):
        QuarterlyTarget = request.env["opms.quarterly.target"]
        qts = QuarterlyTarget.search(self._build_qt_domain(params))
        if len(qts) != 1:
            return {"visible": False}

        quarterly_target = qts[0]
        annual_target = quarterly_target.annual_target_id
        preview_actual = (params.get("preview_actual_value") or "").strip() or None
        quarter = quarterly_target.quarter_id
        planned_display = self._format_indicator_target_value(quarterly_target.output_indicator_id, quarterly_target.planned_target)
        heading = _("Selected target: %s - %s %s (Planned: %s)") % (
            quarterly_target.output_indicator_id.name or "-",
            (quarterly_target.quarter_id.code or quarterly_target.quarter_id.name or "Quarter").upper(),
            quarterly_target.financial_year.name or "",
            planned_display,
        )

        # Get submission period state from quarter
        submission_period_state = quarter.submission_period_state if quarter else "closed"
        submission_open_date = self._format_display_date(quarter.submission_open_date) if quarter else "-"
        submission_close_date = self._format_display_date(quarter.submission_close_date) if quarter else "-"

        return {
            "visible": True,
            "heading": heading,
            "subheading": _("Actuals are aggregated from submission actual values. Projected values include the actual value entered for this new submission."),
            "annual": self._build_metric_summary(_("Annual target"), annual_target, annual_target.target_value, preview_actual),
            "quarterly": self._build_metric_summary(_("Quarterly target"), quarterly_target, quarterly_target.planned_target, preview_actual),
            "target_input": self._get_target_input(quarterly_target),
            "submission_period_state": submission_period_state,
            "submission_open_date": submission_open_date,
            "submission_close_date": submission_close_date,
        }

    def _get_hierarchy_options(self, params):
        QuarterlyTarget = request.env["opms.quarterly.target"]
        qts = QuarterlyTarget.search(self._build_qt_domain(params))
        target_summary = self._get_target_summary(params)

        financial_years = qts.mapped("financial_year").sorted(lambda r: (r.name or ""))
        programmes = qts.mapped("programme_id").sorted(lambda r: (r.code or "", r.name or ""))
        sub_programmes = qts.mapped("sub_programme_id").sorted(lambda r: (r.code or "", r.name or ""))
        directorates = qts.mapped("directorate_id").sorted(lambda r: (r.code or "", r.name or ""))
        outputs = qts.mapped("output_id").sorted(lambda r: (r.code or "", r.name or ""))
        indicators = qts.mapped("output_indicator_id").sorted(lambda r: (r.name or ""))
        annual_targets = qts.mapped("annual_target_id").sorted(lambda r: (r.financial_year.name or "", r.output_indicator_id.name or ""))
        quarters = qts.mapped("quarter_id").sorted(lambda r: (r.financial_year.name or "", r.code or ""))

        # Resolve quarter submission period state when quarter_id is in params
        quarter_id = self._int_or_none(params.get("quarter_id"))
        quarter_submission_state = None
        if quarter_id:
            Quarter = request.env["opms.quarter"]
            quarter = Quarter.browse(quarter_id)
            if quarter.exists():
                quarter_submission_state = {
                    "state": quarter.submission_period_state or "closed",
                    "label": self._quarter_label(quarter),
                    "open_date": self._format_display_date(quarter.submission_open_date),
                    "close_date": self._format_display_date(quarter.submission_close_date),
                }

        options = {
            "financial_years": self._option_list(financial_years, lambda r: r.name),
            "programmes": self._hierarchy_option_list(programmes, self._hierarchy_label),
            "sub_programmes": self._hierarchy_option_list(sub_programmes, self._hierarchy_label),
            "directorates": self._hierarchy_option_list(directorates, self._hierarchy_label),
            "outputs": self._hierarchy_option_list(outputs, self._hierarchy_label),
            "output_indicators": self._hierarchy_option_list(indicators, lambda r: r.name),
            "annual_targets": self._option_list(
                annual_targets,
                    lambda r: f"Target: {self._format_indicator_target_value(r.output_indicator_id, r.target_value)}",
                ),
            "quarters": self._option_list(quarters, lambda r: f"{r.code.upper()} - {r.financial_year.name}"),
            "quarterly_targets": self._option_list(
                qts.sorted(lambda r: ((r.quarter_id.financial_year.name or ""), (r.quarter_id.code or ""), (r.output_indicator_id.name or ""))),
                    lambda r: f"Planned: {self._format_indicator_target_value(r.output_indicator_id, r.planned_target)}",
                ),
            "target_summary": target_summary,
            "target_input": target_summary.get("target_input", {"visible": False}),
            "existing_submissions": self._get_existing_submissions(params),
            "quarter_submission_state": quarter_submission_state,
        }
        return options

    def _get_existing_submissions(self, params):
        """Return serialised list of existing submissions for the selected quarterly target."""
        qt_id = self._int_or_none(params.get("quarterly_target_id"))
        if not qt_id:
            return []
        qt = request.env["opms.quarterly.target"].browse(qt_id)
        if not qt.exists():
            return []
        STATUS_LABELS = {
            "draft": "Draft",
            "submitted": "Submitted",
            "director_review": "Director Review",
            "approved": "Approved",
            "rejected": "Rejected",
        }
        quarter_open = qt.quarter_id._is_submission_open() if qt.quarter_id else False
        planned_value = self._format_indicator_target_value(qt.output_indicator_id, qt.planned_target)
        result = []
        for sub in qt.reporting_submission_ids.sorted(lambda r: (r.submission_date or "", r.id)):
            result.append({
                "id": sub.id,
                "name": sub.name or "-",
                "quarter_code": (qt.quarter_id.code or "-").upper(),
                "submitted_by": sub.submitted_by.name or "-",
                "submission_date": self._format_display_date(sub.submission_date),
                "workflow_status": STATUS_LABELS.get(sub.workflow_status or "", sub.workflow_status or "-"),
                "planned_value": planned_value,
                "actual_value": sub.actual_value_display or "-",
                "comments": sub.comments or "-",
                "is_quarter_open": quarter_open,
                "quarter_label": self._quarter_label(qt.quarter_id),
            })
        return result

    def _get_fy_all_submissions(self, params):
        """Return all submissions for the current financial year for the portal user."""
        STATUS_LABELS = {
            "draft": "Draft", "submitted": "Submitted", "director_review": "Director Review",
            "approved": "Approved", "rejected": "Rejected",
        }
        fy_id = self._int_or_none(params.get("financial_year_id")) or self._get_current_financial_year_id()
        domain = [("active", "=", True)]
        if fy_id:
            domain.append(("financial_year", "=", fy_id))
        subs = request.env["opms.reporting.submission"].search(
            domain, order="submission_date desc, id desc", limit=500
        )

        all_subs = request.env["opms.reporting.submission"].search(
            [("active", "=", True), ("financial_year", "!=", False)],
            order="submission_date desc, id desc",
            limit=5000,
        )
        fy_options = all_subs.mapped("financial_year").sorted(lambda fy: fy.date_from or fields.Date.today(), reverse=True)

        result = []
        for sub in subs:
            qt = sub.quarterly_target_id
            quarter_open = sub.quarter_id._is_submission_open() if sub.quarter_id else False
            planned_value = self._format_indicator_target_value(sub.output_indicator_id, qt.planned_target) if qt else "-"
            result.append({
                "id": sub.id,
                "name": sub.name or "-",
                "submitted_by": sub.submitted_by.name if sub.submitted_by else "-",
                "submission_date": self._format_display_date(sub.submission_date),
                "workflow_status": STATUS_LABELS.get(sub.workflow_status or "", sub.workflow_status or "-"),
                "actual_value": sub.actual_value_display or "-",
                "planned_value": planned_value,
                "comments": sub.comments or "-",
                "quarter_label": self._quarter_label(sub.quarter_id),
                "quarter_code": (sub.quarter_id.code or "").upper() if sub.quarter_id else "-",
                "programme": self._hierarchy_label(sub.programme_id) if sub.programme_id else "-",
                "sub_programme": self._hierarchy_label(sub.sub_programme_id) if sub.sub_programme_id else "-",
                "directorate": self._hierarchy_label(sub.directorate_id) if sub.directorate_id else "-",
                "output": self._hierarchy_label(sub.output_id) if sub.output_id else "-",
                "indicator_name": sub.output_indicator_id.name if sub.output_indicator_id else "-",
                "evidence_count": len(sub.evidence_ids),
                "is_quarter_open": quarter_open,
            })
        return {
            "submissions": result,
            "financial_year_id": fy_id,
            "financial_year_options": [{"id": fy.id, "name": fy.name or "-"} for fy in fy_options],
        }

    def _get_open_submission_periods(self):
        Quarter = request.env["opms.quarter"]
        today = fields.Date.context_today(request.env.user)
        current_fy_id = self._get_current_financial_year_id()
        domain_base = [("active", "=", True)]
        if current_fy_id:
            domain_base.append(("financial_year", "=", current_fy_id))

        open_quarters = Quarter.search(
            domain_base + [("submission_period_state", "=", "open")],
            order="financial_year desc, code asc",
        )

        upcoming_quarters = Quarter.search(
            domain_base
            + [
                ("submission_period_state", "=", "closed"),
                ("submission_open_date", "!=", False),
                ("submission_open_date", ">=", today),
            ],
            order="submission_open_date asc, financial_year asc, code asc",
            limit=8,
        )

        all_quarters = Quarter.search(domain_base, order="financial_year asc, code asc")

        items = []
        for quarter in open_quarters:
            open_date = self._format_display_date(quarter.submission_open_date)
            close_date = self._format_display_date(quarter.submission_close_date)
            items.append(
                {
                    "id": quarter.id,
                    "quarter_code": (quarter.code or "").upper(),
                    "quarter_name": self._quarter_label(quarter),
                    "financial_year": quarter.financial_year.name or "-",
                    "window": f"{open_date} to {close_date}",
                    "open_date": open_date,
                    "close_date": close_date,
                }
            )

        upcoming_items = []
        for quarter in upcoming_quarters:
            open_date = self._format_display_date(quarter.submission_open_date)
            close_date = self._format_display_date(quarter.submission_close_date)
            upcoming_items.append(
                {
                    "id": quarter.id,
                    "quarter_code": (quarter.code or "").upper(),
                    "quarter_name": self._quarter_label(quarter),
                    "financial_year": quarter.financial_year.name or "-",
                    "opens_on": open_date,
                    "window": f"{open_date} to {close_date}",
                }
            )

        all_items = []
        for quarter in all_quarters:
            open_date = self._format_display_date(quarter.submission_open_date)
            close_date = self._format_display_date(quarter.submission_close_date)
            state = quarter.submission_period_state or "closed"
            all_items.append(
                {
                    "id": quarter.id,
                    "quarter_code": (quarter.code or "").upper(),
                    "quarter_name": self._quarter_label(quarter),
                    "financial_year": quarter.financial_year.name or "-",
                    "status": state,
                    "opens_on": open_date,
                    "status_label": "Open" if state == "open" else "Closed",
                    "window": f"{open_date} to {close_date}",
                }
            )

        closed_count = len([item for item in all_items if item.get("status") != "open"])

        current_fy_name = "-"
        if current_fy_id:
            fy = request.env["account.fiscal.year"].sudo().browse(current_fy_id)
            if fy.exists():
                current_fy_name = fy.name or "-"

        return {
            "has_open_periods": bool(items),
            "count": len(items),
            "items": items,
            "has_upcoming_periods": bool(upcoming_items),
            "upcoming_count": len(upcoming_items),
            "upcoming_items": upcoming_items,
            "current_financial_year": current_fy_name,
            "all_count": len(all_items),
            "closed_count": closed_count,
            "all_items": all_items,
        }

    def _serialize_filter_state(self, params):
        keys = [
            "financial_year_id",
            "programme_id",
            "sub_programme_id",
            "directorate_id",
            "output_id",
            "output_indicator_id",
            "quarter_id",
        ]
        state = {key: str(self._int_or_none(params.get(key)) or "") for key in keys}
        status_value = (params.get("status") or "").strip().lower()
        state["status"] = status_value if status_value in {"unknown", "behind", "met", "exceeded"} else ""
        if not state.get("financial_year_id"):
            state["financial_year_id"] = str(self._get_current_financial_year_id() or "")
        return state

    def _get_indicator_rows(self, params):
        QuarterlyTarget = request.env["opms.quarterly.target"]
        domain = self._build_qt_domain(params)
        status_filter = (params.get("status") or "").strip().lower()
        if status_filter not in {"", "unknown", "behind", "met", "exceeded"}:
            status_filter = ""
        qts = QuarterlyTarget.search(domain).sorted(
            lambda rec: (
                rec.output_id.name or "",
                rec.output_indicator_id.name or "",
                rec.quarter_id.code or "",
            )
        )

        quarter_codes = sorted({(qt.quarter_id.code or "").upper() for qt in qts if qt.quarter_id})
        rows = []
        for qt in qts:
            indicator = qt.output_indicator_id
            indicator_type = (indicator.indicator_type or "").upper()
            indicator_label = indicator.name or "-"
            if indicator_type:
                indicator_label = f"{indicator_label} [{indicator_type}]"
            actual_value = indicator._aggregate_submission_actuals(qt.reporting_submission_ids)
            comparison = indicator._compare_target_and_actual(qt.planned_target, actual_value)
            annual_target = qt.annual_target_id
            computed_status = comparison.get("status") or "unknown"
            if status_filter and computed_status != status_filter:
                continue
            submissions = qt.reporting_submission_ids.sorted(lambda rec: (rec.submission_date or "", rec.id))
            last_submission = submissions[-1] if submissions else request.env["opms.reporting.submission"]

            rows.append(
                {
                    "quarterly_target_id": qt.id,
                    "quarter_id": qt.quarter_id.id,
                    "quarter_code": (qt.quarter_id.code or "").upper() or "-",
                    "output_indicator": indicator_label,
                    "output": qt.output_id.name or "-",
                    "activities": qt.output_id.name or "-",
                    "annual_actual": annual_target.actual_value_display or "-",
                    "annual_target": self._format_indicator_target_value(indicator, annual_target.target_value),
                    "annual_variance": annual_target.variance_display or "-",
                    "planned": self._format_indicator_target_value(indicator, qt.planned_target),
                    "actual": comparison.get("actual_display") or "-",
                    "variance": comparison.get("variance_display") or "-",
                    "status": computed_status,
                    "narrative": "Target achieved" if computed_status in ("met", "exceeded") else "In progress",
                    "last_update": self._format_display_date(last_submission.submission_date) if last_submission and last_submission.submission_date else "-",
                    "submission_count": len(submissions),
                    "evidence_count": len(qt.evidence_ids),
                    "evidence_target_url": f"/my/opms/evidence-documents?quarterly_target_id={qt.id}",
                    "narrative_count": len(qt.narrative_ids),
                    "narrative_texts": " | ".join(
                        n.narrative_text for n in qt.narrative_ids
                        if n.narrative_text
                    ) or "-",
                }
            )

        return {
            "rows": rows,
            "quarter_codes": quarter_codes,
            "count": len(rows),
        }

    def _get_load_progress(self, params):
        """Build quarterly submission load-progress matrix grouped by sub-programme and output indicator."""
        QuarterlyTarget = request.env["opms.quarterly.target"]
        domain = [("active", "=", True), ("app_plan_id.active", "=", True)]
        financial_year_id = self._int_or_none(params.get("financial_year_id")) or self._get_current_financial_year_id()
        sub_programme_id = self._int_or_none(params.get("sub_programme_id"))
        load_status = (params.get("load_status") or "").strip().lower()
        if load_status not in ("", "loaded", "not_loaded"):
            load_status = ""
        if financial_year_id:
            domain.append(("financial_year", "=", financial_year_id))
        if sub_programme_id:
            domain.append(("sub_programme_id", "=", sub_programme_id))

        qts = QuarterlyTarget.search(domain).sorted(
            lambda r: (
                r.sub_programme_id.code or "",
                r.sub_programme_id.name or "",
                r.output_indicator_id.name or "",
                r.quarter_id.code or "",
            )
        )

        quarter_map = {}
        for qt in qts:
            code = (qt.quarter_id.code or "?").upper()
            if code not in quarter_map:
                quarter_map[code] = code
        quarter_codes = sorted(quarter_map.keys())

        row_map = {}
        for qt in qts:
            sub_prog = qt.sub_programme_id
            indicator = qt.output_indicator_id
            q_code = (qt.quarter_id.code or "?").upper()
            key = (sub_prog.id, indicator.id)
            if key not in row_map:
                row_map[key] = {
                    "sub_programme": self._hierarchy_label(sub_prog),
                    "output_indicator": indicator.name or "-",
                    "quarters": {},
                }
            row_map[key]["quarters"][q_code] = bool(qt.reporting_submission_ids)

        rows = list(row_map.values())

        if load_status == "loaded":
            rows = [
                row
                for row in rows
                if any(bool(loaded) for loaded in row["quarters"].values())
            ]
        elif load_status == "not_loaded":
            rows = [
                row
                for row in rows
                if any(not bool(loaded) for loaded in row["quarters"].values())
            ]

        for i, row in enumerate(rows):
            row["no"] = i + 1

        all_qts = QuarterlyTarget.search([("active", "=", True), ("app_plan_id.active", "=", True)])
        financial_years = all_qts.mapped("financial_year").sorted(lambda r: r.name or "")
        sub_programmes = all_qts.mapped("sub_programme_id").sorted(lambda r: (r.code or "", r.name or ""))

        total_cells = sum(len(row["quarters"]) for row in rows)
        total_loaded = sum(1 for row in rows for loaded in row["quarters"].values() if loaded)

        return {
            "rows": rows,
            "quarter_codes": quarter_codes,
            "financial_years": [{"id": r.id, "name": r.name} for r in financial_years],
            "sub_programmes": [
                {"id": r.id, "name": self._hierarchy_label(r)}
                for r in sub_programmes
            ],
            "selected_financial_year_id": financial_year_id or "",
            "selected_sub_programme_id": sub_programme_id or "",
            "selected_load_status": load_status,
            "total_cells": total_cells,
            "total_loaded": total_loaded,
            "total_not_loaded": total_cells - total_loaded,
            "count": len(rows),
        }

    def _get_dashboard_snapshot(self):
        app_plan_model = request.env["opms.app.plan"]
        quarterly_target_model = request.env["opms.quarterly.target"]
        submission_model = request.env["opms.reporting.submission"]
        evidence_model = request.env["opms.evidence"]
        narrative_model = request.env["opms.narrative"]

        base_domain = [("active", "=", True), ("app_plan_id.active", "=", True)]
        quarterly_targets = quarterly_target_model.search(base_domain)
        submissions = submission_model.search(base_domain)
        evidence = evidence_model.search(base_domain)
        narratives = narrative_model.search(base_domain)

        target_count = len(quarterly_targets)
        submitted_target_count = len(quarterly_targets.filtered(lambda qt: bool(qt.reporting_submission_ids)))
        load_percent = round((submitted_target_count / target_count) * 100, 1) if target_count else 0.0

        status_labels = {
            "unknown": _("Not Submitted"),
            "behind": _("Not-Achieved"),
            "met": _("Achieved"),
            "exceeded": _("Exceeded"),
        }
        status_tones = {
            "unknown": "muted",
            "behind": "warning",
            "met": "success",
            "exceeded": "primary",
        }
        status_rows = []
        for key in ["unknown", "behind", "met", "exceeded"]:
            count = len(quarterly_targets.filtered(lambda qt: qt.achievement_status == key))
            pct = round((count / target_count) * 100, 1) if target_count else 0.0
            status_rows.append(
                {
                    "key": key,
                    "label": status_labels[key],
                    "count": count,
                    "pct": pct,
                    "tone": status_tones[key],
                }
            )

        status_chart_colors = {
            "unknown": "#94a3b8",
            "behind": "#f59e0b",
            "met": "#22c55e",
            "exceeded": "#2563eb",
        }
        donut_parts = []
        donut_legend = []
        position = 0.0
        for row in status_rows:
            pct = float(row.get("pct", 0.0))
            color = status_chart_colors.get(row["key"], "#94a3b8")
            if pct > 0:
                end_pos = min(100.0, position + pct)
                donut_parts.append(f"{color} {position:.2f}% {end_pos:.2f}%")
                position = end_pos
            donut_legend.append(
                {
                    "label": row["label"],
                    "count": row["count"],
                    "pct": row["pct"],
                    "color": color,
                }
            )
        status_donut = f"conic-gradient({', '.join(donut_parts)})" if donut_parts else "conic-gradient(#e2e8f0 0 100%)"

        workflow_labels = {
            "draft": _("Draft"),
            "submitted": _("Submitted"),
            "director_review": _("Director Review"),
            "approved": _("Approved"),
            "rejected": _("Rejected"),
        }
        workflow_rows = []
        submission_count = len(submissions)
        for key in ["draft", "submitted", "director_review", "approved", "rejected"]:
            count = len(submissions.filtered(lambda s: s.workflow_status == key))
            pct = round((count / submission_count) * 100, 1) if submission_count else 0.0
            workflow_rows.append(
                {
                    "key": key,
                    "label": workflow_labels[key],
                    "count": count,
                    "pct": pct,
                }
            )

        workflow_chart_palette = {
            "draft": "#94a3b8",
            "submitted": "#38bdf8",
            "director_review": "#f59e0b",
            "approved": "#22c55e",
            "rejected": "#ef4444",
        }
        workflow_pie_rows = [
            {
                "key": row["key"],
                "label": row["label"],
                "count": row["count"],
                "pct": row["pct"],
                "color": workflow_chart_palette.get(row["key"], "#94a3b8"),
            }
            for row in workflow_rows
        ]

        quarter_activity_map = {}
        for target in quarterly_targets:
            quarter_code = (target.quarter_id.code or "qx").upper()
            if quarter_code not in quarter_activity_map:
                quarter_activity_map[quarter_code] = {
                    "quarter": quarter_code,
                    "targets": 0,
                    "loaded_targets": 0,
                    "submissions": 0,
                    "evidence": 0,
                }
            quarter_activity_map[quarter_code]["targets"] += 1
            quarter_activity_map[quarter_code]["loaded_targets"] += 1 if target.reporting_submission_ids else 0
            quarter_activity_map[quarter_code]["submissions"] += len(target.reporting_submission_ids)
            quarter_activity_map[quarter_code]["evidence"] += len(target.evidence_ids)

        def _quarter_rank(code):
            value = (code or "").upper().strip()
            if value.startswith("Q") and value[1:].isdigit():
                return int(value[1:])
            return 99

        quarter_activity_rows = sorted(
            quarter_activity_map.values(),
            key=lambda row: (_quarter_rank(row.get("quarter")), row.get("quarter") or ""),
        )
        for row in quarter_activity_rows:
            targets = row.get("targets", 0)
            row["load_percent"] = round((row.get("loaded_targets", 0) / targets) * 100, 1) if targets else 0.0

        years = quarterly_targets.mapped("financial_year").sorted(lambda fy: fy.date_from or fy.name or "", reverse=True)
        year_rows = []
        for fy in years:
            fy_targets = quarterly_targets.filtered(lambda qt: qt.financial_year.id == fy.id)
            fy_submissions = submissions.filtered(lambda s: s.financial_year.id == fy.id)
            fy_evidence = evidence.filtered(lambda e: e.financial_year.id == fy.id)
            fy_narratives = narratives.filtered(lambda n: n.financial_year.id == fy.id)

            fy_target_count = len(fy_targets)
            fy_loaded_targets = len(fy_targets.filtered(lambda qt: bool(qt.reporting_submission_ids)))
            fy_load_percent = round((fy_loaded_targets / fy_target_count) * 100, 1) if fy_target_count else 0.0

            year_rows.append(
                {
                    "financial_year": fy.name or "-",
                    "quarterly_targets": fy_target_count,
                    "loaded_targets": fy_loaded_targets,
                    "submissions": len(fy_submissions),
                    "evidence": len(fy_evidence),
                    "narratives": len(fy_narratives),
                    "load_percent": fy_load_percent,
                }
            )

        year_rows = sorted(year_rows, key=lambda row: row.get("financial_year") or "")
        max_year_load = max((row.get("load_percent", 0.0) for row in year_rows), default=0.0)
        year_chart_rows = []
        for row in year_rows:
            value = float(row.get("load_percent", 0.0))
            scaled = round((value / max_year_load) * 100.0, 1) if max_year_load else 0.0
            year_chart_rows.append(
                {
                    "financial_year": row.get("financial_year", "-"),
                    "load_percent": value,
                    "scaled_height": scaled,
                    "targets": row.get("quarterly_targets", 0),
                }
            )

        directorate_aggregate = {}
        for target in quarterly_targets:
            directorate = target.directorate_id
            if not directorate:
                continue
            key = directorate.id
            if key not in directorate_aggregate:
                directorate_aggregate[key] = {
                    "name": self._hierarchy_label(directorate),
                    "submissions": 0,
                    "evidence": 0,
                    "targets": 0,
                }
            directorate_aggregate[key]["targets"] += 1
            directorate_aggregate[key]["submissions"] += len(target.reporting_submission_ids)
            directorate_aggregate[key]["evidence"] += len(target.evidence_ids)

        top_directorates = sorted(
            directorate_aggregate.values(),
            key=lambda item: (item["submissions"], item["evidence"], item["targets"]),
            reverse=True,
        )[:6]

        top_indicators = []
        ranked_targets = sorted(
            quarterly_targets,
            key=lambda qt: (len(qt.reporting_submission_ids), len(qt.evidence_ids), qt.output_indicator_id.name or ""),
            reverse=True,
        )[:8]
        for target in ranked_targets:
            top_indicators.append(
                {
                    "indicator": target.output_indicator_id.name or "-",
                    "quarter": (target.quarter_id.code or "-").upper(),
                    "financial_year": target.financial_year.name or "-",
                    "status": target.achievement_status or "unknown",
                    "submissions": len(target.reporting_submission_ids),
                    "evidence": len(target.evidence_ids),
                }
            )

        recent_submissions = submission_model.search(base_domain, order="submission_date desc, id desc", limit=8)
        recent_rows = []
        for submission in recent_submissions:
            recent_rows.append(
                {
                    "name": submission.name or "-",
                    "indicator": submission.output_indicator_id.name or "-",
                    "directorate": self._hierarchy_label(submission.directorate_id) if submission.directorate_id else "-",
                    "date": self._format_display_date(submission.submission_date),
                    "status": submission.workflow_status or "draft",
                }
            )

        current_year_id = self._get_current_financial_year_id()
        current_year = request.env["account.fiscal.year"].sudo().browse(current_year_id) if current_year_id else None

        return {
            "kpis": {
                "app_plans": app_plan_model.search_count([("active", "=", True)]),
                "quarterly_targets": target_count,
                "submissions": submission_count,
                "evidence": len(evidence),
                "load_percent": load_percent,
            },
            "current_year": current_year.name if current_year else _("N/A"),
            "status_rows": status_rows,
            "status_donut": {
                "background": status_donut,
                "legend": donut_legend,
            },
            "workflow_rows": workflow_rows,
            "workflow_pie_rows": workflow_pie_rows,
            "year_rows": year_rows,
            "year_chart_rows": year_chart_rows,
            "quarter_activity_rows": quarter_activity_rows,
            "top_directorates": top_directorates,
            "top_indicators": top_indicators,
            "recent_submissions": recent_rows,
        }

    def _get_evidence_documents(self, params=None):
        params = params or {}
        evidence_model = request.env["opms.evidence"]
        base_domain = [("active", "=", True), ("app_plan_id.active", "=", True)]
        all_records = evidence_model.search(base_domain)

        quarterly_target_id = self._int_or_none(params.get("quarterly_target_id"))
        financial_year_id = self._int_or_none(params.get("financial_year_id"))
        quarter_id = self._int_or_none(params.get("quarter_id"))
        directorate_id = self._int_or_none(params.get("directorate_id"))
        output_indicator_id = self._int_or_none(params.get("output_indicator_id"))
        file_name_search = (params.get("file_name") or "").strip()

        sort_by = (params.get("sort_by") or "hierarchy").strip().lower()
        sort_dir = (params.get("sort_dir") or "asc").strip().lower()
        allowed_sort_by = {"hierarchy", "output_indicator", "quarter", "date", "file_name"}
        if sort_by not in allowed_sort_by:
            sort_by = "hierarchy"
        if sort_dir not in {"asc", "desc"}:
            sort_dir = "asc"

        page = self._int_or_none(params.get("page")) or 1
        if page < 1:
            page = 1
        page_size = self._int_or_none(params.get("page_size")) or 25
        if page_size not in {10, 25, 50, 100}:
            page_size = 25

        filtered_domain = list(base_domain)
        if quarterly_target_id:
            filtered_domain.append(("quarterly_target_id", "=", quarterly_target_id))
        if financial_year_id:
            filtered_domain.append(("financial_year", "=", financial_year_id))
        if quarter_id:
            filtered_domain.append(("quarter_id", "=", quarter_id))
        if directorate_id:
            filtered_domain.append(("directorate_id", "=", directorate_id))
        if output_indicator_id:
            filtered_domain.append(("output_indicator_id", "=", output_indicator_id))
        if file_name_search:
            filtered_domain.append(("file_name", "ilike", file_name_search))

        records = evidence_model.search(filtered_domain)

        financial_years = all_records.mapped("financial_year").sorted(lambda r: (r.date_from or fields.Date.today(), r.name or ""))
        quarters = all_records.mapped("quarter_id").sorted(lambda r: (r.financial_year.name or "", r.code or ""))
        directorates = all_records.mapped("directorate_id").sorted(lambda r: (r.code or "", r.name or ""))
        indicators = all_records.mapped("output_indicator_id").sorted(lambda r: (r.name or ""))

        quarter_rank = {"q1": 1, "q2": 2, "q3": 3, "q4": 4}
        prepared_rows = []
        for rec in records:
            submission = rec.reporting_submission_id.exists()
            submitted_on = submission.submission_date if submission else rec.create_date
            date_text = self._format_display_date(submitted_on)
            date_value = fields.Datetime.context_timestamp(request.env.user, submitted_on) if submitted_on else None
            can_delete = bool(
                submission.exists()
                and submission.active
                and submission.submitted_by.id == request.env.user.id
                and rec.quarter_id._is_submission_open()
            )

            file_name = rec.file_name or f"evidence_{rec.id}.bin"
            prepared_rows.append(
                {
                    "id": rec.id,
                    "programme": (rec.programme_id.name or "").strip(),
                    "sub_programme": (rec.sub_programme_id.name or "").strip(),
                    "directorate": (rec.directorate_id.name or "").strip(),
                    "output": (rec.output_id.name or "").strip(),
                    "output_indicator": rec.output_indicator_id.name or "-",
                    "quarter": (rec.quarter_id.code or "-").upper() if rec.quarter_id else "-",
                    "quarter_rank": quarter_rank.get((rec.quarter_id.code or "").lower(), 99),
                    "date": date_text,
                    "date_raw": date_value,
                    "file_name": file_name,
                    "file_url": f"/my/opms/evidence/{rec.id}/file",
                    "can_delete": can_delete,
                }
            )

        def _lower(value):
            return (value or "").lower().strip()

        if sort_by == "output_indicator":
            prepared_rows = sorted(
                prepared_rows,
                key=lambda row: (_lower(row["output_indicator"]), row["quarter_rank"], row["id"]),
                reverse=(sort_dir == "desc"),
            )
        elif sort_by == "quarter":
            prepared_rows = sorted(
                prepared_rows,
                key=lambda row: (row["quarter_rank"], _lower(row["output_indicator"]), row["id"]),
                reverse=(sort_dir == "desc"),
            )
        elif sort_by == "date":
            prepared_rows = sorted(
                prepared_rows,
                key=lambda row: (row["date_raw"] or datetime.min, _lower(row["output_indicator"]), row["id"]),
                reverse=(sort_dir == "desc"),
            )
        elif sort_by == "file_name":
            prepared_rows = sorted(
                prepared_rows,
                key=lambda row: (_lower(row["file_name"]), _lower(row["output_indicator"]), row["id"]),
                reverse=(sort_dir == "desc"),
            )
        else:
            prepared_rows = sorted(
                prepared_rows,
                key=lambda row: (
                    _lower(row["programme"]),
                    _lower(row["sub_programme"]),
                    _lower(row["directorate"]),
                    _lower(row["output"]),
                    _lower(row["output_indicator"]),
                    row["quarter_rank"],
                    row["id"],
                ),
                reverse=(sort_dir == "desc"),
            )

        total_count = len(prepared_rows)
        total_pages = max(1, (total_count + page_size - 1) // page_size)
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * page_size
        rows = prepared_rows[offset: offset + page_size]

        base_query = {
            "quarterly_target_id": str(quarterly_target_id or ""),
            "financial_year_id": str(financial_year_id or ""),
            "quarter_id": str(quarter_id or ""),
            "directorate_id": str(directorate_id or ""),
            "output_indicator_id": str(output_indicator_id or ""),
            "file_name": file_name_search,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
            "page_size": str(page_size),
        }

        def _build_url(extra=None):
            query = dict(base_query)
            if extra:
                for key, value in extra.items():
                    query[key] = str(value or "")
            clean = {k: v for k, v in query.items() if v not in (None, "")}
            encoded = urlencode(clean)
            return f"/my/opms/evidence-documents?{encoded}" if encoded else "/my/opms/evidence-documents"

        def _sort_link(column):
            next_dir = "asc"
            if sort_by == column and sort_dir == "asc":
                next_dir = "desc"
            return _build_url({"sort_by": column, "sort_dir": next_dir, "page": 1})

        start_idx = offset + 1 if total_count else 0
        end_idx = min(offset + page_size, total_count)
        page_numbers = list(range(1, total_pages + 1))
        if total_pages > 7:
            start_page = max(1, page - 3)
            end_page = min(total_pages, start_page + 6)
            start_page = max(1, end_page - 6)
            page_numbers = list(range(start_page, end_page + 1))

        return {
            "count": total_count,
            "rows": rows,
            "financial_years": self._option_list(financial_years, lambda r: r.name),
            "quarters": self._option_list(quarters, lambda r: f"{(r.code or '-').upper()} - {r.financial_year.name}"),
            "directorates": self._option_list(directorates, self._hierarchy_label),
            "output_indicators": self._option_list(indicators, lambda r: r.name),
            "selected_quarterly_target_id": str(quarterly_target_id or ""),
            "selected_financial_year_id": str(financial_year_id or ""),
            "selected_quarter_id": str(quarter_id or ""),
            "selected_directorate_id": str(directorate_id or ""),
            "selected_output_indicator_id": str(output_indicator_id or ""),
            "selected_file_name": file_name_search,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
            "sort_links": {
                "output_indicator": _sort_link("output_indicator"),
                "quarter": _sort_link("quarter"),
                "date": _sort_link("date"),
                "file_name": _sort_link("file_name"),
            },
            "page": page,
            "page_size": page_size,
            "page_size_options": [10, 25, 50, 100],
            "total_pages": total_pages,
            "start_index": start_idx,
            "end_index": end_idx,
            "prev_url": _build_url({"page": page - 1}) if page > 1 else "",
            "next_url": _build_url({"page": page + 1}) if page < total_pages else "",
            "page_links": [
                {
                    "page": p,
                    "url": _build_url({"page": p}),
                    "is_current": p == page,
                }
                for p in page_numbers
            ],
        }

    @http.route(["/my/opms"], type="http", auth="user", website=True)
    def portal_opms_home(self, **kwargs):
        user = self._check_portal_user()
        values = {
            "page_name": "opms_portal_home",
            "is_opms_user_mgmt_admin": self._is_user_management_admin(user),
        }
        return request.render("opms_ecdhs.portal_opms_home", values)

    @http.route(["/my/opms/user-management"], type="http", auth="user", website=True)
    def portal_user_management(self, success=None, error=None, search="", status="", group="", **kwargs):
        self._check_user_management_admin()
        search = (search or "").strip()
        status = (status or "").strip()
        group = (group or "").strip()
        values = {
            "page_name": "opms_portal_user_management",
            "success": success,
            "error": error,
            "rows": self._get_user_management_list_rows(
                search_query=search,
                status_filter=status,
                group_filter=group
            ),
            "search_query": search,
            "status_filter": status,
            "group_filter": group,
        }
        return request.render("opms_ecdhs.portal_opms_user_management", values)

    @http.route(["/my/opms/user-management/new"], type="http", auth="user", website=True)
    def portal_user_management_new(self, success=None, error=None, warning=None, **kwargs):
        self._check_user_management_admin()
        values = self._build_user_management_form_values(error=error)
        values.update({"success": success, "warning": warning})
        return request.render("opms_ecdhs.portal_opms_user_management_form", values)

    @http.route(["/my/opms/user-management/create"], type="http", auth="user", website=True, methods=["POST"])
    def portal_user_management_create(self, **post):
        self._check_user_management_admin()
        try:
            vals = self._extract_user_management_vals(post)
            request.env["opms.user.management"].sudo().create(vals)
        except ValidationError as e:
            return self._redirect_with_notice(
                "/my/opms/user-management/new",
                error=_("Could not create OPMS profile: %s") % str(e),
            )
        except Exception:
            return self._redirect_with_notice(
                "/my/opms/user-management/new",
                error=_("Could not create OPMS profile due to an unexpected issue. Please review your selections and try again."),
            )
        return self._redirect_with_notice("/my/opms/user-management", success=_("OPMS profile created successfully."))

    @http.route(["/my/opms/user-management/<int:link_id>/edit"], type="http", auth="user", website=True)
    def portal_user_management_edit(self, link_id, success=None, error=None, warning=None, **kwargs):
        self._check_user_management_admin()
        link = request.env["opms.user.management"].with_context(active_test=False).sudo().browse(link_id)
        if not link.exists():
            return self._redirect_with_notice("/my/opms/user-management", error=_("Profile not found."))
        values = self._build_user_management_form_values(link=link, error=error)
        values.update({"success": success, "warning": warning})
        return request.render("opms_ecdhs.portal_opms_user_management_form", values)

    @http.route(["/my/opms/user-management/<int:link_id>/update"], type="http", auth="user", website=True, methods=["POST"])
    def portal_user_management_update(self, link_id, **post):
        self._check_user_management_admin()
        link = request.env["opms.user.management"].with_context(active_test=False).sudo().browse(link_id)
        if not link.exists():
            return self._redirect_with_notice("/my/opms/user-management", error=_("Profile not found."))

        try:
            vals = self._extract_user_management_vals(post)
            link.write(vals)
        except ValidationError as e:
            return self._redirect_with_notice(
                "/my/opms/user-management/%s/edit" % link_id,
                error=_("Could not update OPMS profile: %s") % str(e),
            )
        except Exception:
            return self._redirect_with_notice(
                "/my/opms/user-management/%s/edit" % link_id,
                error=_("Could not update OPMS profile due to an unexpected issue. Please review your selections and try again."),
            )
        return self._redirect_with_notice("/my/opms/user-management", success=_("OPMS profile updated successfully."))

    @http.route(["/my/opms/user-management/<int:link_id>/delete"], type="http", auth="user", website=True, methods=["POST"])
    def portal_user_management_delete(self, link_id, **post):
        self._check_user_management_admin()
        link = request.env["opms.user.management"].with_context(active_test=False).sudo().browse(link_id)
        if link.exists():
            link.unlink()
        return request.redirect("/my/opms/user-management?success=%s" % quote_plus("OPMS profile deleted."))

    @http.route(["/my/opms/user-management/<int:link_id>/block"], type="http", auth="user", website=True, methods=["POST"])
    def portal_user_management_block(self, link_id, **post):
        self._check_user_management_admin()
        link = request.env["opms.user.management"].with_context(active_test=False).sudo().browse(link_id)
        if link.exists():
            link.write({"active": False})
        return request.redirect("/my/opms/user-management?success=%s" % quote_plus("OPMS profile blocked."))

    @http.route(["/my/opms/user-management/<int:link_id>/unblock"], type="http", auth="user", website=True, methods=["POST"])
    def portal_user_management_unblock(self, link_id, **post):
        self._check_user_management_admin()
        link = request.env["opms.user.management"].with_context(active_test=False).sudo().browse(link_id)
        if link.exists():
            link.write({"active": True})
        return request.redirect("/my/opms/user-management?success=%s" % quote_plus("OPMS profile unblocked."))

    @http.route(["/my/opms/user-management/bulk"], type="http", auth="user", website=True, methods=["POST"])
    def portal_user_management_bulk(self, **post):
        self._check_user_management_admin()
        selected_ids = self._parse_int_list(request.httprequest.form.getlist("selected_ids"))
        action = (post.get("bulk_action") or "").strip().lower()
        if not selected_ids:
            return request.redirect("/my/opms/user-management?error=%s" % quote_plus("Select at least one profile."))

        links = request.env["opms.user.management"].with_context(active_test=False).sudo().browse(selected_ids)
        if action == "delete":
            links.unlink()
            message = "Selected OPMS profiles deleted."
        elif action == "unblock":
            links.write({"active": True})
            message = "Selected OPMS profiles unblocked."
        else:
            links.write({"active": False})
            message = "Selected OPMS profiles blocked."
        return request.redirect("/my/opms/user-management?success=%s" % quote_plus(message))

    @http.route(["/my/opms/progress"], type="http", auth="user", website=True)
    def portal_load_progress(self, **kwargs):
        self._check_portal_user()
        progress = self._get_load_progress(kwargs)
        values = {
            "page_name": "opms_portal_progress",
            "progress": progress,
        }
        return request.render("opms_ecdhs.portal_opms_progress", values)

    @http.route(["/my/opms/dashboard"], type="http", auth="user", website=True)
    def portal_dashboard(self, **kwargs):
        self._check_portal_user()
        dashboard = self._get_dashboard_snapshot()
        values = {
            "page_name": "opms_portal_dashboard",
            "dashboard": dashboard,
            "dashboard_json": json.dumps(dashboard),
        }
        return request.render("opms_ecdhs.portal_opms_dashboard", values)

    @http.route(["/my/opms/evidence-documents"], type="http", auth="user", website=True)
    def portal_evidence_documents(self, **kwargs):
        self._check_portal_user()
        evidence_documents = self._get_evidence_documents(kwargs)
        values = {
            "page_name": "opms_portal_evidence_documents",
            "evidence_documents": evidence_documents,
        }
        return request.render("opms_ecdhs.portal_opms_evidence_documents", values)

    @http.route(["/my/opms/submissions"], type="http", auth="user", website=True)
    def portal_all_submissions(self, **kwargs):
        self._check_portal_user()
        values = {
            "page_name": "opms_portal_all_submissions",
            "highlighted_submission_id": self._int_or_none(kwargs.get("submission_id")) or "",
        }
        return request.render("opms_ecdhs.portal_opms_all_submissions_page", values)

    @http.route(["/my/opms/evidence/<int:evidence_id>/file"], type="http", auth="user", website=True)
    def portal_evidence_file(self, evidence_id, download=False, **kwargs):
        self._check_portal_user()
        evidence = request.env["opms.evidence"].browse(evidence_id)
        if not evidence.exists() or not evidence.active or not evidence.app_plan_id.active:
            return request.not_found()
        if not evidence.file:
            return request.not_found()

        file_name = evidence.file_name or f"evidence_{evidence.id}.bin"
        mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        disposition = "attachment" if str(download).lower() in {"1", "true", "yes"} else "inline"

        return request.make_response(
            base64.b64decode(evidence.file),
            headers=[
                ("Content-Type", mime_type),
                ("Content-Disposition", f'{disposition}; filename="{file_name}"'),
                ("Cache-Control", "private, max-age=0, no-cache"),
                ("X-Content-Type-Options", "nosniff"),
            ],
        )

    @http.route(["/my/opms/submit"], type="http", auth="user", website=True)
    def portal_submission_form(self, error=None, success=None, **kwargs):
        self._check_portal_user()
        options = self._get_hierarchy_options({})
        enable_narratives = request.env["ir.config_parameter"].sudo().get_param(
            "opms_ecdhs.enable_narratives", "1"
        ) != "0"
        values = {
            "page_name": "opms_portal_submission",
            "error": error,
            "success": success,
            "options": options,
            "selected_financial_year_id": str(self._get_current_financial_year_id() or ""),
            "target_summary": options.get("target_summary", {"visible": False}),
            "target_summary_json": json.dumps(options.get("target_summary", {"visible": False})),
            "target_input_json": json.dumps(options.get("target_input", {"visible": False})),
            "open_submission_periods": self._get_open_submission_periods(),
            "enable_narratives": enable_narratives,
        }
        return request.render("opms_ecdhs.portal_opms_submission_form", values)

    @http.route(["/my/opms/hierarchy/options"], type="http", auth="user", website=True)
    def portal_hierarchy_options(self, **kwargs):
        self._check_portal_user()
        payload = self._get_hierarchy_options(kwargs)
        return self._json_response(payload)

    def _generate_indicator_report_pdf(self, params):
        """Generate PDF report for indicator view with selected filters and quarter."""
        QuarterlyTarget = request.env["opms.quarterly.target"]
        domain = self._build_qt_domain(params)
        quarter_id = self._int_or_none(params.get("quarter_id"))
        clicked_quarter_code = (params.get("clicked_quarter_code") or "").strip().upper()
        status_filter = (params.get("status") or "").strip().lower()
        if status_filter not in {"", "unknown", "behind", "met", "exceeded"}:
            status_filter = ""

        if quarter_id:
            domain.append(("quarter_id", "=", quarter_id))

        qts = QuarterlyTarget.search(domain).sorted(
            lambda rec: (
                rec.output_indicator_id.name or "",
                rec.quarter_id.code or "",
            )
        )

        if clicked_quarter_code:
            qts = qts.filtered(lambda rec: (rec.quarter_id.code or "").strip().upper() == clicked_quarter_code)

        if status_filter:
            qts = qts.filtered(
                lambda rec: (rec.output_indicator_id._compare_target_and_actual(
                    rec.planned_target,
                    rec.output_indicator_id._aggregate_submission_actuals(rec.reporting_submission_ids),
                ).get("status") or "unknown") == status_filter
            )

        financial_year_id = self._int_or_none(params.get("financial_year_id")) or self._get_current_financial_year_id()
        fy = request.env["account.fiscal.year"].sudo().browse(financial_year_id) if financial_year_id else None
        programme_id = self._int_or_none(params.get("programme_id"))
        programme = request.env["opms.programme"].browse(programme_id) if programme_id else None
        sub_programme_id = self._int_or_none(params.get("sub_programme_id"))
        sub_programme = request.env["opms.sub.programme"].browse(sub_programme_id) if sub_programme_id else None
        directorate_id = self._int_or_none(params.get("directorate_id"))
        directorate = request.env["opms.directorate"].browse(directorate_id) if directorate_id else None

        if qts:
            sample_qt = qts[0]
            if not programme:
                programme = sample_qt.programme_id
            if not sub_programme:
                sub_programme = sample_qt.sub_programme_id

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=12,
            textColor=colors.HexColor('#000000'),
            spaceAfter=2,
            alignment=0,
            fontName='Helvetica-Bold',
        )

        year_style = ParagraphStyle(
            'YearStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#000000'),
            spaceAfter=8,
            alignment=0,
            fontName='Helvetica-Bold',
        )

        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            spaceAfter=4,
            alignment=0,
            fontName='Helvetica-Bold',
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#000000'),
            spaceAfter=2,
        )

        # Header information (requested format)
        app_name = ""
        if qts and qts[0].app_plan_id:
            app_name = (qts[0].app_plan_id.name or "").strip()
        if not app_name and fy:
            app_name = (fy.name or "").strip()
        if not app_name:
            app_name = "Annual Performance Plan"

        year_suffix = (fy.name or "").strip() if fy else ""
        app_line = f"Annual Performance Plan: {app_name}"
        if year_suffix and year_suffix not in app_name:
            app_line = f"{app_line} {year_suffix}"

        story.append(Paragraph(app_line, title_style))
        story.append(Spacer(1, 0.08*inch))

        if programme:
            programme_label = (self._hierarchy_label(programme) or "").upper()
            story.append(Paragraph(f"<b>Programme: {programme_label}</b>", heading_style))

        if sub_programme:
            sub_programme_label = (self._hierarchy_label(sub_programme) or "").upper()
            story.append(Paragraph(f"<b>{sub_programme_label}</b>", heading_style))

        strategic_obj = ""
        if qts and qts[0].output_id:
            strategic_obj = (qts[0].output_id.name or "").strip()
        if strategic_obj:
            story.append(Paragraph(f"<b>Strategic Objective: {strategic_obj}</b>", normal_style))

        story.append(Spacer(1, 0.2*inch))

        if clicked_quarter_code:
            story.append(Paragraph(f"<b>Quarter: {clicked_quarter_code}</b>", normal_style))
            story.append(Spacer(1, 0.08*inch))

        if qts:
            quarter_codes = sorted({(qt.quarter_id.code or "").upper() for qt in qts if qt.quarter_id})
            is_single_quarter = len(quarter_codes) == 1
            status_labels = {
                "met": "Achieved",
                "exceeded": "Exceeded",
                "behind": "Not-Achieved",
                "unknown": "Not Submitted",
            }

            table_text_style = ParagraphStyle(
                'TableText',
                parent=normal_style,
                fontSize=8,
                leading=9,
            )
            table_text_center_style = ParagraphStyle(
                'TableTextCenter',
                parent=table_text_style,
                alignment=1,
            )

            header_row = ['Output Indicator', 'Annual Target']
            actual_col_indices = [1]  # Annual Target is index 1
            if is_single_quarter:
                col_widths = [2.3*inch, 1.1*inch]
            else:
                col_widths = [2.15*inch, 1.05*inch]

            for qc in quarter_codes:
                for metric in ['Planned', 'Actual', 'Deviation', 'Status']:
                    header_row.append(f"{qc} {metric}")
                    if is_single_quarter:
                        if metric in ('Planned', 'Actual', 'Deviation'):
                            col_widths.append(0.95*inch)
                        else:
                            col_widths.append(0.9*inch)
                    else:
                        if metric in ('Planned', 'Actual', 'Deviation'):
                            col_widths.append(0.9*inch)
                        else:
                            col_widths.append(0.8*inch)
                    if metric == 'Actual':
                        actual_col_indices.append(len(header_row) - 1)

            data = [header_row]

            for qt in qts:
                indicator_name = (qt.output_indicator_id.name or "-").strip()
                indicator_type = (qt.output_indicator_id.indicator_type or "").strip().upper()
                if indicator_type:
                    indicator_label = f"{indicator_name} [{indicator_type}]"
                else:
                    indicator_label = indicator_name

                row = [
                    Paragraph(indicator_label[:90], table_text_style),
                    Paragraph(str(self._format_indicator_target_value(qt.output_indicator_id, qt.annual_target_id.target_value) or "-"), table_text_center_style),
                ]

                actual_value = qt.output_indicator_id._aggregate_submission_actuals(qt.reporting_submission_ids)
                comparison = qt.output_indicator_id._compare_target_and_actual(qt.planned_target, actual_value)
                q_code = (qt.quarter_id.code or "").upper()

                for qc in quarter_codes:
                    if qc == q_code:
                        status_code = str(comparison.get("status") or "unknown").strip().lower()
                        row.append(Paragraph(str(self._format_indicator_target_value(qt.output_indicator_id, qt.planned_target) or "-"), table_text_center_style))
                        row.append(Paragraph(str(comparison.get("actual_display") or "-"), table_text_center_style))
                        row.append(Paragraph(str(comparison.get("variance_display") or "-"), table_text_center_style))
                        row.append(Paragraph(status_labels.get(status_code, status_code.title() if status_code else "Not Submitted"), table_text_center_style))
                    else:
                        row.extend([
                            Paragraph("-", table_text_center_style),
                            Paragraph("-", table_text_center_style),
                            Paragraph("-", table_text_center_style),
                            Paragraph("-", table_text_center_style),
                        ])

                data.append(row)

            table = Table(data, colWidths=col_widths)

            cell_styles = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
            ]

            for col_idx in actual_col_indices:
                cell_styles.append(('BACKGROUND', (col_idx, 0), (col_idx, -1), colors.HexColor('#fee2e2')))
                cell_styles.append(('BACKGROUND', (col_idx, 0), (col_idx, 0), colors.HexColor('#fecaca')))

            table.setStyle(TableStyle(cell_styles))
            story.append(table)
        else:
            story.append(Paragraph("No data found for the selected filters.", normal_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @http.route(["/my/opms/submissions/all"], type="http", auth="user", website=True)
    def portal_submissions_all(self, **kwargs):
        """JSON endpoint returning all FY submissions for the Submissions section."""
        self._check_portal_user()
        payload = self._get_fy_all_submissions(kwargs)
        return self._json_response(payload)

    @http.route(["/my/opms/submission/<int:submission_id>/delete"], type="http", auth="user", website=True, methods=["POST"])
    def portal_submission_delete(self, submission_id, **kwargs):
        """Delete a submission only when its quarter is open."""
        self._check_portal_user()
        sub = self._get_portal_owned_submission(submission_id)
        if not sub.exists():
            return self._json_response({"ok": False, "error": "Submission not found or access denied."})
        if not sub.quarter_id._is_submission_open():
            return self._json_response({"ok": False, "error": "Cannot delete: the submission period for this quarter is currently closed."})
        sub.unlink()
        return self._json_response({"ok": True})

    @http.route(["/my/opms/evidence/<int:evidence_id>/delete"], type="http", auth="user", website=True, methods=["POST"])
    def portal_evidence_delete(self, evidence_id, **kwargs):
        """Delete an evidence file only when it belongs to the portal user and its quarter is open."""
        self._check_portal_user()
        evidence = self._get_portal_owned_evidence(evidence_id)
        if not evidence.exists():
            return self._json_response({"ok": False, "error": "Evidence file not found or access denied."})
        if not evidence.quarter_id._is_submission_open():
            return self._json_response({"ok": False, "error": "Cannot delete: the submission period for this quarter is currently closed."})
        evidence.unlink()
        return self._json_response({"ok": True})

    @http.route(["/my/opms/submission/<int:submission_id>/load"], type="http", auth="user", website=True)
    def portal_submission_load(self, submission_id, **kwargs):
        """Load a submission's data for inline editing."""
        self._check_portal_user()
        sub = self._get_portal_owned_submission(submission_id)
        if not sub.exists():
            return self._json_response({"ok": False, "error": "Submission not found or access denied."})
        if not sub.quarter_id._is_submission_open():
            return self._json_response({"ok": False, "error": "Cannot edit: the submission period for this quarter is currently closed."})
        measurement_type = (sub.output_indicator_id.measurement_type or "text") if sub.output_indicator_id else "text"
        actual_value_input = sub.actual_value or ""
        if measurement_type == "date":
            actual_value_input = self._format_display_date(sub.actual_value)
        return self._json_response({
            "ok": True,
            "id": sub.id,
            "name": sub.name or "",
            "actual_value": sub.actual_value or "",
            "actual_value_input": actual_value_input,
            "measurement_type": measurement_type,
            "comments": sub.comments or "",
            "reason_for_deviation": sub.reason_for_deviation or "",
            "remedial_actions": sub.remedial_actions or "",
            "evidence_count": len(sub.evidence_ids),
            "quarterly_target_id": sub.quarterly_target_id.id if sub.quarterly_target_id else None,
            "quarter_label": self._quarter_label(sub.quarter_id),
            "indicator_name": sub.output_indicator_id.name if sub.output_indicator_id else "-",
        })

    @http.route(["/my/opms/submission/<int:submission_id>/update"], type="http", auth="user", website=True, methods=["POST"])
    def portal_submission_update(self, submission_id, **post):
        """Update an existing submission when quarter is open."""
        self._check_portal_user()
        sub = self._get_portal_owned_submission(submission_id)
        if not sub.exists():
            return self._json_response({"ok": False, "error": "Submission not found or access denied."})
        if not sub.quarter_id._is_submission_open():
            return self._json_response({"ok": False, "error": "Cannot update: the submission period for this quarter is currently closed."})
        try:
            vals = {}
            if "comments" in post:
                vals["comments"] = self._safe_text(post["comments"], self._MAX_TEXT_LEN)
                if not vals["comments"]:
                    return self._json_response({"ok": False, "error": "Progress / Comments cannot be empty."})
            if "actual_value" in post:
                vals["actual_value"] = self._safe_text(post["actual_value"], self._MAX_ACTUAL_VALUE_LEN)
            if "reason_for_deviation" in post:
                vals["reason_for_deviation"] = self._safe_text(post["reason_for_deviation"], self._MAX_TEXT_LEN)
            if "remedial_actions" in post:
                vals["remedial_actions"] = self._safe_text(post["remedial_actions"], self._MAX_TEXT_LEN)
            if vals:
                sub.write(vals)

            uploaded_files = [f for f in request.httprequest.files.getlist("evidence_files") if getattr(f, "filename", None)]
            if uploaded_files:
                if len(uploaded_files) > self._MAX_FILE_COUNT:
                    raise ValidationError(_("You can upload a maximum of %s evidence files.") % self._MAX_FILE_COUNT)

                evidence_vals = []
                total_uploaded_bytes = 0
                for uploaded in uploaded_files:
                    safe_name = self._safe_filename(uploaded.filename)
                    content = uploaded.read()
                    if not content:
                        continue
                    self._validate_pdf_content(content)
                    content_size = len(content)
                    total_uploaded_bytes += content_size
                    if content_size > self._MAX_FILE_BYTES:
                        raise ValidationError(_("A file exceeds the maximum upload size of %s MB.") % int(self._MAX_FILE_BYTES / (1024 * 1024)))
                    if total_uploaded_bytes > self._MAX_TOTAL_UPLOAD_BYTES:
                        raise ValidationError(_("Total upload size exceeds the maximum allowed %s MB.") % int(self._MAX_TOTAL_UPLOAD_BYTES / (1024 * 1024)))

                    evidence_vals.append(
                        {
                            "name": safe_name,
                            "quarterly_target_id": sub.quarterly_target_id.id,
                            "narrative_id": (sub.narrative_ids[:1].id if sub.narrative_ids else False),
                            "reporting_submission_id": sub.id,
                            "file": base64.b64encode(content),
                            "file_name": safe_name,
                        }
                    )

                # Replace evidence only when new files are provided.
                if evidence_vals:
                    sub.evidence_ids.unlink()
                    request.env["opms.evidence"].create(evidence_vals)
        except ValidationError as e:
            return self._json_response({"ok": False, "error": str(e)})
        return self._json_response({"ok": True, "evidence_count": len(sub.evidence_ids)})

    @http.route(["/my/opms/view/download-report"], type="http", auth="user", website=True)
    def portal_indicator_view_download_pdf(self, **kwargs):
        """Download indicator report as PDF."""
        self._check_portal_user()
        try:
            pdf_bytes = self._generate_indicator_report_pdf(kwargs)
            fy_id = self._int_or_none(kwargs.get("financial_year_id"))
            fy = request.env["account.fiscal.year"].sudo().browse(fy_id) if fy_id else None
            filename = f"OPMS_Report_{(fy.name or 'Unknown').replace(' ', '_')}.pdf"
            response = request.make_response(pdf_bytes, [
                ("Content-Type", "application/pdf"),
                ("Content-Disposition", f"attachment; filename={filename}"),
            ])
            return response
        except Exception as e:
            return request.make_response(str(e), [("Content-Type", "text/plain")])

    @http.route(["/my/opms/view"], type="http", auth="user", website=True)
    def portal_indicator_view(self, error=None, success=None, **kwargs):
        self._check_portal_user()
        options = self._get_hierarchy_options({})
        selected_filters = self._serialize_filter_state(kwargs)
        enable_narratives = request.env["ir.config_parameter"].sudo().get_param(
            "opms_ecdhs.enable_narratives", "1"
        ) != "0"
        values = {
            "page_name": "opms_portal_indicator_view",
            "error": error,
            "success": success,
            "options": options,
            "selected_filters": selected_filters,
            "selected_filters_json": json.dumps(selected_filters),
            "enable_narratives": enable_narratives,
        }
        return request.render("opms_ecdhs.portal_opms_indicator_view", values)

    @http.route(["/my/opms/view/data"], type="http", auth="user", website=True)
    def portal_indicator_view_data(self, **kwargs):
        self._check_portal_user()
        payload = self._get_indicator_rows(kwargs)
        return self._json_response(payload)

    @http.route(["/my/opms/submit/create"], type="http", auth="user", website=True, methods=["POST"])
    def portal_submission_create(self, **post):
        user = self._check_portal_user()

        quarterly_target_id = self._int_or_none(post.get("quarterly_target_id"))
        if not quarterly_target_id:
            return request.redirect("/my/opms/submit?error=Please+select+a+Quarterly+Target")

        QuarterlyTarget = request.env["opms.quarterly.target"]
        quarterly_target = QuarterlyTarget.browse(quarterly_target_id)
        if not quarterly_target.exists():
            return request.redirect("/my/opms/submit?error=Selected+Quarterly+Target+does+not+exist")

        try:
            submission_name = self._safe_text(post.get("submission_name"), self._MAX_TEXT_LEN) or _("Portal Submission")
            comments = self._safe_text(post.get("comments"), self._MAX_TEXT_LEN)
            reason_for_deviation = self._safe_text(post.get("reason_for_deviation"), self._MAX_TEXT_LEN)
            remedial_actions = self._safe_text(post.get("remedial_actions"), self._MAX_TEXT_LEN)
            narrative_name = self._safe_text(post.get("narrative_name"), self._MAX_TEXT_LEN) or _("Portal Narrative")
            narrative_text = self._safe_text(post.get("narrative_text"), self._MAX_TEXT_LEN)
            actual_value = self._safe_text(post.get("actual_value"), self._MAX_ACTUAL_VALUE_LEN)
            aggregation_rule = quarterly_target.output_indicator_id.aggregation_rule or "latest"

            if not comments:
                return request.redirect("/my/opms/submit?error=Please+enter+Progress")

            self._validate_target_matches_posted_scope(quarterly_target, post)

            if aggregation_rule != "count" and not actual_value:
                return request.redirect("/my/opms/submit?error=Please+enter+the+actual+value+for+this+submission")

            # Validate and stage evidence files before creating any records.
            files = request.httprequest.files.getlist("evidence_files")
            if len(files) > self._MAX_FILE_COUNT:
                raise ValidationError(_("You can upload a maximum of %s evidence files.") % self._MAX_FILE_COUNT)

            total_uploaded_bytes = 0
            staged_evidence = []
            for uploaded in files:
                if not uploaded.filename:
                    continue
                safe_name = self._safe_filename(uploaded.filename)
                content = uploaded.read()
                if not content:
                    continue
                self._validate_pdf_content(content)
                content_size = len(content)
                total_uploaded_bytes += content_size
                if content_size > self._MAX_FILE_BYTES:
                    raise ValidationError(_("A file exceeds the maximum upload size of %s MB.") % int(self._MAX_FILE_BYTES / (1024 * 1024)))
                if total_uploaded_bytes > self._MAX_TOTAL_UPLOAD_BYTES:
                    raise ValidationError(_("Total upload size exceeds the maximum allowed %s MB.") % int(self._MAX_TOTAL_UPLOAD_BYTES / (1024 * 1024)))

                staged_evidence.append({
                    "name": safe_name,
                    "file_name": safe_name,
                    "file": base64.b64encode(content),
                })

            ReportingSubmission = request.env["opms.reporting.submission"]
            submission = ReportingSubmission.create(
                {
                    "name": submission_name,
                    "quarterly_target_id": quarterly_target.id,
                    "submitted_by": user.id,
                    "workflow_status": "draft",
                    "comments": comments,
                    "reason_for_deviation": reason_for_deviation,
                    "remedial_actions": remedial_actions,
                    "actual_value": actual_value,
                }
            )

            narrative = request.env["opms.narrative"]
            if narrative_text:
                narrative = request.env["opms.narrative"].create(
                    {
                        "name": narrative_name,
                        "quarterly_target_id": quarterly_target.id,
                        "narrative_text": narrative_text,
                        "reporting_submission_id": submission.id,
                    }
                )

            for item in staged_evidence:
                request.env["opms.evidence"].create(
                    {
                        "name": item["name"],
                        "quarterly_target_id": quarterly_target.id,
                        "narrative_id": narrative.id if narrative else False,
                        "reporting_submission_id": submission.id,
                        "file": item["file"],
                        "file_name": item["file_name"],
                    }
                )

        except ValidationError as error:
            return request.redirect(f"/my/opms/submit?error={quote_plus(f'{error}')}")
        except Exception as error:  # pragma: no cover - defensive portal response
            return request.redirect(f"/my/opms/submit?error={quote_plus(f'{error}')}")

        redirect_params = {
            "success": _("Submission created successfully"),
        }
        for key in (
            "financial_year_id",
            "programme_id",
            "sub_programme_id",
            "directorate_id",
            "output_id",
            "output_indicator_id",
            "quarter_id",
        ):
            value = post.get(key)
            if value:
                redirect_params[key] = value

        return request.redirect(f"/my/opms/view?{urlencode(redirect_params)}")
