import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class OpmsSubEntityReportWizard(models.TransientModel):
    _name = "opms.sub.entity.report.wizard"
    _description = "OPMS Reporting Wizard"

    report_template = fields.Selection(
        [
            ("app_annual", "APP Annual Report"),
            ("sub_entity", "Sub-Programme / Directorate Report"),
        ],
        string="Report",
        required=True,
        default="app_annual",
    )
    programme_id = fields.Many2one(
        "opms.programme",
        string="Programme",
    )

    report_scope = fields.Selection(
        [("sub_programme", "Sub-Programme"), ("directorate", "Directorate"), ("both", "Both")],
        string="Report Type",
        required=True,
        default="sub_programme",
    )
    sub_programme_id = fields.Many2one(
        "opms.sub.programme",
        string="Sub-Programme",
    )
    directorate_id = fields.Many2one(
        "opms.directorate",
        string="Directorate",
    )
    fiscal_year_id = fields.Many2one(
        "account.fiscal.year",
        string="Fiscal Year",
        ondelete="restrict",
    )
    output_mode = fields.Selection(
        [("pdf", "PDF Report"), ("spreadsheet", "Spreadsheet")],
        string="Output Format",
        required=True,
        default="pdf",
    )
    spreadsheet_sync_mode = fields.Selection(
        [
            ("none", "Do Not Sync Spreadsheet"),
            ("create", "Create New Spreadsheet Report"),
            ("update", "Update Existing Spreadsheet Report"),
        ],
        string="Spreadsheet Sync",
        required=True,
        default="none",
    )
    spreadsheet_name = fields.Char(
        string="Spreadsheet Name",
        default="OPMS Report",
    )
    existing_spreadsheet_id = fields.Many2one(
        "documents.document",
        string="Existing Spreadsheet Report",
        domain="[('handler', '=', 'spreadsheet'), ('name', 'ilike', 'OPMS Report')]",
    )
    dashboard_sync_mode = fields.Selection(
        [
            ("none", "Do Not Sync Dashboard"),
            ("create", "Add New Dashboard"),
            ("update", "Update Existing Dashboard"),
        ],
        string="Dashboard Sync",
        required=True,
        default="none",
    )
    dashboard_id = fields.Many2one(
        "spreadsheet.dashboard",
        string="Existing Dashboard",
        domain="[('name', 'ilike', 'OPMS Report')]",
    )
    dashboard_name = fields.Char(
        string="Dashboard Name",
        default="OPMS Report Dashboard",
    )
    dashboard_group_id = fields.Many2one(
        "spreadsheet.dashboard.group",
        string="Dashboard Section",
    )
    open_dashboard_after_generation = fields.Boolean(
        string="Open Dashboard After Generation",
        default=False,
    )
    result_spreadsheet_id = fields.Many2one(
        "documents.document",
        string="Generated Spreadsheet",
        readonly=True,
        copy=False,
    )
    result_dashboard_id = fields.Many2one(
        "spreadsheet.dashboard",
        string="Generated Dashboard",
        readonly=True,
        copy=False,
    )
    generated_spreadsheet_url = fields.Char(
        string="Generated Spreadsheet",
        compute="_compute_result_links",
        readonly=True,
    )
    generated_dashboard_url = fields.Char(
        string="Generated Dashboard",
        compute="_compute_result_links",
        readonly=True,
    )
    result_spreadsheet_url = fields.Char(
        string="Spreadsheet Link",
        compute="_compute_result_links",
        readonly=True,
    )
    result_dashboard_url = fields.Char(
        string="Dashboard Link",
        compute="_compute_result_links",
        readonly=True,
    )

    @api.onchange("sub_programme_id")
    def _onchange_sub_programme_id(self):
        for wizard in self:
            if wizard.directorate_id and wizard.directorate_id.sub_programme_id != wizard.sub_programme_id:
                wizard.directorate_id = False

    @api.onchange("output_mode")
    def _onchange_output_mode(self):
        for wizard in self:
            if wizard.output_mode != "spreadsheet":
                wizard.spreadsheet_sync_mode = "none"
                wizard.existing_spreadsheet_id = False
                wizard.dashboard_sync_mode = "none"
                wizard.dashboard_id = False
                wizard.dashboard_group_id = False
                wizard.open_dashboard_after_generation = False
            elif wizard.spreadsheet_sync_mode == "none":
                wizard.spreadsheet_sync_mode = "create"

    def _build_spreadsheet_url(self, spreadsheet):
        if not spreadsheet:
            return False
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "").rstrip("/")
        return f"{base_url}/odoo/documents/spreadsheet/{spreadsheet.id}?debug=1" if base_url else False

    def _build_dashboard_url(self, dashboard):
        if not dashboard:
            return False
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "").rstrip("/")
        return f"{base_url}/odoo/dashboards?debug=1&dashboard_id={dashboard.id}" if base_url else False

    @api.depends("result_spreadsheet_id", "result_dashboard_id")
    def _compute_result_links(self):
        for wizard in self:
            spreadsheet_url = wizard._build_spreadsheet_url(wizard.result_spreadsheet_id)
            dashboard_url = wizard._build_dashboard_url(wizard.result_dashboard_id)
            wizard.generated_spreadsheet_url = spreadsheet_url
            wizard.generated_dashboard_url = dashboard_url
            wizard.result_spreadsheet_url = spreadsheet_url
            wizard.result_dashboard_url = dashboard_url

    def _validate_scope_inputs(self):
        self.ensure_one()
        if self.report_template == "app_annual":
            if not self.programme_id:
                raise ValidationError("Select a programme before printing this report.")
            return

        if self.report_scope == "sub_programme":
            if not self.sub_programme_id:
                raise ValidationError("Select a sub-programme before printing this report.")
            return
        if self.report_scope == "directorate" and not self.directorate_id:
            raise ValidationError("Select a directorate before printing this report.")
        if self.report_scope == "both":
            if not self.sub_programme_id:
                raise ValidationError("Select a sub-programme for the 'Both' report option.")
            if not self.directorate_id:
                raise ValidationError("Select a directorate for the 'Both' report option.")
            if self.directorate_id.sub_programme_id != self.sub_programme_id:
                raise ValidationError("The selected directorate must belong to the selected sub-programme.")

    def _validate_output_inputs(self):
        self.ensure_one()
        if self.report_template == "sub_entity" and not self.fiscal_year_id:
            raise ValidationError("Select a fiscal year before generating this report.")

        if self.output_mode != "spreadsheet":
            self.spreadsheet_sync_mode = "none"
            self.existing_spreadsheet_id = False
            self.dashboard_sync_mode = "none"
            self.dashboard_id = False
            self.dashboard_group_id = False
            self.open_dashboard_after_generation = False

        if self.output_mode == "spreadsheet" and self.spreadsheet_sync_mode == "none":
            self.spreadsheet_sync_mode = "create"

        if self.spreadsheet_sync_mode == "update" and not self.existing_spreadsheet_id:
            raise ValidationError("Select an existing spreadsheet report to update.")

        if self.dashboard_sync_mode == "update" and not self.dashboard_id:
            raise ValidationError("Select an existing dashboard to update.")

        if self.dashboard_sync_mode == "create" and not self.dashboard_group_id:
            raise ValidationError("Select a dashboard section when adding a new dashboard.")

        if self._requires_spreadsheet_features() and not self._has_spreadsheet_features():
            raise UserError(
                _(
                    "Spreadsheet features require the modules documents_spreadsheet and spreadsheet_dashboard to be installed."
                )
            )

    def _requires_spreadsheet_features(self):
        self.ensure_one()
        return (
            self.output_mode == "spreadsheet"
            or self.spreadsheet_sync_mode != "none"
            or self.dashboard_sync_mode != "none"
        )

    def _has_spreadsheet_features(self):
        return (
            "documents.document" in self.env
            and "spreadsheet.dashboard" in self.env
            and "spreadsheet.dashboard.group" in self.env
        )

    def _build_report_data_payload(self):
        self.ensure_one()
        scope_record = self.sub_programme_id if self.report_scope == "sub_programme" else self.directorate_id
        if self.report_scope == "both":
            scope_record = self.sub_programme_id
        return {
            "report_template": self.report_template,
            "wizard_id": self.id,
            "report_scope": self.report_scope,
            "sub_programme_id": self.sub_programme_id.id,
            "directorate_id": self.directorate_id.id,
            "scope_id": scope_record.id if scope_record else False,
            "scope_name": scope_record.name if scope_record else "",
            "scope_code": (getattr(scope_record, "code", "") or "") if scope_record else "",
            "fiscal_year_id": self.fiscal_year_id.id,
            "fiscal_year_name": self.fiscal_year_id.name or "",
        }

    def _build_app_annual_data_payload(self):
        self.ensure_one()
        return {
            "report_template": self.report_template,
            "wizard_id": self.id,
            "programme_id": self.programme_id.id,
            "programme_name": self.programme_id.name,
            "programme_code": self.programme_id.code or "",
        }

    def _get_report_values_for_output(self, report_data):
        self.ensure_one()
        if self.report_template == "app_annual":
            report_model = self.env["report.opms_ecdhs.report_opms_app_annual_template"]
            return report_model._get_report_values([], data=report_data)

        report_model = self.env["report.opms_ecdhs.report_opms_sub_entity_template"]
        return report_model._get_report_values([], data=report_data)

    def _build_snapshot_sections(self, report_values):
        self.ensure_one()
        if self.report_template == "app_annual":
            return [
                {
                    "scope_title": report_values.get("programme_title") or report_values.get("programme_name") or "APP Annual Report",
                    "purpose_text": report_values.get("purpose_text") or "-",
                    "ordered_years": report_values.get("ordered_years", []),
                    "aud_years": report_values.get("aud_years", []),
                    "est_years": report_values.get("est_years", []),
                    "mtdp_years": report_values.get("mtdp_years", []),
                    "annual_rows": report_values.get("rows", []),
                }
            ]

        return report_values.get("sections", [])

    def _default_report_name(self):
        self.ensure_one()
        if self.report_template == "app_annual":
            return f"OPMS APP Annual Report - {self.programme_id.display_name}"
        scope_label = {
            "sub_programme": self.sub_programme_id.display_name,
            "directorate": self.directorate_id.display_name,
            "both": "Sub-Programme and Directorate",
        }.get(self.report_scope, "Report")
        fy = self.fiscal_year_id.name or ""
        return f"OPMS Report - {scope_label} ({fy})"

    def _spreadsheet_styles(self):
        return {
            "1": {"bold": True, "textColor": "#FFFFFF", "fillColor": "#079C4B"},
            "2": {"bold": True},
            "3": {},
            "4": {"bold": True, "textColor": "#079C4B"},
            "5": {"bold": True, "textColor": "#FFFFFF", "fillColor": "#079C4B"},
        }

    def _to_a1(self, row, col):
        letters = ""
        while col:
            col, rem = divmod(col - 1, 26)
            letters = chr(65 + rem) + letters
        return f"{letters}{row}"

    def _set_cell(self, cells, row, col, content, style="3"):
        cells[self._to_a1(row, col)] = {
            "content": "" if content is None else str(content),
            "style": int(style),
        }

    def _write_table_annual(self, cells, start_row, section):
        ordered_years = section.get("ordered_years", [])
        total_cols = max(4, 3 + len(ordered_years))
        self._set_cell(cells, start_row, 1, "Outcomes, Outputs, Performance Indicators and Targets", "2")

        row = start_row + 1
        self._set_cell(cells, row, 1, "Outcome", "1")
        self._set_cell(cells, row, 2, "Outputs", "1")
        self._set_cell(cells, row, 3, "Output Indicators", "1")
        self._set_cell(cells, row, 4, "Annual Targets", "1")
        for i, year in enumerate(ordered_years):
            self._set_cell(cells, row, 4 + i, year, "1")

        row += 1
        segment_labels = []
        segment_labels.extend(["Audited/Actual performance"] * len(section.get("aud_years", [])))
        segment_labels.extend(["Estimated performance"] * len(section.get("est_years", [])))
        segment_labels.extend(["MTDP Period"] * len(section.get("mtdp_years", [])))
        for i, segment in enumerate(segment_labels):
            self._set_cell(cells, row, 4 + i, segment, "1")

        row += 1
        annual_rows = section.get("annual_rows", [])
        if not annual_rows:
            self._set_cell(cells, row, 1, "No output indicators found for this selection.", "3")
            return row + 1

        for line in annual_rows:
            self._set_cell(cells, row, 1, line.get("outcome_label") or "-", "5")
            self._set_cell(cells, row, 2, line.get("output_name") or "-", "3")
            self._set_cell(cells, row, 3, line.get("indicator_name") or "-", "3")
            for i, year in enumerate(ordered_years):
                self._set_cell(cells, row, 4 + i, line.get("targets", {}).get(year, "-"), "3")
            row += 1
        return row + 1

    def _write_table_quarterly(self, cells, start_row, section):
        title = "Indicators, Annual and Quarterly Targets"
        if section.get("selected_fiscal_year_name"):
            title = f"{title} ({section.get('selected_fiscal_year_name')})"
        self._set_cell(cells, start_row, 1, title, "2")

        row = start_row + 1
        headers = ["Ref", "Output Indicators", f"Annual Target {section.get('selected_fiscal_year_name') or ''}", "1st", "2nd", "3rd", "4th"]
        for idx, header in enumerate(headers, start=1):
            self._set_cell(cells, row, idx, header, "1")

        row += 1
        quarter_rows = section.get("quarterly_rows", [])
        if not quarter_rows:
            self._set_cell(cells, row, 1, "No annual or quarterly targets found for the selected fiscal year.", "3")
            return row + 1

        for line in quarter_rows:
            self._set_cell(cells, row, 1, line.get("indicator_label") or "-", "5")
            self._set_cell(cells, row, 2, line.get("indicator_name") or "-", "3")
            self._set_cell(cells, row, 3, line.get("annual_target") or "-", "3")
            self._set_cell(cells, row, 4, line.get("q1") or "-", "3")
            self._set_cell(cells, row, 5, line.get("q2") or "-", "3")
            self._set_cell(cells, row, 6, line.get("q3") or "-", "3")
            self._set_cell(cells, row, 7, line.get("q4") or "-", "3")
            row += 1
        return row + 1

    def _build_spreadsheet_snapshot(self, report_values):
        styles = self._spreadsheet_styles()
        sheets = []
        sections = self._build_snapshot_sections(report_values)
        for index, section in enumerate(sections, start=1):
            cells = {}
            row = 1
            self._set_cell(cells, row, 1, section.get("scope_title") or "-", "4")
            row += 1
            self._set_cell(cells, row, 1, f"Purpose: {section.get('purpose_text') or '-'}", "2")
            row += 2
            row = self._write_table_annual(cells, row, section)
            if "quarterly_rows" in section:
                row = self._write_table_quarterly(cells, row, section)

            sheets.append(
                {
                    "id": f"sh{index}",
                    "name": (section.get("scope_title") or f"Section {index}")[:30],
                    "colNumber": 16,
                    "rowNumber": max(200, row + 20),
                    "rows": {},
                    "cols": {},
                    "merges": [],
                    "cells": cells,
                    "conditionalFormats": [],
                    "figures": [],
                    "areGridLinesVisible": True,
                }
            )

        return {
            "version": 10,
            "sheets": sheets,
            "styles": styles,
            "borders": {},
            "formats": {},
            "entities": {},
            "revisionId": "START_REVISION",
            "uniqueFigureIds": True,
        }

    def _create_documents_spreadsheet(self, snapshot, name):
        document_model = self.env["documents.document"]
        spreadsheet = document_model.create(
            {
                "name": name,
                "handler": "spreadsheet",
                "mimetype": "application/o-spreadsheet",
                "spreadsheet_data": json.dumps(snapshot),
            }
        )
        return spreadsheet

    def _update_documents_spreadsheet(self, spreadsheet, snapshot, name):
        spreadsheet.write(
            {
                "name": name,
                "handler": "spreadsheet",
                "mimetype": "application/o-spreadsheet",
                "spreadsheet_data": json.dumps(snapshot),
            }
        )
        return spreadsheet

    def _sync_dashboard(self, snapshot, spreadsheet_name):
        self.ensure_one()
        if self.dashboard_sync_mode == "none":
            return self.env["spreadsheet.dashboard"]

        if self.dashboard_sync_mode == "update":
            vals = {
                "name": self.dashboard_name or self.dashboard_id.name,
                "spreadsheet_data": json.dumps(snapshot),
            }
            self.dashboard_id.write(vals)
            return self.dashboard_id

        dashboard = self.env["spreadsheet.dashboard"].create(
            {
                "name": self.dashboard_name or f"{spreadsheet_name} Dashboard",
                "dashboard_group_id": self.dashboard_group_id.id,
                "spreadsheet_data": json.dumps(snapshot),
            }
        )
        return dashboard

    def _sync_spreadsheet_and_dashboard(self, report_data):
        self.ensure_one()
        report_values = self._get_report_values_for_output(report_data)
        snapshot = self._build_spreadsheet_snapshot(report_values)

        target_name = (self.spreadsheet_name or "").strip() or self._default_report_name()
        if self.output_mode == "spreadsheet" and self.spreadsheet_sync_mode == "none":
            self.spreadsheet_sync_mode = "create"

        spreadsheet = self.env["documents.document"]
        if self.spreadsheet_sync_mode == "update":
            spreadsheet = self._update_documents_spreadsheet(self.existing_spreadsheet_id, snapshot, target_name)
        elif self.spreadsheet_sync_mode == "create":
            spreadsheet = self._create_documents_spreadsheet(snapshot, target_name)
        elif self.dashboard_sync_mode != "none":
            spreadsheet = self._create_documents_spreadsheet(snapshot, target_name)

        dashboard = self.env["spreadsheet.dashboard"]
        if self.dashboard_sync_mode != "none":
            if not spreadsheet:
                spreadsheet = self._create_documents_spreadsheet(snapshot, target_name)
            dashboard = self._sync_dashboard(snapshot, target_name)

        if spreadsheet or dashboard:
            self.env["opms.live.report.sync"].sudo().register_or_update_link(
                spreadsheet=spreadsheet,
                dashboard=dashboard,
                payload=report_data,
                name=target_name,
            )

        return spreadsheet, dashboard

    def _build_reopen_wizard_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "OPMS Reports",
            "res_model": "opms.sub.entity.report.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    def _run_generation(self):
        self.ensure_one()
        self._validate_scope_inputs()
        self._validate_output_inputs()

        data = self._build_app_annual_data_payload() if self.report_template == "app_annual" else self._build_report_data_payload()
        spreadsheet, dashboard = self._sync_spreadsheet_and_dashboard(data)

        self.write(
            {
                "result_spreadsheet_id": spreadsheet.id if spreadsheet else False,
                "result_dashboard_id": dashboard.id if dashboard else False,
            }
        )
        return data, spreadsheet, dashboard

    def action_generate_with_links(self):
        self.ensure_one()
        self._run_generation()
        return self._build_reopen_wizard_action()

    def action_print_report(self):
        self.ensure_one()
        data, spreadsheet, dashboard = self._run_generation()

        if self.report_template == "app_annual":
            if self.output_mode == "spreadsheet":
                if self.open_dashboard_after_generation and dashboard:
                    return {
                        "type": "ir.actions.client",
                        "tag": "action_spreadsheet_dashboard",
                        "params": {"dashboard_id": dashboard.id},
                    }
                if not spreadsheet:
                    raise UserError(_("No spreadsheet was generated. Please choose a spreadsheet sync mode."))
                return spreadsheet.action_open_spreadsheet()

            app_report_wizard = self.env["opms.app.annual.report.wizard"].create(
                {
                    "programme_id": self.programme_id.id,
                }
            )
            return self.env.ref("opms_ecdhs.action_report_opms_app_annual_report").report_action(app_report_wizard, data=data)

        if self.output_mode == "spreadsheet":
            if self.open_dashboard_after_generation and dashboard:
                return {
                    "type": "ir.actions.client",
                    "tag": "action_spreadsheet_dashboard",
                    "params": {"dashboard_id": dashboard.id},
                }
            if not spreadsheet:
                raise UserError(_("No spreadsheet was generated. Please choose a spreadsheet sync mode."))
            return spreadsheet.action_open_spreadsheet()

        return self.env.ref("opms_ecdhs.action_report_opms_sub_entity_report").report_action(self, data=data)