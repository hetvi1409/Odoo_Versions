import base64
import datetime as dt
import io
import re
import zipfile
import xml.etree.ElementTree as ET

from odoo import models, fields, _, api
from odoo.exceptions import UserError

XML_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"a": XML_NS}
EXCEL_EPOCH = dt.date(1899, 12, 30)


class RiskRegisterImport(models.TransientModel):
    """Import Operational / Fraud / Emerging Risk Register"""
    _name = "risk.register.import"
    _description = "Import Risk Register"

    file = fields.Binary(string="File", required=True)
    file_name = fields.Char(string="Filename")
    risk_register_type = fields.Selection(
        [
            ("strategic", "Strategic Risk Register"),
            ("operational", "Operational Risk Register"),
            ("fraud", "Fraud Risk Register"),
            ("project", "Project Risk Register"),
            ("business", "Business Unit Risks"),
            ("process", "Process Risks"),
            ("emerging", "Emerging Risk Register"),
        ],
        string="Type",
        required=True,
    )

    def action_import_xlsx(self):
        self.ensure_one()
        if not self.file:
            raise UserError(_("Please upload an .xlsx file."))

        workbook = self._load_workbook(base64.b64decode(self.file))
        cfg = self._get_import_config(self.risk_register_type)

        sheet_name = self._find_sheet_name(workbook, cfg["sheet_aliases"])
        if not sheet_name:
            raise UserError(
                _("Could not find the %s sheet in the uploaded workbook.")
                % self.risk_register_type
            )

        created, skipped = self._import_sheet(
            workbook[sheet_name],
            kind=cfg["kind"],
            risk_type_xmlid=cfg["risk_type_xmlid"],
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import completed"),
                "message": _("%s records created, %s duplicate rows skipped.") % (created, skipped),
                "type": "success",
                "sticky": False,
            },
        }

    def _get_import_config(self, risk_register_type):
        mapping = {
            "strategic": {
                "kind": "strategic",
                "risk_type_xmlid": "risk_universe_update.risk_type_strategic",
                "sheet_aliases": ["Strategic Risk Register"],
            },
            "operational": {
                "kind": "operational",
                "risk_type_xmlid": "risk_universe_update.risk_type_operational",
                "sheet_aliases": ["Operational Risk Register"],
            },
            "project": {
                "kind": "project",
                "risk_type_xmlid": "risk_universe_update.risk_type_project",
                "sheet_aliases": ["Project Risk Register"],
            },
            "fraud": {
                "kind": "fraud",
                "risk_type_xmlid": "risk_universe_update.risk_type_fraud",
                "sheet_aliases": ["Fraud Risk Register"],
            },
            "business": {
                "kind": "business",
                "risk_type_xmlid": "risk_universe_update.risk_type_business",
                "sheet_aliases": ["Business Risk Register"],
            },
            "process": {
                "kind": "process",
                "risk_type_xmlid": "risk_universe_update.risk_type_process",
                "sheet_aliases": ["Process Risk Register"],
            },
            "emerging": {
                "kind": "emerging",
                "risk_type_xmlid": "risk_universe_update.risk_type_emerging",
                "sheet_aliases": ["Emerging Risk Register"],
            },
        }

        if risk_register_type not in mapping:
            raise UserError(_("Import for %s is not implemented yet.") % risk_register_type)
        return mapping[risk_register_type]

    def _load_workbook(self, content):
        try:
            zf = zipfile.ZipFile(io.BytesIO(content))
        except zipfile.BadZipFile as exc:
            raise UserError(_("The uploaded file is not a valid .xlsx workbook.")) from exc

        shared_strings = self._read_shared_strings(zf)
        workbook_xml = ET.fromstring(zf.read("xl/workbook.xml"))
        rels_xml = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels_xml}

        sheets = {}
        for sheet in workbook_xml.find("a:sheets", NS):
            sheet_name = (sheet.attrib.get("name") or "").strip()
            rel_id = sheet.attrib[f"{{{REL_NS}}}id"]
            target = rel_map[rel_id].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            sheets[sheet_name] = self._read_sheet_rows(zf.read(target), shared_strings)

        return sheets

    def _read_shared_strings(self, zf):
        if "xl/sharedStrings.xml" not in zf.namelist():
            return []

        root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
        values = []
        for si in root.findall("a:si", NS):
            parts = []
            for node in si.iter(f"{{{XML_NS}}}t"):
                parts.append(node.text or "")
            values.append("".join(parts))
        return values

    def _read_sheet_rows(self, sheet_bytes, shared_strings):
        root = ET.fromstring(sheet_bytes)
        sheet_data = root.find("a:sheetData", NS)
        rows = []

        if sheet_data is None:
            return rows

        for row in sheet_data.findall("a:row", NS):
            values = {}
            for cell in row.findall("a:c", NS):
                ref = cell.attrib.get("r", "")
                col_index = self._column_index(ref)
                values[col_index] = self._cell_value(cell, shared_strings)

            if values:
                max_col = max(values)
                rows.append([values.get(i, "") for i in range(1, max_col + 1)])

        return rows

    def _cell_value(self, cell, shared_strings):
        cell_type = cell.attrib.get("t")
        v = cell.find("a:v", NS)

        if cell_type == "s" and v is not None:
            idx = int(v.text or "0")
            return shared_strings[idx] if idx < len(shared_strings) else ""

        if cell_type == "inlineStr":
            return "".join(node.text or "" for node in cell.iter(f"{{{XML_NS}}}t"))

        if v is None:
            return ""
        return v.text or ""

    def _column_index(self, cell_ref):
        match = re.match(r"([A-Z]+)", cell_ref or "")
        if not match:
            return 0
        result = 0
        for ch in match.group(1):
            result = result * 26 + (ord(ch) - 64)
        return result

    def _find_sheet_name(self, workbook, aliases):
        normalized_aliases = [self._normalize(a) for a in aliases]
        for sheet_name in workbook.keys():
            normalized_name = self._normalize(sheet_name)
            if any(alias in normalized_name for alias in normalized_aliases):
                return sheet_name
        return False

    def _import_sheet(self, rows, kind, risk_type_xmlid):
        header_row_idx, header_map = self._find_header_row(rows, kind)
        if header_map is None:
            raise UserError(_("Could not detect the header row for the selected sheet."))

        created = 0
        skipped = 0

        for row in rows[header_row_idx + 1:]:
            vals = self._build_vals(row, header_map, kind, risk_type_xmlid)
            if not vals:
                continue

            domain = [("risk_type_id", "=", vals["risk_type_id"])]
            if vals.get("sequence"):
                domain.append(("sequence", "=", vals["sequence"]))
            elif vals.get("name"):
                domain.append(("name", "=", vals["name"]))

            exists = self.env["oi_risk_management.risk"].sudo().search(domain, limit=1)
            if exists:
                skipped += 1
                continue

            self.env["oi_risk_management.risk"].sudo().with_context(
                skip_risk_import_notifications=True,
                mail_create_nolog=True,
                mail_notrack=True,
            ).create(vals)
            created += 1

        return created, skipped

    def _find_header_row(self, rows, kind):
        def norm_row(row):
            return [self._normalize(v) for v in row]

        if not rows:
            return None, None

        if kind == "fraud":
            row = rows[0]
            vals = norm_row(row)
            if len(vals) >= 5 and vals[:5] in (
                    ["link to outcome", "risk number", "chief directorate", "sub-directorate", "risk category"],
                    ["link to outcome", "risk number", "chief directorate", "sub directorate", "risk category"],
            ):
                return 0, self._header_map(row)

        if kind == "strategic":
            for idx, row in enumerate(rows[:25]):
                vals = norm_row(row)
                if len(vals) >= 4 and vals[:4] in (
                        ["link to outcome", "risk description", "risk category", "risk number"],
                        ["link to outcome", "risk number", "risk category", "risk description"],
                ):
                    return idx, self._header_map(row)

        for idx, row in enumerate(rows[:25]):
            vals = norm_row(row)
            if len(vals) < 4:
                continue

            if vals[:4] == [
                "link to outcome",
                "risk number",
                "unit",
                "risk category",
            ]:
                return idx, self._header_map(row)

        return None, None

    def _header_map(self, row):
        mapping = {}
        for idx, value in enumerate(row):
            key = self._normalize(value)
            if key:
                mapping[key] = idx
        return mapping

    def _build_vals(self, row, header_map, kind, risk_type_xmlid):
        if kind == "fraud":
            return self._build_fraud_vals(row, header_map, risk_type_xmlid)
        if kind == "strategic":
            return self._build_strategic_vals(row, header_map, risk_type_xmlid)
        return self._build_operational_vals(row, header_map, risk_type_xmlid)

    def _build_strategic_vals(self, row, header_map, risk_type_xmlid):
        risk_number = self._get(row, header_map, "risk number")
        risk_description = self._get(row, header_map, "risk description", "risk name")
        link_to_outcome = self._get(row, header_map, "link to outcome")

        if not any([risk_number, risk_description, link_to_outcome]):
            return False

        department = self._resolve_department(self._get(row, header_map, "unit"))
        category = self._resolve_category(self._get(row, header_map, "risk category"))
        activity = self._resolve_activity(
            link_to_outcome or risk_description or risk_number,
            department,
            category,
        )
        owner = self._resolve_employee(self._get(row, header_map, "risk owner"), department)
        action_owner = self._resolve_department(self._get(row, header_map, "action owner"))
        timeline = self._parse_timeline(self._get(row, header_map, "timeline"))

        return {
            "risk_type_id": self.env.ref(risk_type_xmlid).id,
            "sequence": self._clean(risk_number, collapse=True) or False,
            "name": self._build_risk_name(risk_number, risk_description),
            "uncertainty": self._clean(risk_description, collapse=False) or False,
            "main_cause": self._clean(self._get(row, header_map, "risk causes"), collapse=False) or False,
            "consequences": self._clean(self._get(row, header_map, "consequences"), collapse=False) or False,
            "link_to_outcome": self._clean(link_to_outcome, collapse=False) or False,
            "department_id": department.id if department else False,
            "unit": department.id if department else False,
            "activity_id": activity.id,
            "category_id": category.id if category else False,
            "owner_id": owner.id if owner else False,
            "employee_id": owner.id if owner else False,
            "impact_value": self._as_int(self._get(row, header_map, "impact value", "impact")),
            "likelihood_value": self._as_int(self._get(row, header_map, "likelihood value", "likelihood")),
            "current_controls": self._clean(self._get(row, header_map, "current controls"), collapse=False) or False,
            "control_effectiveness": self._clean(self._get(row, header_map, "control effectiveness"),
                                                 collapse=True) or False,
            "effectiveness_rating": self._as_float(self._get(row, header_map, "effectiveness rating", "effectiveness")),
            "risk_appetite": self._clean(self._get(row, header_map, "risk appetite"), collapse=False) or False,
            "risk_tolerance": self._clean(self._get(row, header_map, "risk tolerance"), collapse=True) or False,
            "risk_response_treatment": self._clean(
                self._get(row, header_map, "risk response treatment", "suggested risk response"),
                collapse=True,
            ) or False,
            "improve_management_of_risk": self._clean(
                self._get(row, header_map, "action to improve management of the risk"),
                collapse=False,
            ) or False,
            "action_owner": action_owner.id if action_owner else False,
            "timeline": timeline or False,
        }

    def _build_operational_vals(self, row, header_map, risk_type_xmlid):
        risk_number = self._get(row, header_map, "risk number")
        risk_description = self._get(row, header_map, "risk description")
        link_to_outcome = self._get(row, header_map, "link to outcome")

        if not any([risk_number, risk_description, link_to_outcome]):
            return False

        category = self._resolve_category(self._get(row, header_map, "risk category"))
        department = self._resolve_department(self._get(row, header_map, "unit"))
        activity = self._resolve_activity(link_to_outcome or risk_description or risk_number, department, category)
        owner = self._resolve_employee(self._get(row, header_map, "risk owner"), department)
        action_owner = self._resolve_department(self._get(row, header_map, "action owner"))
        timeline = self._parse_timeline(self._get(row, header_map, "timeline"))

        return {
            "risk_type_id": self.env.ref(risk_type_xmlid).id,
            "sequence": self._clean(risk_number, collapse=True) or False,
            "name": self._build_risk_name(risk_number, risk_description),
            "uncertainty": self._clean(risk_description, collapse=False) or False,
            "main_cause": self._clean(self._get(row, header_map, "risk causes"), collapse=False) or False,
            "consequences": self._clean(self._get(row, header_map, "consequences"), collapse=False) or False,
            "link_to_outcome": self._clean(link_to_outcome, collapse=False) or False,
            "department_id": department.id if department else False,
            "unit": department.id if department else False,
            "activity_id": activity.id,
            "category_id": category.id if category else False,
            "owner_id": owner.id if owner else False,
            "employee_id": owner.id if owner else False,
            "impact_value": self._as_int(self._get(row, header_map, "impact value")),
            "likelihood_value": self._as_int(self._get(row, header_map, "likelihood value")),
            "current_controls": self._clean(self._get(row, header_map, "current controls"), collapse=False) or False,
            "control_effectiveness": self._clean(self._get(row, header_map, "control effectiveness"),
                                                 collapse=True) or False,
            "effectiveness_rating": self._as_float(self._get(row, header_map, "effectiveness rating")),
            "risk_appetite": self._clean(self._get(row, header_map, "risk appetite"), collapse=False) or False,
            "risk_tolerance": self._clean(self._get(row, header_map, "risk tolerance"), collapse=True) or False,
            "risk_response_treatment": self._clean(self._get(row, header_map, "suggested risk response"),
                                                   collapse=True) or False,
            "improve_management_of_risk": self._clean(
                self._get(row, header_map, "action to improve management of the risk"),
                collapse=False,
            ) or False,
            "action_owner": action_owner.id if action_owner else False,
            "timeline": timeline or False,
        }

    def _build_fraud_vals(self, row, header_map, risk_type_xmlid):
        risk_number = self._get(row, header_map, "risk number")
        risk_name = self._get(row, header_map, "risk name")
        risk_description = self._get(row, header_map, "risk description")
        link_to_outcome = self._get(row, header_map, "link to outcome")

        if not any([risk_number, risk_name, risk_description, link_to_outcome]):
            return False

        chief_department = self._resolve_department(self._get(row, header_map, "chief directorate"))
        sub_department = self._resolve_department(self._get(row, header_map, "sub-directorate"))
        department = chief_department or sub_department
        category = self._resolve_category(self._get(row, header_map, "risk category"))
        activity = self._resolve_activity(
            link_to_outcome or risk_name or risk_description or risk_number,
            department,
            category,
        )
        owner = self._resolve_employee(self._get(row, header_map, "risk owner"), department)
        action_owner = self._resolve_department(self._get(row, header_map, "action owner"))
        timeline = self._parse_timeline(self._get(row, header_map, "timeline"))

        return {
            "risk_type_id": self.env.ref(risk_type_xmlid).id,
            "sequence": self._clean(risk_number, collapse=True) or False,
            "name": self._build_risk_name(risk_number, risk_name or risk_description),
            "uncertainty": self._clean(risk_description, collapse=False) or False,
            "main_cause": self._clean(self._get(row, header_map, "risk causes"), collapse=False) or False,
            "consequences": self._clean(self._get(row, header_map, "consequences"), collapse=False) or False,
            "link_to_outcome": self._clean(link_to_outcome, collapse=False) or False,
            "department_id": department.id if department else False,
            "chief_directorate_id": chief_department.id if chief_department else False,
            "directorate_id": sub_department.id if sub_department else False,
            "activity_id": activity.id,
            "category_id": category.id if category else False,
            "owner_id": owner.id if owner else False,
            "employee_id": owner.id if owner else False,
            "impact_value": self._as_int(self._get(row, header_map, "impact value")),
            "likelihood_value": self._as_int(self._get(row, header_map, "likelihood value")),
            "current_controls": self._clean(self._get(row, header_map, "current controls"), collapse=False) or False,
            "control_effectiveness": self._clean(self._get(row, header_map, "control effectiveness"),
                                                 collapse=True) or False,
            "effectiveness_rating": self._as_float(self._get(row, header_map, "effectiveness rating")),
            "risk_appetite": self._clean(self._get(row, header_map, "risk appetite"), collapse=False) or False,
            "risk_tolerance": self._clean(self._get(row, header_map, "risk tolerance"), collapse=True) or False,
            "risk_response_treatment": self._clean(self._get(row, header_map, "risk response treatment"),
                                                   collapse=True) or False,
            "improve_management_of_risk": self._clean(
                self._get(row, header_map, "action to improve management of the risk"),
                collapse=False,
            ) or False,
            "action_owner": action_owner.id if action_owner else False,
            "timeline": timeline or False,
        }

    def _resolve_activity(self, name, department, category):
        name = self._clean(name, collapse=True)
        if not name:
            name = _("Imported Risk Activity")

        domain = [("name", "=", name)]
        if department:
            domain.append(("department_id", "=", department.id))
        if category:
            domain.append(("category_id", "=", category.id))

        activity = self.env["oi_risk_management.activity"].sudo().search(domain, limit=1)
        if activity:
            return activity

        vals = {"name": name}
        if department:
            vals["department_id"] = department.id
        if category:
            vals["category_id"] = category.id
        return self.env["oi_risk_management.activity"].sudo().create(vals)

    def _resolve_category(self, name):
        name = self._clean(name, collapse=True)
        if not name:
            return False

        category = self.env["oi_risk_management.activity_category"].sudo().search([("name", "=", name)], limit=1)
        if category:
            return category
        return self.env["oi_risk_management.activity_category"].sudo().create({"name": name})

    def _resolve_department(self, name):
        name = self._clean(name, collapse=True)
        if not name:
            return False

        department = self.env["hr.department"].sudo().search([("name", "=", name)], limit=1)
        if department:
            return department

        department = self.env["hr.department"].sudo().search([("name", "ilike", name)], limit=1)
        if department:
            return department

        return self.env["hr.department"].sudo().create({"name": name})

    def _resolve_employee(self, name, department):
        name = self._clean(name, collapse=True)
        if not name:
            if department and department.manager_id:
                return department.manager_id
            if department and department.employee_ids:
                return department.employee_ids[:1]
            return False

        employee = self.env["hr.employee"].sudo().search([("name", "=", name)], limit=1)
        if employee:
            return employee

        employee = self.env["hr.employee"].sudo().search([("name", "ilike", name)], limit=1)
        if employee:
            return employee

        if department and department.manager_id:
            return department.manager_id
        if department and department.employee_ids:
            return department.employee_ids[:1]
        return False

    def _build_risk_name(self, risk_number, title):
        risk_number = self._clean(risk_number, collapse=True)
        title = self._clean(title, collapse=True)
        if risk_number and title:
            return f"{risk_number} - {title}"
        return risk_number or title or _("Imported Risk")

    def _get(self, row, header_map, *names):
        for name in names:
            idx = header_map.get(self._normalize(name))
            if idx is not None and idx < len(row):
                value = row[idx]
                if value not in (None, ""):
                    return value
        return ""

    def _clean(self, value, collapse=False):
        if value in (None, False):
            return ""
        text = str(value).replace("\r", "")
        if collapse:
            text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _normalize(self, value):
        return re.sub(r"\s+", " ", self._clean(value, collapse=True).lower()).strip()

    def _as_int(self, value):
        text = self._clean(value, collapse=True)
        if not text:
            return False
        try:
            return int(float(text.replace(",", "")))
        except (TypeError, ValueError):
            return False

    def _as_float(self, value):
        text = self._clean(value, collapse=True)
        if not text:
            return False
        try:
            return float(text.replace(",", ""))
        except (TypeError, ValueError):
            return False

    def _parse_timeline(self, value):
        text = self._clean(value, collapse=True)
        if not text:
            return False

        if re.fullmatch(r"\d+(\.0+)?", text):
            try:
                serial = int(float(text))
                return (EXCEL_EPOCH + dt.timedelta(days=serial)).isoformat()
            except Exception:
                pass

        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
            try:
                return dt.datetime.strptime(text, fmt).date().isoformat()
            except ValueError:
                continue

        return text