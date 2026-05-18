import re

from odoo import api, fields, models


class OpmsSubEntityReport(models.AbstractModel):
    _name = "report.opms_ecdhs.report_opms_sub_entity_template"
    _description = "OPMS Sub-Programme and Directorate Report"

    def _fiscal_year_start(self, fiscal_year):
        if fiscal_year.date_from:
            return fiscal_year.date_from.year
        name = (fiscal_year.name or "").strip()
        match = re.match(r"(\d{4})", name)
        if match:
            return int(match.group(1))
        return 0

    def _fy_label_from_start_year(self, start_year, fy_by_start):
        fy = fy_by_start.get(start_year)
        if fy and fy.name:
            return fy.name
        return f"{start_year}-{str(start_year + 1)[-2:]}"

    def _format_scope_title(self, scope_type, scope_code, scope_name):
        label = "SUB-PROGRAMME" if scope_type == "sub_programme" else "DIRECTORATE"
        code = (scope_code or "").strip()
        name = (scope_name or "").strip()
        if code and name:
            return f"{code} {name}".upper()
        if name:
            return f"{label}: {name}".upper()
        if code:
            return f"{label}: {code}".upper()
        return label

    def _scope_model_name(self, scope_type):
        return "opms.sub.programme" if scope_type == "sub_programme" else "opms.directorate"

    def _scope_field_name(self, scope_type):
        return "sub_programme_id" if scope_type == "sub_programme" else "directorate_id"

    def _get_scope_record(self, data):
        scope_type = data.get("report_scope") or "sub_programme"
        scope_model = self.env[self._scope_model_name(scope_type)]
        scope_id = data.get("scope_id") or data.get(self._scope_field_name(scope_type))
        return scope_type, scope_model.browse(scope_id)

    def _get_record_for_scope(self, scope_type, data):
        model = self.env[self._scope_model_name(scope_type)]
        if scope_type == "sub_programme":
            return model.browse(data.get("sub_programme_id") or data.get("scope_id"))
        return model.browse(data.get("directorate_id") or data.get("scope_id"))

    def _build_fiscal_year_buckets(self, annual_targets):
        fiscal_year_model = self.env["account.fiscal.year"]
        all_fys = fiscal_year_model.search([])
        fy_by_start = {}
        for fy in all_fys:
            start = self._fiscal_year_start(fy)
            if start and start not in fy_by_start:
                fy_by_start[start] = fy

        app_plan_years = annual_targets.mapped("app_plan_id.financial_year")
        target_years = annual_targets.mapped("financial_year")
        anchor_candidates = (app_plan_years or target_years).sorted(
            key=lambda fy: (self._fiscal_year_start(fy), fy.name or "")
        )
        if anchor_candidates:
            estimated_start_year = self._fiscal_year_start(anchor_candidates[-1])
        else:
            today = fields.Date.context_today(self)
            estimated_start_year = today.year if today.month >= 4 else today.year - 1

        audited_start_years = list(range(estimated_start_year - 4, estimated_start_year))
        estimated_start_years = [estimated_start_year]
        mtdp_start_years = [estimated_start_year + 1, estimated_start_year + 2, estimated_start_year + 3]

        aud_years = [self._fy_label_from_start_year(y, fy_by_start) for y in audited_start_years]
        est_years = [self._fy_label_from_start_year(y, fy_by_start) for y in estimated_start_years]
        mtdp_years = [self._fy_label_from_start_year(y, fy_by_start) for y in mtdp_start_years]
        return aud_years, est_years, mtdp_years

    def _get_scope_purpose(self, scope_record, scope_type):
        purpose_text = ""
        if scope_record:
            if "notes" in scope_record._fields:
                purpose_text = (scope_record.notes or "").strip()
            elif "description" in scope_record._fields:
                purpose_text = (scope_record.description or "").strip()

        if purpose_text:
            return purpose_text

        scope_label = "sub-programme" if scope_type == "sub_programme" else "directorate"
        if scope_record and scope_record.name:
            return f"To provide strategic and operational direction for {scope_label} {scope_record.name}."
        return "-"

    def _build_annual_rows(self, scope_field, scope_record, ordered_years):
        annual_targets = self.env["opms.annual.target"].search([(scope_field, "=", scope_record.id)])
        outputs = self.env["opms.output"].search([(scope_field, "=", scope_record.id)], order="code asc, name asc")

        targets_index = {}
        for target in annual_targets:
            year_name = target.financial_year.name or ""
            if not year_name:
                continue
            key = (target.output_indicator_id.id, year_name)
            if key not in targets_index:
                targets_index[key] = target.target_value or "-"

        rows = []
        row_number = 0
        for output in outputs:
            indicators = output.output_indicator_ids.filtered(lambda ind: getattr(ind, scope_field).id == scope_record.id)
            indicators = indicators.sorted(key=lambda ind: ((ind.output_id.code or ""), ind.name or ""))
            if not indicators:
                row_number += 1
                rows.append(
                    {
                        "outcome_label": f"1.{row_number}",
                        "output_name": output.name or "-",
                        "indicator_name": "-",
                        "targets": {year: "-" for year in ordered_years},
                    }
                )
                continue

            for indicator in indicators:
                row_number += 1
                rows.append(
                    {
                        "outcome_label": f"1.{row_number}",
                        "output_name": output.name or "-",
                        "indicator_name": indicator.name or "-",
                        "targets": {
                            year: targets_index.get((indicator.id, year), "-") for year in ordered_years
                        },
                    }
                )

        return annual_targets, rows

    def _build_quarterly_rows(self, scope_field, scope_record, fiscal_year):
        annual_targets = self.env["opms.annual.target"].search(
            [(scope_field, "=", scope_record.id), ("financial_year", "=", fiscal_year.id)]
        )
        annual_targets = annual_targets.sorted(
            key=lambda target: (
                target.output_id.code or "",
                target.output_id.name or "",
                target.output_indicator_id.name or "",
            )
        )
        quarterly_targets = self.env["opms.quarterly.target"].search(
            [(scope_field, "=", scope_record.id), ("financial_year", "=", fiscal_year.id)]
        )

        quarter_index = {}
        for target in quarterly_targets:
            quarter_code = (target.quarter_id.code or "").lower()
            if not quarter_code:
                continue
            quarter_index[(target.output_indicator_id.id, quarter_code)] = target.planned_target or "-"

        rows = []
        row_number = 0
        seen_indicator_ids = set()
        for target in annual_targets:
            indicator = target.output_indicator_id
            if not indicator or indicator.id in seen_indicator_ids:
                continue
            seen_indicator_ids.add(indicator.id)
            row_number += 1
            rows.append(
                {
                    "indicator_label": f"1.{row_number}",
                    "indicator_name": indicator.name or "-",
                    "annual_target": target.target_value or "-",
                    "q1": quarter_index.get((indicator.id, "q1"), "-"),
                    "q2": quarter_index.get((indicator.id, "q2"), "-"),
                    "q3": quarter_index.get((indicator.id, "q3"), "-"),
                    "q4": quarter_index.get((indicator.id, "q4"), "-"),
                }
            )

        return rows

    def _build_scope_section(self, scope_type, scope_record, fiscal_year, data):
        if not scope_record:
            return {
                "scope_type": scope_type,
                "scope_record": scope_record,
                "scope_title": "-",
                "purpose_text": "-",
                "selected_fiscal_year": fiscal_year,
                "selected_fiscal_year_name": data.get("fiscal_year_name") or (fiscal_year.name if fiscal_year else ""),
                "aud_years": [],
                "est_years": [],
                "mtdp_years": [],
                "ordered_years": [],
                "annual_rows": [],
                "quarterly_rows": [],
            }

        scope_field = self._scope_field_name(scope_type)
        annual_targets, annual_rows = self._build_annual_rows(scope_field, scope_record, [])
        aud_years, est_years, mtdp_years = self._build_fiscal_year_buckets(annual_targets)
        ordered_years = aud_years + est_years + mtdp_years
        annual_targets, annual_rows = self._build_annual_rows(scope_field, scope_record, ordered_years)
        quarterly_rows = self._build_quarterly_rows(scope_field, scope_record, fiscal_year) if fiscal_year else []

        return {
            "scope_type": scope_type,
            "scope_record": scope_record,
            "scope_title": self._format_scope_title(
                scope_type,
                scope_record.code,
                scope_record.name,
            ),
            "purpose_text": self._get_scope_purpose(scope_record, scope_type),
            "selected_fiscal_year": fiscal_year,
            "selected_fiscal_year_name": data.get("fiscal_year_name") or (fiscal_year.name if fiscal_year else ""),
            "aud_years": aud_years,
            "est_years": est_years,
            "mtdp_years": mtdp_years,
            "ordered_years": ordered_years,
            "annual_rows": annual_rows,
            "quarterly_rows": quarterly_rows,
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        scope_type = data.get("report_scope") or "sub_programme"
        fiscal_year = self.env["account.fiscal.year"].browse(data.get("fiscal_year_id"))

        sections = []
        if scope_type == "both":
            sub_programme_record = self._get_record_for_scope("sub_programme", data)
            directorate_record = self._get_record_for_scope("directorate", data)
            sections.append(self._build_scope_section("sub_programme", sub_programme_record, fiscal_year, data))
            sections.append(self._build_scope_section("directorate", directorate_record, fiscal_year, data))
        else:
            scope_record = self._get_record_for_scope(scope_type, data)
            sections.append(self._build_scope_section(scope_type, scope_record, fiscal_year, data))

        first_section = sections[0] if sections else {}

        return {
            "docids": docids,
            "scope_type": scope_type,
            "sections": sections,
            "scope_record": first_section.get("scope_record"),
            "scope_title": first_section.get("scope_title", "-"),
            "purpose_text": first_section.get("purpose_text", "-"),
            "selected_fiscal_year": fiscal_year,
            "selected_fiscal_year_name": first_section.get("selected_fiscal_year_name", ""),
            "aud_years": first_section.get("aud_years", []),
            "est_years": first_section.get("est_years", []),
            "mtdp_years": first_section.get("mtdp_years", []),
            "ordered_years": first_section.get("ordered_years", []),
            "annual_rows": first_section.get("annual_rows", []),
            "quarterly_rows": first_section.get("quarterly_rows", []),
        }