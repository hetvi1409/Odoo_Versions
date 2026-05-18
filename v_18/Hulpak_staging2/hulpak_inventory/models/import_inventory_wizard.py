# -*- coding: utf-8 -*-
import base64
import io

from odoo import api, fields, models, _
from odoo.exceptions import UserError

try:
    import openpyxl
except Exception:
    openpyxl = None


class ImportInventoryWizard(models.TransientModel):
    _name = "import.inventory.wizard"
    _description = "Import Production Template Excel"

    batch_id = fields.Many2one("inventory.adjust.batch", required=True)
    file = fields.Binary(string="Excel File (.xlsx)", required=True)
    filename = fields.Char()

    def action_import(self):
        self.ensure_one()
        if not openpyxl:
            raise UserError(_("Python package 'openpyxl' is required on the server."))

        data = base64.b64decode(self.file or b"")
        if not data:
            raise UserError(_("File is empty."))

        wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
        ws = wb.active  # first sheet

        # Parse header (strip whitespace)
        header = []
        for cell in ws[1]:
            val = cell.value or ""
            if isinstance(val, str):
                val = val.strip()
            header.append(val)

        # Clear old rows
        self.batch_id.raw_data_ids.unlink()

        # Build rows
        row_index = 0
        for i, row in enumerate(ws.iter_rows(min_row=2), start=2):
            vals = {}
            empty = True
            for j, cell in enumerate(row):
                key = header[j] if j < len(header) else f"COL{j+1}"
                val = cell.value
                if isinstance(val, str):
                    val = val.strip()
                if val not in (None, "", 0):
                    empty = False
                vals[key] = val

            if empty:
                continue

            row_index += 1
            self.env["inventory.adjust.raw"].create({
                "batch_id": self.batch_id.id,
                "row_index": row_index,
                "row_json": vals,
            })

        self.batch_id.state = "imported"
        return {"type": "ir.actions.act_window_close"}
