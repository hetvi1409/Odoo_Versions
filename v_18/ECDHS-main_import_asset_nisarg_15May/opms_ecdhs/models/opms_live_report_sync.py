import json

from odoo import api, fields, models


class OpmsLiveReportSync(models.Model):
    _name = "opms.live.report.sync"
    _description = "OPMS Live Spreadsheet/Dashboard Sync"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    auto_refresh = fields.Boolean(default=True)

    spreadsheet_document_id = fields.Many2one("documents.document", ondelete="set null")
    dashboard_id = fields.Many2one("spreadsheet.dashboard", ondelete="set null")

    report_payload = fields.Text(required=True)
    last_sync_at = fields.Datetime(readonly=True)
    last_sync_error = fields.Text(readonly=True)

    def _payload_report_template(self, payload):
        if not payload:
            return "sub_entity"
        explicit = payload.get("report_template")
        if explicit in {"app_annual", "sub_entity"}:
            return explicit
        if payload.get("report_scope"):
            return "sub_entity"
        if payload.get("programme_id"):
            return "app_annual"
        return "sub_entity"

    def _build_snapshot_from_payload(self, payload):
        report_template = self._payload_report_template(payload)
        if report_template == "app_annual":
            report_model = self.env["report.opms_ecdhs.report_opms_app_annual_template"]
        else:
            report_model = self.env["report.opms_ecdhs.report_opms_sub_entity_template"]
        wizard_model = self.env["opms.sub.entity.report.wizard"]
        report_values = report_model._get_report_values([], data=payload)
        return wizard_model._build_spreadsheet_snapshot(report_values)

    def _link_matches_scope(self, link, programme_ids=None, sub_programme_ids=None, directorate_ids=None):
        try:
            payload = json.loads(link.report_payload or "{}")
        except Exception:
            return False

        report_template = self._payload_report_template(payload)
        programme_ids = set(programme_ids or [])
        sub_programme_ids = set(sub_programme_ids or [])
        directorate_ids = set(directorate_ids or [])

        if report_template == "app_annual":
            return bool(payload.get("programme_id") in programme_ids)

        scope_type = payload.get("report_scope") or "sub_programme"
        if scope_type == "sub_programme":
            return bool(payload.get("sub_programme_id") in sub_programme_ids)
        if scope_type == "directorate":
            return bool(payload.get("directorate_id") in directorate_ids)
        if scope_type == "both":
            return bool(
                payload.get("sub_programme_id") in sub_programme_ids
                or payload.get("directorate_id") in directorate_ids
            )
        return False

    @api.model
    def refresh_links_for_scope(self, programme_ids=None, sub_programme_ids=None, directorate_ids=None):
        links = self.search([("active", "=", True), ("auto_refresh", "=", True)])
        impacted = links.filtered(
            lambda link: self._link_matches_scope(
                link,
                programme_ids=programme_ids,
                sub_programme_ids=sub_programme_ids,
                directorate_ids=directorate_ids,
            )
        )
        if impacted:
            impacted.refresh_from_backend()
        return impacted

    def refresh_from_backend(self):
        for record in self:
            if not record.active or not record.auto_refresh:
                continue
            if not record.report_payload:
                continue

            try:
                payload = json.loads(record.report_payload)
                snapshot = record._build_snapshot_from_payload(payload)
                snapshot_json = json.dumps(snapshot)

                if record.spreadsheet_document_id:
                    record.spreadsheet_document_id.with_context(opms_skip_live_sync_propagation=True).write(
                        {
                            "handler": "spreadsheet",
                            "mimetype": "application/o-spreadsheet",
                            "spreadsheet_data": snapshot_json,
                        }
                    )

                if record.dashboard_id:
                    record.dashboard_id.with_context(opms_skip_live_sync_propagation=True).write(
                        {"spreadsheet_data": snapshot_json}
                    )

                record.write(
                    {
                        "last_sync_at": fields.Datetime.now(),
                        "last_sync_error": False,
                    }
                )
            except Exception as error:
                record.write({"last_sync_error": str(error)})

    @api.model
    def cron_refresh_live_links(self):
        links = self.search([("active", "=", True), ("auto_refresh", "=", True)])
        links.refresh_from_backend()

    @api.model
    def register_or_update_link(self, spreadsheet, dashboard, payload, name):
        if not payload:
            return self.env["opms.live.report.sync"]

        link = self.env["opms.live.report.sync"]
        if spreadsheet:
            link = self.search([("spreadsheet_document_id", "=", spreadsheet.id)], limit=1)
        if not link and dashboard:
            link = self.search([("dashboard_id", "=", dashboard.id)], limit=1)

        values = {
            "name": name or "OPMS Live Sync",
            "spreadsheet_document_id": spreadsheet.id if spreadsheet else False,
            "dashboard_id": dashboard.id if dashboard else False,
            "report_payload": json.dumps(payload),
            "active": True,
            "auto_refresh": True,
        }

        if link:
            link.write(values)
            return link
        return self.create(values)


def _opms_live_sync_scope_snapshot(self):
    scope = {
        "programme_ids": set(),
        "sub_programme_ids": set(),
        "directorate_ids": set(),
    }
    for record in self:
        if record._name == "opms.programme":
            scope["programme_ids"].add(record.id)
        elif "programme_id" in record._fields and record.programme_id:
            scope["programme_ids"].add(record.programme_id.id)

        if record._name == "opms.sub.programme":
            scope["sub_programme_ids"].add(record.id)
        elif "sub_programme_id" in record._fields and record.sub_programme_id:
            scope["sub_programme_ids"].add(record.sub_programme_id.id)

        if record._name == "opms.directorate":
            scope["directorate_ids"].add(record.id)
        elif "directorate_id" in record._fields and record.directorate_id:
            scope["directorate_ids"].add(record.directorate_id.id)
    return scope


def _opms_trigger_live_sync_refresh(self, previous_scope=None):
    current_scope = _opms_live_sync_scope_snapshot(self)
    if previous_scope:
        current_scope["programme_ids"].update(previous_scope.get("programme_ids", set()))
        current_scope["sub_programme_ids"].update(previous_scope.get("sub_programme_ids", set()))
        current_scope["directorate_ids"].update(previous_scope.get("directorate_ids", set()))

    self.env["opms.live.report.sync"].sudo().refresh_links_for_scope(
        programme_ids=sorted(current_scope["programme_ids"]),
        sub_programme_ids=sorted(current_scope["sub_programme_ids"]),
        directorate_ids=sorted(current_scope["directorate_ids"]),
    )


def _opms_skip_sync(env):
    return env.context.get("opms_skip_live_sync_refresh") or env.context.get("opms_import_app_matrix")


class OpmsProgrammeLiveSync(models.Model):
    _inherit = "opms.programme"

    _opms_live_sync_scope_snapshot = _opms_live_sync_scope_snapshot
    _opms_trigger_live_sync_refresh = _opms_trigger_live_sync_refresh

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not _opms_skip_sync(self.env):
            records._opms_trigger_live_sync_refresh()
        return records

    def write(self, vals):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().write(vals)
        if not _opms_skip_sync(self.env):
            self._opms_trigger_live_sync_refresh(previous_scope=previous_scope)
        return result

    def unlink(self):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().unlink()
        if not _opms_skip_sync(self.env):
            self.env["opms.live.report.sync"].sudo().refresh_links_for_scope(
                programme_ids=sorted(previous_scope["programme_ids"]),
                sub_programme_ids=sorted(previous_scope["sub_programme_ids"]),
                directorate_ids=sorted(previous_scope["directorate_ids"]),
            )
        return result


class OpmsSubProgrammeLiveSync(models.Model):
    _inherit = "opms.sub.programme"

    _opms_live_sync_scope_snapshot = _opms_live_sync_scope_snapshot
    _opms_trigger_live_sync_refresh = _opms_trigger_live_sync_refresh

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not _opms_skip_sync(self.env):
            records._opms_trigger_live_sync_refresh()
        return records

    def write(self, vals):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().write(vals)
        if not _opms_skip_sync(self.env):
            self._opms_trigger_live_sync_refresh(previous_scope=previous_scope)
        return result

    def unlink(self):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().unlink()
        if not _opms_skip_sync(self.env):
            self.env["opms.live.report.sync"].sudo().refresh_links_for_scope(
                programme_ids=sorted(previous_scope["programme_ids"]),
                sub_programme_ids=sorted(previous_scope["sub_programme_ids"]),
                directorate_ids=sorted(previous_scope["directorate_ids"]),
            )
        return result


class OpmsDirectorateLiveSync(models.Model):
    _inherit = "opms.directorate"

    _opms_live_sync_scope_snapshot = _opms_live_sync_scope_snapshot
    _opms_trigger_live_sync_refresh = _opms_trigger_live_sync_refresh

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not _opms_skip_sync(self.env):
            records._opms_trigger_live_sync_refresh()
        return records

    def write(self, vals):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().write(vals)
        if not _opms_skip_sync(self.env):
            self._opms_trigger_live_sync_refresh(previous_scope=previous_scope)
        return result

    def unlink(self):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().unlink()
        if not _opms_skip_sync(self.env):
            self.env["opms.live.report.sync"].sudo().refresh_links_for_scope(
                programme_ids=sorted(previous_scope["programme_ids"]),
                sub_programme_ids=sorted(previous_scope["sub_programme_ids"]),
                directorate_ids=sorted(previous_scope["directorate_ids"]),
            )
        return result


class OpmsOutputLiveSync(models.Model):
    _inherit = "opms.output"

    _opms_live_sync_scope_snapshot = _opms_live_sync_scope_snapshot
    _opms_trigger_live_sync_refresh = _opms_trigger_live_sync_refresh

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not _opms_skip_sync(self.env):
            records._opms_trigger_live_sync_refresh()
        return records

    def write(self, vals):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().write(vals)
        if not _opms_skip_sync(self.env):
            self._opms_trigger_live_sync_refresh(previous_scope=previous_scope)
        return result

    def unlink(self):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().unlink()
        if not _opms_skip_sync(self.env):
            self.env["opms.live.report.sync"].sudo().refresh_links_for_scope(
                programme_ids=sorted(previous_scope["programme_ids"]),
                sub_programme_ids=sorted(previous_scope["sub_programme_ids"]),
                directorate_ids=sorted(previous_scope["directorate_ids"]),
            )
        return result


class OpmsOutputIndicatorLiveSync(models.Model):
    _inherit = "opms.output.indicator"

    _opms_live_sync_scope_snapshot = _opms_live_sync_scope_snapshot
    _opms_trigger_live_sync_refresh = _opms_trigger_live_sync_refresh

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not _opms_skip_sync(self.env):
            records._opms_trigger_live_sync_refresh()
        return records

    def write(self, vals):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().write(vals)
        if not _opms_skip_sync(self.env):
            self._opms_trigger_live_sync_refresh(previous_scope=previous_scope)
        return result

    def unlink(self):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().unlink()
        if not _opms_skip_sync(self.env):
            self.env["opms.live.report.sync"].sudo().refresh_links_for_scope(
                programme_ids=sorted(previous_scope["programme_ids"]),
                sub_programme_ids=sorted(previous_scope["sub_programme_ids"]),
                directorate_ids=sorted(previous_scope["directorate_ids"]),
            )
        return result


class OpmsAnnualTargetLiveSync(models.Model):
    _inherit = "opms.annual.target"

    _opms_live_sync_scope_snapshot = _opms_live_sync_scope_snapshot
    _opms_trigger_live_sync_refresh = _opms_trigger_live_sync_refresh

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not _opms_skip_sync(self.env):
            records._opms_trigger_live_sync_refresh()
        return records

    def write(self, vals):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().write(vals)
        if not _opms_skip_sync(self.env):
            self._opms_trigger_live_sync_refresh(previous_scope=previous_scope)
        return result

    def unlink(self):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().unlink()
        if not _opms_skip_sync(self.env):
            self.env["opms.live.report.sync"].sudo().refresh_links_for_scope(
                programme_ids=sorted(previous_scope["programme_ids"]),
                sub_programme_ids=sorted(previous_scope["sub_programme_ids"]),
                directorate_ids=sorted(previous_scope["directorate_ids"]),
            )
        return result


class OpmsQuarterlyTargetLiveSync(models.Model):
    _inherit = "opms.quarterly.target"

    _opms_live_sync_scope_snapshot = _opms_live_sync_scope_snapshot
    _opms_trigger_live_sync_refresh = _opms_trigger_live_sync_refresh

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not _opms_skip_sync(self.env):
            records._opms_trigger_live_sync_refresh()
        return records

    def write(self, vals):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().write(vals)
        if not _opms_skip_sync(self.env):
            self._opms_trigger_live_sync_refresh(previous_scope=previous_scope)
        return result

    def unlink(self):
        previous_scope = self._opms_live_sync_scope_snapshot()
        result = super().unlink()
        if not _opms_skip_sync(self.env):
            self.env["opms.live.report.sync"].sudo().refresh_links_for_scope(
                programme_ids=sorted(previous_scope["programme_ids"]),
                sub_programme_ids=sorted(previous_scope["sub_programme_ids"]),
                directorate_ids=sorted(previous_scope["directorate_ids"]),
            )
        return result


class DocumentsDocument(models.Model):
    _inherit = "documents.document"

    def write(self, vals):
        result = super().write(vals)
        if self.env.context.get("opms_skip_live_sync_propagation"):
            return result

        if "spreadsheet_data" not in vals:
            return result

        changed_docs = self.filtered(lambda rec: rec.handler == "spreadsheet")
        if not changed_docs:
            return result

        links = self.env["opms.live.report.sync"].sudo().search(
            [
                ("active", "=", True),
                ("spreadsheet_document_id", "in", changed_docs.ids),
                ("dashboard_id", "!=", False),
            ]
        )
        for link in links:
            link.dashboard_id.with_context(opms_skip_live_sync_propagation=True).write(
                {"spreadsheet_data": link.spreadsheet_document_id.spreadsheet_data}
            )
            link.write({"last_sync_at": fields.Datetime.now(), "last_sync_error": False})

        return result


class SpreadsheetRevision(models.Model):
    _inherit = "spreadsheet.revision"

    @api.model_create_multi
    def create(self, vals_list):
        revisions = super().create(vals_list)
        if self.env.context.get("opms_skip_live_sync_propagation"):
            return revisions

        doc_revisions = revisions.filtered(
            lambda rev: rev.res_model == "documents.document" and rev.res_id
        )
        if not doc_revisions:
            return revisions

        document_ids = list({rev.res_id for rev in doc_revisions})
        links = self.env["opms.live.report.sync"].sudo().search(
            [
                ("active", "=", True),
                ("spreadsheet_document_id", "in", document_ids),
                ("dashboard_id", "!=", False),
            ]
        )
        if not links:
            return revisions

        documents = self.env["documents.document"].sudo().browse(document_ids)
        now = fields.Datetime.now()
        for document in documents:
            linked = links.filtered(
                lambda link: link.spreadsheet_document_id.id == document.id and link.dashboard_id
            )
            if not linked:
                continue

            # Manual spreadsheet edits are stored as collaborative revisions.
            # Mirror the document's full revision chain to each linked dashboard so
            # the dashboard always reflects the current state of the spreadsheet.
            for dashboard in linked.mapped("dashboard_id").sudo():
                # Step 1: Reset dashboard to document's base binary, which automatically
                # clears the dashboard's existing revisions and snapshot via
                # SpreadsheetMixin.write → _delete_collaborative_data().
                dashboard.with_context(
                    opms_skip_live_sync_propagation=True,
                ).write({
                    "spreadsheet_binary_data": document.sudo().spreadsheet_binary_data,
                })

                # Step 2: Restore the collaborative snapshot so clients don't need
                # to replay every revision from scratch.
                doc_snapshot = document.sudo().spreadsheet_snapshot
                if doc_snapshot:
                    dashboard.with_context(
                        preserve_spreadsheet_revisions=True,
                        opms_skip_live_sync_propagation=True,
                    ).write({"spreadsheet_snapshot": doc_snapshot})

                # Step 3: Copy the full revision chain from the document to the dashboard.
                # Use opms_skip_live_sync_propagation so the revision copies created
                # inside _copy_revisions_to do not recursively re-trigger this hook.
                document.sudo().with_context(
                    opms_skip_live_sync_propagation=True,
                )._copy_revisions_to(dashboard)

            linked.write({"last_sync_at": now, "last_sync_error": False})

        return revisions
