from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import xlrd
import datetime


class APPImportWizard(models.TransientModel):
    _name = "app.import.wizard"
    _description = "APP Import Wizard"

    file = fields.Binary(string="Excel File", required=True)
    filename = fields.Char(string="Filename")

    # -----------------------------
    # SAFE DATE PARSER
    # -----------------------------
    def _excel_date(self, value):
        if not value or value in ["Not Applicable", "N/A"]:
            return False

        # direct python date
        if isinstance(value, datetime.date):
            return value

        # string date
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d %b %y", "%d/%m/%Y"):
                try:
                    return datetime.datetime.strptime(value, fmt).date()
                except Exception:
                    pass
            return False

        # numeric excel serial date
        if isinstance(value, float) and value > 30000:
            try:
                return datetime.datetime(*xlrd.xldate_as_tuple(value, 0)).date()
            except Exception:
                return False

        return False

    def _safe_float(self, value):
        try:
            return float(value)
        except:
            return 0.0

    # -----------------------------
    # MAIN IMPORT FUNCTION
    # -----------------------------
    def action_import_app(self):
        if not self.file:
            raise UserError("Upload Excel File first.")

        try:
            data = base64.b64decode(self.file)
            workbook = xlrd.open_workbook(file_contents=data)
            sheet = workbook.sheet_by_index(0)
        except:
            raise UserError("Invalid file format. Upload an XLS file.")

        # ======================================================
        # 1️⃣ READ MAIN HEADER SECTION (Rows 3 to 11)
        # ======================================================
        def read_cell(colA_label):
            for r in range(2, 12):  # rows 2–11
                if sheet.cell(r, 0).value == colA_label:
                    return sheet.cell(r, 1).value
            return False

        # name = read_cell("name (ref number)")
        entity_name = read_cell("entity_name")
        user_name = read_cell("user_id")
        procurement_method = read_cell("procurement_method")
        indicative = read_cell("indicative")
        company_name = read_cell("company_id")
        year = read_cell("year")
        department_name = read_cell("department_id")
        state = read_cell("state")

        # Right-hand data (Date Start / End etc.)
        def read_cell_right(colC_label):
            for r in range(2, 12):
                if sheet.cell(r, 2).value == colC_label:
                    return sheet.cell(r, 3).value
            return False

        date_start = self._excel_date(read_cell_right("date_start"))
        date_end = self._excel_date(read_cell_right("date_end"))
        approve_date = self._excel_date(read_cell_right("approve_date"))
        budget_from = self._safe_float(read_cell_right("estimated_budget_total_from"))
        budget_to = self._safe_float(read_cell_right("estimated_budget_total_to"))
        total_app_budget = self._safe_float(read_cell_right("total_app_budget"))
        total_unused_budget = self._safe_float(read_cell_right("total_unused_budget"))
        currency_name = read_cell_right("currency_id")
        notes = read_cell_right("notes")

        # ======================================================
        # 2️⃣ RESOLVE RELATED RECORDS
        # ======================================================
        # User
        user = False
        if user_name:
            user = self.env["res.users"].search([("name", "=", user_name)], limit=1)

        # Company
        company = False
        if company_name:
            company = self.env["res.company"].search([("name", "=", company_name)], limit=1)

        # Department
        department = False
        if department_name:
            department = self.env["hr.department"].search([("name", "=", department_name)], limit=1)

        # Currency
        currency = False
        if currency_name:
            # currency = self.env["res.currency"].search([("name", "=", currency_name)], limit=1)
            currency = self.env["res.currency"].search([("name", "=", "ZAR")], limit=1)

        fiscal_year = False
        if year:
            fiscal_year = self.env["account.fiscal.year"].search([("name", "ilike", year)], limit=1)
        # ======================================================
        # 3️⃣ CREATE MAIN APP RECORD
        # ======================================================
        app = self.env["annual.procurement.plan"].sudo().create({
            # "name": name,
            "entity_name": entity_name,
            "user_id": user.id if user else False,
            "procurement_method": procurement_method,
            "company_id": company.id if company else False,
            "fiscal_year": fiscal_year.id if fiscal_year else False,
            "department_id": department.id if department else False,
            "state": state if state else "draft",
            "indicative":indicative,

            "date_start": date_start,
            "date_end": date_end,
            "approve_date": approve_date,

            "estimated_budget_total_from": budget_from,
            "estimated_budget_total_to": budget_to,
            "total_app_budget": total_app_budget,
            "total_unused_budget": total_unused_budget,

            "currency_id": currency.id if currency else False,
            "notes": notes,
            "initiator_id":self.env.user.id,
            "create_uid":self.env.user.id,
        })

        # ======================================================
        # 4️⃣ IMPORT LINES (Start from row 17)
        # ======================================================
        for row in range(18, sheet.nrows):
            ref_no = sheet.cell(row, 0).value
            if not ref_no:
                continue  # skip empty rows

            class_of_proc = sheet.cell(row, 1).value
            object_code = sheet.cell(row, 2).value
            requirement = sheet.cell(row, 3).value
            pmo_name = sheet.cell(row, 4).value
            procurement_method = sheet.cell(row, 5).value

            # Dates
            eoi_pub = self._excel_date(sheet.cell(row, 6).value)
            eoi_close = self._excel_date(sheet.cell(row, 7).value)
            bid_pub = self._excel_date(sheet.cell(row, 8).value)
            bid_close = self._excel_date(sheet.cell(row, 9).value)
            award_pub = self._excel_date(sheet.cell(row, 10).value)
            contract_sign = self._excel_date(sheet.cell(row, 11).value)

            cycle = self._safe_float(sheet.cell(row, 12).value)
            lead_time = self._safe_float(sheet.cell(row, 13).value)
            spoc = sheet.cell(row, 14).value
            source_of_funds = sheet.cell(row, 15).value
            uom_name = sheet.cell(row, 16).value
            quantity = self._safe_float(sheet.cell(row, 17).value)
            unit_price = self._safe_float(sheet.cell(row, 18).value)
            mode = self._safe_float(sheet.cell(row, 19).value)
            co = self._safe_float(sheet.cell(row, 20).value)
            comment = sheet.cell(row, 21).value

            # User
            user = False
            if pmo_name:
                user = self.env["res.users"].search([("name", "=", pmo_name)], limit=1)

            # Product
            product = False
            if requirement:
                product = self.env["product.product"].search([("name", "=ilike", requirement)], limit=1)

            # UOM
            uom = self.env["uom.uom"].search([("name", "=", uom_name)], limit=1)

            line_vals = {
                "plan_id": app.id,
                "name": ref_no,
                "class_of_procurement": class_of_proc,
                "object_code": object_code,
                "product_id": product.id if product else False,
                "requirements": requirement,
                "user_id": user.id if user else False,

                "procurement_method": procurement_method,

                "eoi_publication_date": eoi_pub,
                "eoi_closing_date": eoi_close,
                "tender_notice_date": bid_pub,
                "tender_closing_date": bid_close,
                "award_publication_date": award_pub,
                "contract_signing_date": contract_sign,

                "cycle_work_days": cycle,
                "lead_time_days": lead_time,
                "spoc_required": "yes" if spoc == "Y" else "no",
                "source_of_funds": source_of_funds,

                "uom_id": uom.id if uom else False,
                "quantity": quantity,
                "unit_price": unit_price,
                "mode": mode,
                "co": co,
                "comment": comment,
            }

            Line = self.env["annual.procurement.plan.line"].sudo()
            if ref_no:
                existing = Line.search([("plan_id", "=", app.id), ("name", "=", ref_no)], limit=1)
            else:
                existing = False

            if existing:
                existing.write(line_vals)
            else:
                Line.create(line_vals)

        return {
            "effect": {
                "fadeout": "slow",
                "message": "APP + APP Lines Imported Successfully!",
                "type": "rainbow_man",
            }
        }

class APPLineImportWizard(models.TransientModel):
    _name = "app.line.import.wizard"
    _description = "APP Line Import Wizard"

    plan_id = fields.Many2one("annual.procurement.plan", string="Plan", required=True)
    file = fields.Binary(string="Excel File", required=True)
    filename = fields.Char(string="Filename")

    # SAFE DATE PARSER (match APPImportWizard behaviour)
    def _excel_date(self, value):
        if not value or value in ["Not Applicable", "N/A"]:
            return False

        # direct python date
        if isinstance(value, datetime.date):
            return value

        # string date
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d %b %y", "%d/%m/%Y"):
                try:
                    return datetime.datetime.strptime(value, fmt).date()
                except Exception:
                    pass
            return False

        # numeric excel serial date
        if isinstance(value, float) and value > 30000:
            try:
                return datetime.datetime(*xlrd.xldate_as_tuple(value, 0)).date()
            except Exception:
                return False

        return False

    def _safe_float(self, value):
        try:
            return float(value)
        except:
            return 0.0

    def action_import_lines(self):
        if not self.file:
            raise UserError("Please upload an XLS file.")

        try:
            data = base64.b64decode(self.file)
            workbook = xlrd.open_workbook(file_contents=data)
            sheet = workbook.sheet_by_index(0)
        except Exception:
            raise UserError("Invalid file format. Please upload a valid .xls file.")

        # IMPORT LINES (Start from row 18 to match APPImportWizard)
        for row in range(18, sheet.nrows):
            ref_no = sheet.cell(row, 0).value
            if not ref_no:
                continue  # skip empty rows

            class_of_proc = sheet.cell(row, 1).value
            object_code = sheet.cell(row, 2).value
            requirement = sheet.cell(row, 3).value
            pmo_name = sheet.cell(row, 4).value
            procurement_method = sheet.cell(row, 5).value

            # Dates
            eoi_pub = self._excel_date(sheet.cell(row, 6).value)
            eoi_close = self._excel_date(sheet.cell(row, 7).value)
            bid_pub = self._excel_date(sheet.cell(row, 8).value)
            bid_close = self._excel_date(sheet.cell(row, 9).value)
            award_pub = self._excel_date(sheet.cell(row, 10).value)
            contract_sign = self._excel_date(sheet.cell(row, 11).value)

            cycle = self._safe_float(sheet.cell(row, 12).value)
            lead_time = self._safe_float(sheet.cell(row, 13).value)
            spoc = sheet.cell(row, 14).value
            source_of_funds = sheet.cell(row, 15).value
            uom_name = sheet.cell(row, 16).value
            quantity = self._safe_float(sheet.cell(row, 17).value)
            unit_price = self._safe_float(sheet.cell(row, 18).value)
            mode = self._safe_float(sheet.cell(row, 19).value)
            co = self._safe_float(sheet.cell(row, 20).value)
            comment = sheet.cell(row, 21).value

            # User
            user = False
            if pmo_name:
                user = self.env["res.users"].search([("name", "=", pmo_name)], limit=1)

            # Product
            product = False
            if requirement:
                product = self.env["product.product"].search([("name", "=ilike", requirement)], limit=1)

            # UOM
            uom = self.env["uom.uom"].search([("name", "=", uom_name)], limit=1)

            line_vals = {
                "plan_id": self.plan_id.id,
                "name": ref_no,
                "class_of_procurement": class_of_proc,
                "object_code": object_code,
                "product_id": product.id if product else False,
                "requirements": requirement,
                "user_id": user.id if user else False,

                "procurement_method": procurement_method,

                "eoi_publication_date": eoi_pub,
                "eoi_closing_date": eoi_close,
                "tender_notice_date": bid_pub,
                "tender_closing_date": bid_close,
                "award_publication_date": award_pub,
                "contract_signing_date": contract_sign,

                "cycle_work_days": cycle,
                "lead_time_days": lead_time,
                "spoc_required": "yes" if spoc == "Y" else "no",
                "source_of_funds": source_of_funds,

                "uom_id": uom.id if uom else False,
                "quantity": quantity,
                "unit_price": unit_price,
                "mode": mode,
                "co": co,
                "comment": comment,
            }

            Line = self.env["annual.procurement.plan.line"].sudo()
            if ref_no:
                existing = Line.search([("plan_id", "=", self.plan_id.id), ("name", "=", ref_no)], limit=1)
            else:
                existing = False

            if existing:
                existing.write(line_vals)
            else:
                Line.create(line_vals)

        return {
            "effect": {
                "fadeout": "slow",
                "message": "APP Lines Imported Successfully!",
                "type": "rainbow_man",
            }
        }
