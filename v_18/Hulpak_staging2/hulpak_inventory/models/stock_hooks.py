from odoo import models, fields, api,_
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

# --------- small utility to prefix once ---------
def _prefixed(prefix, base):
    prefix = (prefix or "").strip()
    base = (base or "").strip()
    if not prefix:
        return base
    # avoid double prefixing
    if base.startswith(prefix + " | ") or base == prefix:
        return base
    return f"{prefix} | {base}" if base else prefix


# ---------------- stock.move ----------------
class StockMove(models.Model):
    _inherit = "stock.move"

    hulpak_trace = fields.Char(string="FG/Batch/Row", index=True, help="FGSKU - Batch# - R<RowIndex>")

    @api.model_create_multi
    def create(self, vals_list):
        trace = (self.env.context or {}).get("hulpak_trace")
        for vals in vals_list:
            if trace:
                vals.setdefault("hulpak_trace", trace)
                # name = Operation Description, reference = Source Document
                vals["name"] = _prefixed(trace, vals.get("name"))
                vals["reference"] = _prefixed(trace, vals.get("reference"))
        return super().create(vals_list)


# --------------- stock.move.line ---------------
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    hulpak_trace = fields.Char(string="FG/Batch/Row", index=True, help="FGSKU - Batch# - R<RowIndex>")

    @api.model_create_multi
    def create(self, vals_list):
        trace = (self.env.context or {}).get("hulpak_trace")
        records = super().create(vals_list)
        if trace:
            # set the trace on the line; and ensure its parent move is prefixed (in case move existed)
            for ml in records:
                if not ml.hulpak_trace:
                    ml.hulpak_trace = trace
                if ml.move_id:
                    ml.move_id.sudo().write({
                        "name": _prefixed(trace, ml.move_id.name),
                        "reference": _prefixed(trace, ml.move_id.reference),
                        "hulpak_trace": ml.move_id.hulpak_trace or trace,
                    })
        return records


# # ----------- stock.valuation.layer -----------
# class StockValuationLayer(models.Model):
#     _inherit = "stock.valuation.layer"

#     hulpak_trace = fields.Char(string="FG/Batch/Row", index=True, help="FGSKU - Batch# - R<RowIndex>")

#     @api.model_create_multi
#     def create(self, vals_list):
#         trace = (self.env.context or {}).get("hulpak_trace")
#         for vals in vals_list:
#             if trace:
#                 vals.setdefault("hulpak_trace", trace)
#                 # 'description' is the label visible in reporting
#                 vals["description"] = _prefixed(trace, vals.get("description"))
#             # fallback from linked move if context missing
#             if not vals.get("hulpak_trace") and vals.get("stock_move_id"):
#                 move = self.env["stock.move"].browse(vals["stock_move_id"])
#                 if move.hulpak_trace:
#                     vals["hulpak_trace"] = move.hulpak_trace
#                     vals["description"] = _prefixed(move.hulpak_trace, vals.get("description"))
#         return super().create(vals_list)


# ----------------- account.move -----------------
class AccountMove(models.Model):
    _inherit = "account.move"

    hulpak_trace = fields.Char(string="FG/Batch/Row", index=True, help="FGSKU - Batch# - R<RowIndex>")

    @api.model_create_multi
    def create(self, vals_list):
        trace = (self.env.context or {}).get("hulpak_trace")
        for vals in vals_list:
            if trace:
                vals.setdefault("hulpak_trace", trace)
                # 'ref' is the journal entry label
                vals["ref"] = _prefixed(trace, vals.get("ref"))
        return super().create(vals_list)

    def post(self):
        # ensure ref is prefixed even if trace only reached the SVL
        for move in self:
            if not move.hulpak_trace:
                svls = move.line_ids.mapped("stock_valuation_layer_ids")
                if svls and svls[0].hulpak_trace:
                    trace = svls[0].hulpak_trace
                    move.write({
                        "hulpak_trace": trace,
                        "ref": _prefixed(trace, move.ref),
                    })
        return super().post()
