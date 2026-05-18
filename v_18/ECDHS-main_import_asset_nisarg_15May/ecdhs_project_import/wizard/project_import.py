import xlrd
import tempfile
import binascii
import re
from difflib import SequenceMatcher
from odoo import fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProjectImport(models.Model):
    """Chart of Project Import Model"""
    _name = 'project.import'
    _description = "Import Project"

    file = fields.Binary(string='File', required=True)

    def _normalize_municipality_key(self, value):
        """Return a simplified key to match municipality names across messy sources."""
        if value is None:
            return ""
        # xlrd sometimes returns floats for numeric-looking cells; be defensive.
        value = str(value).strip()
        if not value:
            return ""
        value = value.lower()
        value = re.sub(r"[^a-z0-9]+", " ", value)
        words = [w for w in value.split() if w]

        stop = {
            "all",
            "municipality",
            # Common misspelling seen in some datasets.
            "municiipality",
            "municipalities",
            "municipal",
            "local",
            "district",
            "metro",
            "metropolitan",
        }
        words = [w for w in words if w not in stop and len(w) > 1]
        return " ".join(words).strip()

    def _find_municipality(self, raw_name):
        Municipality = self.env["res.municipality"].sudo()
        raw_name = "" if raw_name is None else str(raw_name).strip()
        if not raw_name:
            return Municipality.browse()

        # 1) Keep existing behavior (fast path).
        municipality = Municipality.search([("municipality", "ilike", raw_name)], limit=1)
        if municipality:
            return municipality

        # 2) Fuzzy-ish fallback: normalize and match on the remaining key tokens.
        key = self._normalize_municipality_key(raw_name)
        if not key:
            return Municipality.browse()

        tokens = key.split()
        # Use AND across tokens to reduce false positives.
        domain = [("municipality", "ilike", t) for t in tokens]
        candidates = Municipality.search(domain, limit=20)
        if len(candidates) == 1:
            return candidates
        if not candidates:
            # Last fallback: try the longest token only.
            longest = max(tokens, key=len)
            return Municipality.search([("municipality", "ilike", longest)], limit=1)

        # Pick best candidate by similarity on normalized keys.
        best = None
        best_score = -1.0
        for cand in candidates:
            cand_key = self._normalize_municipality_key(cand.municipality)
            score = SequenceMatcher(None, key, cand_key).ratio()
            if score > best_score:
                best_score = score
                best = cand
        return best if best else Municipality.browse()

    def action_import_xlsx(self):
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            book = xlrd.open_workbook(fp.name)
        except FileNotFoundError:
            raise UserError(
                'No such file or directory found. \n%s.' % self.file_name)
        except xlrd.biffh.XLRDError:
            raise UserError('Only excel files are supported.')
        for sheet in book.sheets():
            try:
                for row in range(3,sheet.nrows):
                    row_values = sheet.row_values(row)
                    _logger.info("XLS Sheet Row Value: %s", row_values)
                    project = self.env['project.project'].sudo().search(
                        [('hss_project_number', '=', row_values[4])])
                    if not project:
                        result = self.create_project(row_values)
            except IndexError:
                pass

    def create_project(self, row_values):
        company = False
        municipality = False
        not_company = []
        if row_values:
            company = self.env['res.company'].sudo().search([('name', 'ilike', row_values[0])],limit=1)
            municipality = self._find_municipality(row_values[1])
            _logger.info("Find Company with XLS Sheet first column Value: %s", company)
            _logger.info("Find Municipality with XLS Sheet second column Value: %s", municipality)
            if company:
                project = self.env['project.project'].sudo().create({
                    'name': row_values[5],
                    'company_id': company.id if company else False,
                    'municipality_id': municipality.id if municipality else False,
                    'intervention': row_values[2].replace(' ', ''),
                    'sub_intervention': row_values[3],
                    'hss_project_number': row_values[4],
                    'description': row_values[5],
                    'total_annual_no_of_units': row_values[6],
                    'total_annual_no_of_sites': row_values[7],
                    'total_budget_amount': row_values[8],
                })
                _logger.info("Creaed Project using XLS Sheet Row Values: %s", project)
            else:
                not_company.append(row_values[0])
        return not_company
