import re

from odoo import api, fields, models


class OpmsAppAnnualReport(models.AbstractModel):
    _name = "report.opms_ecdhs.report_opms_app_annual_template"
    _description = "OPMS APP Annual Report"

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

    def _format_programme_title(self, programme_code, programme_name):
        name = (programme_name or "").strip()
        code = (programme_code or "").strip()
        if name.lower().startswith("programme"):
            return name.upper()
        if code:
            return f"PROGRAMME {code}: {name}".strip().upper()
        return f"PROGRAMME: {name}".strip().upper()

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        programme = self.env["opms.programme"].browse(data.get("programme_id"))
        annual_target_model = self.env["opms.annual.target"]
        output_model = self.env["opms.output"]

        domain = [("programme_id", "=", programme.id)] if programme else []
        annual_targets = annual_target_model.search(domain)

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
        ordered_years = aud_years + est_years + mtdp_years

        targets_index = {}
        for target in annual_targets:
            year_name = target.financial_year.name or ""
            if not year_name:
                continue
            key = (target.output_indicator_id.id, year_name)
            if key not in targets_index:
                targets_index[key] = target.target_value or "-"

        rows = []
        if programme:
            outputs = output_model.search([("programme_id", "=", programme.id)], order="code asc, name asc")
            programme_number = (programme.code or "").strip() or "1"
            row_number = 0
            for output in outputs:
                indicators = output.output_indicator_ids.sorted(key=lambda ind: ind.name or "")
                if not indicators:
                    row_number += 1
                    targets_by_year = {year: "-" for year in ordered_years}
                    rows.append(
                        {
                            "outcome_label": f"{programme_number}.{row_number}",
                            "output_name": output.name or "-",
                            "indicator_name": "-",
                            "targets": targets_by_year,
                        }
                    )
                    continue

                for indicator in indicators:
                    row_number += 1
                    targets_by_year = {}
                    for year in ordered_years:
                        targets_by_year[year] = targets_index.get((indicator.id, year), "-")
                    rows.append(
                        {
                            "outcome_label": f"{programme_number}.{row_number}",
                            "output_name": output.name or "-",
                            "indicator_name": indicator.name or "-",
                            "targets": targets_by_year,
                        }
                    )

        programme_code = (data.get("programme_code") or (programme.code if programme else "") or "").strip()
        programme_name = data.get("programme_name") or (programme.name if programme else "") or ""
        programme_title = self._format_programme_title(programme_code, programme_name)

        purpose_text = ""
        if programme:
            # Keep report resilient across model variations.
            if "notes" in programme._fields:
                purpose_text = (programme.notes or "").strip()
            elif "description" in programme._fields:
                purpose_text = (programme.description or "").strip()
        if not purpose_text:
            purpose_text = (
                f"To provide strategic and operational direction for {programme_name}."
                if programme_name
                else "-"
            )

        return {
            "docids": docids,
            "programme": programme,
            "programme_name": programme_name,
            "programme_code": programme_code,
            "programme_title": programme_title,
            "purpose_text": purpose_text,
            "aud_years": aud_years,
            "est_years": est_years,
            "mtdp_years": mtdp_years,
            "ordered_years": ordered_years,
            "rows": rows,
        }
