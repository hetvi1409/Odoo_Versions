from odoo import models, fields, api,_
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

# Map of SKU families -> (SKU column, QTY column, COST column, is_used)
# is_used=True => consumption (goes negative); False => production (goes positive)#
SKU_COLUMNS = {
    "METAL": ("METAL SKU", "USED METAL", "METAL COST", True),
    "FINISHED_GOODS": ("FINISHED GOODS SKU", "PRODUCED FINISHED GOODS", "FINISHED GOODS COST", False),
    "OUTER_CARTON": ("OUTER CARTON SKU", "USED OUTER CARTON", "OUTER CARTON COST", True),
    "POLYBAG": ("POLYBAG SKU", "USED POLYBAGS", "POLLYBAG COST", True),
    "SCRAP": ("SCARP SKU", "PRODUCED SCRAP", "SCRAP COST", False),
    "FILLER": ("FILLER SKU", "USED FILLERS", "FILLER COST", True),
}

# Existing SKU map remains as you already have it.
# Add this fixed component mapping (you can lift to settings later if you prefer)
COMPONENT_PRODUCT_IDS = {
    "METAL": 2901,
    "OUTER_CARTON": 2900,
    "POLYBAG": 2897,
    "FILLER": 2895,
}



class InventoryAdjustBatch(models.Model):
    _name = "inventory.adjust.batch"
    _description = "Inventory Adjustment Batch (Excel-driven)"
    _order = "id desc"

    name = fields.Char(required=True, default=lambda s: _("Batch %s") % fields.Date.today())
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    location_id = fields.Many2one(
        "stock.location",
        string="Warehouse Location (Production)",
        domain=[("usage", "=", "internal")],
        required=True,
        help="Internal location where on-hand/final quantities are computed and applied."
    )
    state = fields.Selection(
        [("draft", "Draft"), ("imported", "Imported"), ("prepared", "Prepared"), ("applied", "Applied")],
        default="draft",
        tracking=True
    )

    raw_data_ids = fields.One2many("inventory.adjust.raw", "batch_id", string="Raw Excel Rows", copy=False)
    processing_ids = fields.One2many("inventory.adjust.line", "batch_id", string="Processing Lines", copy=False)
    cost_split_update_ids = fields.One2many("inventory.cost.split.update", "batch_id", string="Cost Split Updates", copy=False)
    # ---------- Helpers ----------
    def _get_row_val(self, row_dict, *candidates):
        """Return first non-empty value for any of the candidate header names."""
        for key in candidates:
            if key in row_dict and row_dict[key] not in (None, ""):
                return row_dict[key]
        return None

    # ---------- Actions ----------
    def action_prepare_processing(self):
        """Flatten raw rows into per-SKU lines with resolved product, OH, update, final and costs."""
        Product = self.env["product.product"]

        for batch in self:
            if not batch.raw_data_ids:
                raise UserError(_("No raw data to prepare."))

            # Clear previous processing lines
            batch.processing_ids.unlink()

            for rr in batch.raw_data_ids:
                row = rr._row_as_dict()

                for family, (sku_col, qty_col, cost_col, is_used) in SKU_COLUMNS.items():
                    sku = (self._get_row_val(row, sku_col) or "").strip()
                    if not sku:
                        continue

                    # Quantity (+/-)
                    qty_raw = self._get_row_val(row, qty_col) or 0.0
                    try:
                        qty_raw = float(qty_raw or 0.0)
                    except Exception:
                        qty_raw = 0.0
                    qty_update = -abs(qty_raw) if is_used else abs(qty_raw)

                    # Cost (robust header)
                    cost_val = self._get_row_val(row, cost_col, cost_col.strip(), cost_col.upper().strip())
                    try:
                        production_cost = float(cost_val or 0.0)
                    except Exception:
                        production_cost = 0.0

                    # Product by default_code = sku
                    product = Product.search([("default_code", "=", sku)], limit=1)

                    # On-hand at chosen location
                    qty_on_hand = 0.0
                    if product and batch.location_id:
                        qty_on_hand = product.with_context(location=batch.location_id.id).qty_available

                    final_qty = qty_on_hand + qty_update
                    current_cost = product.standard_price if product else 0.0

                    self.env["inventory.adjust.line"].create({
                        "batch_id": batch.id,
                        "row_index": rr.row_index,
                        "family": family,
                        "sku": sku,
                        "product_id": product.id or False,
                        "uom_id": product.uom_id.id if product else False,
                        "qty_on_hand": qty_on_hand,
                        "qty_update": qty_update,
                        "final_qty": final_qty,
                        "current_cost": current_cost,
                        "production_cost": production_cost,
                        "note": "" if product else _("No product found for SKU"),
                        "status": "ready" if product else "error",
                        "company_id": batch.company_id.id,
                    })

            batch.state = "prepared"
        return True
    # ---------- Button: Apply Adjustments ----------

    def action_apply_adjustments(self):
        """Post per row_index; SCRAP lines posted one-by-one with per-line cost; others aggregated per SKU.
        Also passes hulpak_trace='FGSKU - <Batch#> - R<row>' so labels are prefixed and stored on SVL/ML/AM."""
        Quant = self.env["stock.quant"]

        # helper to build the single trace string for this row
        def _trace_for_row(row_lines, row_idx, batch):
            fg = next((x for x in row_lines if (x.family or "").upper() == "FINISHED_GOODS"), None)
            sku = (fg.sku if fg else (row_lines and row_lines[0].sku) or "") or ""
            batch_no = batch.id or batch.name or ""
            return f"{sku} - {batch_no} - R{int(row_idx)}" # R = Row


        for batch in self:
            if batch.state != "prepared":
                raise UserError(_("Batch must be in 'Prepared' state."))


            # --- Refresh current_cost for guard context ---
            for l in batch.processing_ids.filtered(lambda x: x.product_id):
                tmpl = l.product_id.product_tmpl_id.with_company(batch.company_id)
                l.current_cost = float(tmpl.standard_price or 0.0)

            # --- Guards ---
            # 1) Non-scrap lines that change qty must have non-zero CURRENT cost
            missing_cost = batch.processing_ids.filtered(
                lambda l: l.product_id
                and (l.family or "").upper() != "SCRAP"
                and float(l.qty_update or 0.0) != 0.0
                and float(l.current_cost or 0.0) <= 0.0

            )
            if missing_cost:
                lines = "\n".join(f"- [Row {l.row_index}] {l.sku}" for l in missing_cost[:50])
                extra = "" if len(missing_cost) <= 50 else _("\n...and %s more") % (len(missing_cost) - 50)
                raise UserError(_(

                    "Cannot apply inventory: some NON-SCRAP lines change quantity but Current Product Cost is 0.\n"
                    "Set a non-zero product cost first for:\n%s%s"
                ) % (lines, extra))

            # 2) Scrap lines must have a positive per-line production_cost (we’ll set it JIT)
            bad_scrap = batch.processing_ids.filtered(
                lambda l: (l.family or "").upper() == "SCRAP"
                and float(l.qty_update or 0.0) != 0.0
                and float(l.production_cost or 0.0) <= 0.0
            )
            if bad_scrap:
                lines = "\n".join(f"- [Row {l.row_index}] {l.sku}" for l in bad_scrap[:50])
                extra = "" if len(bad_scrap) <= 50 else _("\n...and %s more") % (len(bad_scrap) - 50)
                raise UserError(_(
                    "Cannot apply inventory: some SCRAP lines have missing/zero Scrap Cost.\n"
                    "Provide a Scrap Cost for:\n%s%s"
                ) % (lines, extra))

            # 3) Unmapped SKUs still block

            error_lines = batch.processing_ids.filtered(lambda l: l.status == "error")
            if error_lines:
                sample = "\n".join(f"- [Row {l.row_index}] {l.sku}" for l in error_lines[:10])
                raise UserError(_("Fix unmapped SKUs before applying.\nExamples:\n%s") % sample)


            # ------- process row-by-row -------
            lines_to_apply = batch.processing_ids.filtered(lambda x: x.product_id and x.status != "applied")
            rows = {}
            for l in lines_to_apply:
                rows.setdefault(int(l.row_index or 0), []).append(l)

            for row_idx in sorted(rows):
                row_lines = rows[row_idx]
                trace = _trace_for_row(row_lines, row_idx, batch)
                ctx = {"hulpak_trace": trace}

                # ---------- A) SCRAP FIRST — post each scrap line individually with its own cost ----------
                scrap_lines = [l for l in row_lines if (l.family or "").upper() == "SCRAP"]
                for sl in scrap_lines:
                    product = sl.product_id

                    # 1) JIT set scrap product cost to this line's scrap cost
                    tmpl = product.product_tmpl_id.with_company(batch.company_id).sudo()
                    new_cost = float(sl.production_cost or 0.0)
                    if abs(float(tmpl.standard_price or 0.0) - new_cost) > 1e-6:
                        tmpl.standard_price = new_cost

                    # 2) Quant for this product/location
                    domain = [
                        ("product_id", "=", product.id),
                        ("location_id", "=", batch.location_id.id),
                        ("lot_id", "=", False),
                        ("owner_id", "=", False),
                        ("package_id", "=", False),
                    ]
                    quant = Quant.search(domain, limit=1)
                    if not quant:
                        quant = Quant.create({
                            "product_id": product.id,
                            "location_id": batch.location_id.id,
                            "lot_id": False,
                            "owner_id": False,
                            "package_id": False,
                            "company_id": batch.company_id.id,
                        })

                    # 3) Use LIVE on-hand; post this ONE line (with trace in context for label prefixing)
                    base_on_hand = float(quant.quantity or 0.0)
                    sl.qty_on_hand = base_on_hand
                    final_counted = base_on_hand + float(sl.qty_update or 0.0)

                    quant.with_context(**ctx).write({
                        "inventory_quantity": final_counted,
                        "inventory_date": fields.Datetime.now(),
                    })
                    quant.with_context(**ctx).action_apply_inventory()

                    sl.final_qty = final_counted
                    sl.status = "applied"

                    # 4) Push new on-hand to FUTURE lines of this SKU
                    new_on_hand = float(quant.quantity or final_counted)
                    future_lines = batch.processing_ids.filtered(
                        lambda x: x.product_id and x.product_id.id == product.id
                        and (int(x.row_index or 0) > row_idx) and x.status != "applied"
                    )
                    for fl in future_lines:
                        fl.qty_on_hand = new_on_hand
                        fl.final_qty = new_on_hand + float(fl.qty_update or 0.0)

                # ---------- B) NON-SCRAP — aggregate per SKU within this row (efficient & consistent) ----------
                other_lines = [l for l in row_lines if (l.family or "").upper() != "SCRAP"]
                per_prod = {}
                for l in other_lines:
                    b = per_prod.setdefault(l.product_id.id, {"product": l.product_id, "delta": 0.0, "lines": []})
                    b["delta"] += float(l.qty_update or 0.0)
                    b["lines"].append(l)

                for prod_id, b in per_prod.items():
                    product = b["product"]
                    net_delta = b["delta"]

                    domain = [
                        ("product_id", "=", product.id),
                        ("location_id", "=", batch.location_id.id),
                        ("lot_id", "=", False),
                        ("owner_id", "=", False),
                        ("package_id", "=", False),
                    ]
                    quant = Quant.search(domain, limit=1)
                    if not quant:
                        quant = Quant.create({
                            "product_id": product.id,
                            "location_id": batch.location_id.id,
                            "lot_id": False,
                            "owner_id": False,
                            "package_id": False,
                            "company_id": batch.company_id.id,
                        })

                    base_on_hand = float(quant.quantity or 0.0)
                    for line in b["lines"]:
                        line.qty_on_hand = base_on_hand

                    running = base_on_hand
                    for line in b["lines"]:
                        running += float(line.qty_update or 0.0)
                        line.final_qty = running

                    final_counted = base_on_hand + net_delta
                    # pass trace in context so move/SVL/AM labels are prefixed
                    quant.with_context(**ctx).write({
                        "inventory_quantity": final_counted,
                        "inventory_date": fields.Datetime.now(),
                    })
                    quant.with_context(**ctx).action_apply_inventory()

                    for line in b["lines"]:
                        line.status = "applied"

                    new_on_hand = float(quant.quantity or final_counted)
                    future_lines = batch.processing_ids.filtered(
                        lambda x: x.product_id and x.product_id.id == product.id
                        and (int(x.row_index or 0) > row_idx) and x.status != "applied"
                    )
                    for fl in future_lines:
                        fl.qty_on_hand = new_on_hand
                        fl.final_qty = new_on_hand + float(fl.qty_update or 0.0)

            batch.state = "applied"
        return True



    # ---------- Button: Apply Cost Splits ----------

    # def action_apply_cost_splits(self):
    #     """Create/Update product.cost.split and its lines for each staged FG entry."""
    #     Split = self.env["product.cost.split"].sudo()            # sudo: avoid ACL hiccups creating/updating
    #     SplitLine = self.env["product.cost.split.line"].sudo()
    #     Product = self.env["product.product"]                    # browse components as user is fine

    #     # Map your fixed component product IDs
    #     COMPONENT_PRODUCT_IDS = {
    #         "METAL": 2901,
    #         "OUTER_CARTON": 2900,
    #         "POLYBAG": 2897,
    #         "FILLER": 2895,
    #     }
    #     comp_prods = {k: Product.browse(v) for k, v in COMPONENT_PRODUCT_IDS.items()}

    #     for batch in self:
    #         if not batch.cost_split_update_ids:
    #             raise UserError(_("No cost split updates staged. Click 'Prepare Cost Splits' first."))

    #         # sanity: ensure component products exist
    #         missing = [k for k, p in comp_prods.items() if not p.exists()]
    #         if missing:
    #             raise UserError(_("Missing component products for: %s") % ", ".join(missing))

    #         for upd in batch.cost_split_update_ids:
    #             main_prod = upd.main_product_id
    #             if not main_prod:
    #                 upd.status = "error"
    #                 upd.note = _("No main product.")
    #                 continue

    #             # find or create split (sudo)
    #             split = Split.search([("main_product_id", "=", main_prod.id)], limit=1)
    #             if not split:
    #                 split = Split.create({
    #                     "main_product_id": main_prod.id,
    #                     # "machine": some_value_if_you_have_it,
    #                 })

    #             # helper: upsert one component line (sudo on write/create)
    #             def upsert_line(component_prod, amount):
    #                 amount = float(amount or 0.0)
    #                 line = split.line_ids.filtered(lambda l: l.component_product_id.id == component_prod.id)[:1]
    #                 if line:
    #                     line.sudo().write({"amount": amount})
    #                 else:
    #                     SplitLine.create({
    #                         "split_id": split.id,
    #                         "component_product_id": component_prod.id,
    #                         "amount": amount,
    #                     })

    #             upsert_line(comp_prods["METAL"], upd.metal_amount)
    #             upsert_line(comp_prods["OUTER_CARTON"], upd.outer_carton_amount)
    #             upsert_line(comp_prods["POLYBAG"], upd.pollybag_amount)
    #             upsert_line(comp_prods["FILLER"], upd.filler_amount)

    #             upd.sudo().write({"split_id": split.id, "status": "applied", "note": _("Applied")})

    #     return {
    #         "type": "ir.actions.client",
    #         "tag": "display_notification",
    #         "params": {
    #             "title": _("Cost splits applied"),
    #             "message": _("All staged cost splits were applied."),
    #             "type": "success",
    #             "sticky": False,
    #         },
    #     }

    def action_prepare_cost_splits(self):
        """
        Stage cost-split updates for FINISHED_GOODS using per-row JSON from inventory.adjust.raw.

        Amounts (per FG unit):
        metal_amount        = (METAL COST * USED METAL) / PRODUCED FINISHED GOODS
        outer_carton_amount = OUTER CARTON COST
        filler_amount       = FILLER COST * USED FILLERS
        pollybag_amount     = (POLLYBAG COST * USED POLYBAGS) / PRODUCED FINISHED GOODS   # <— changed
        """
        Update = self.env["inventory.cost.split.update"].sudo()
        RawRow = self.env["inventory.adjust.raw"].sudo()

        import re
        def _num(v):
            try: return float(v or 0.0)
            except Exception: return 0.0
        def _nk(k: str) -> str:
            return re.sub(r"[^a-z0-9]+", "_", (k or "").strip().lower()).strip("_")
        def _norm_dict(d: dict) -> dict:
            return {_nk(k): v for k, v in (d or {}).items()} if isinstance(d, dict) else {}
        def _from_row(row_norm: dict, original_header: str) -> float:
            return _num(row_norm.get(_nk(original_header)))

        for batch in self:
            if not batch.processing_ids:
                raise UserError(_("No processing lines found. Run 'Prepare Processing' first."))
            if batch.cost_split_update_ids:
                batch.cost_split_update_ids.sudo().unlink()

            Currency = batch.company_id.currency_id
            _r = Currency.round

            raw_rows = RawRow.search([("batch_id", "=", batch.id)])
            raw_by_idx = {int(r.row_index or 0): _norm_dict(r._row_as_dict()) for r in raw_rows}

            by_row = {}
            for l in batch.processing_ids:
                by_row.setdefault(int(l.row_index or 0), []).append(l)

            created = 0
            for row_idx, row_lines in by_row.items():
                fg = next((x for x in row_lines
                        if (x.family or "").upper() == "FINISHED_GOODS" and x.product_id), None)
                if not fg:
                    continue

                row = raw_by_idx.get(int(row_idx), {}) or {}
                note_bits = []
                if not row:
                    note_bits.append("no row_json for this row_index")

                # Column names via SKU_COLUMNS map
                METAL_COST_COL   = SKU_COLUMNS["METAL"][2]           # "METAL COST"
                METAL_QTY_COL    = SKU_COLUMNS["METAL"][1]           # "USED METAL"
                OUTER_COST_COL   = SKU_COLUMNS["OUTER_CARTON"][2]    # "OUTER CARTON COST"
                FILLER_COST_COL  = SKU_COLUMNS["FILLER"][2]          # "FILLER COST"
                FILLER_QTY_COL   = SKU_COLUMNS["FILLER"][1]          # "USED FILLERS"
                FG_QTY_COL       = SKU_COLUMNS["FINISHED_GOODS"][1]  # "PRODUCED FINISHED GOODS"

                # NEW: Pollybag columns (note: header spelled "POLLYBAG COST" in your map)
                PB_COST_COL      = SKU_COLUMNS["POLYBAG"][2]         # "POLLYBAG COST"
                PB_QTY_COL       = SKU_COLUMNS["POLYBAG"][1]         # "USED POLYBAGS"

                # Pull inputs
                metal_cost    = _from_row(row, METAL_COST_COL)
                used_metal    = _from_row(row, METAL_QTY_COL)
                outer_cost    = _from_row(row, OUTER_COST_COL)
                filler_cost   = _from_row(row, FILLER_COST_COL)
                used_fillers  = _from_row(row, FILLER_QTY_COL)
                produced_fg   = _from_row(row, FG_QTY_COL)

                # NEW: Pollybag inputs
                pollybag_cost = _from_row(row, PB_COST_COL)
                used_pollybag = _from_row(row, PB_QTY_COL)

                
                outer_carton_amount = outer_cost
                filler_amount = filler_cost
                
                # FG cost (prefer JSON, fallback to FG line’s production_cost)
                fg_cost = _from_row(row, "FINISHED GOODS COST")
                if not fg_cost:
                    fg_cost = _num(getattr(fg, "production_cost", 0.0))

                # Compute per-FG amounts (defensive for division by zero)
                if produced_fg <= 0:
                    metal_amount = 0.0
                    pollybag_amount = 0.0  # NEW: per spec, division would be invalid
                    note_bits.append("PRODUCED FINISHED GOODS is 0; metal/pollybag set to 0")
                else:
                    # metal_amount = (metal_cost * used_metal) / produced_fg
                    # NEW: Polly bag per box
                    pollybag_amount = (pollybag_cost * used_pollybag) / produced_fg
                    metal_amount = fg_cost - (pollybag_amount + outer_carton_amount + filler_amount)


                metal_amount        = _r(metal_amount)
                outer_carton_amount = _r(outer_carton_amount)
                filler_amount       = _r(filler_amount)
                pollybag_amount     = _r(pollybag_amount)

                # (Optional) If you still want to see reconciliation vs FG total, compute residual for notes only:
                residual = _r(fg_cost - (metal_amount + outer_carton_amount + filler_amount + pollybag_amount))
                if abs(residual) > 1e-6:
                    note_bits.append(f"residual vs FG cost: {residual}")

                # Diagnostics
                if metal_cost == 0:        note_bits.append(f"{METAL_COST_COL} missing/0")
                if used_metal == 0:        note_bits.append(f"{METAL_QTY_COL} missing/0")
                if outer_cost == 0:        note_bits.append(f"{OUTER_COST_COL} missing/0")
                if filler_cost == 0:       note_bits.append(f"{FILLER_COST_COL} missing/0")
                if used_fillers == 0:      note_bits.append(f"{FILLER_QTY_COL} missing/0")
                if pollybag_cost == 0:     note_bits.append(f"{PB_COST_COL} missing/0")
                if used_pollybag == 0:     note_bits.append(f"{PB_QTY_COL} missing/0")
                if fg_cost == 0:           note_bits.append("FINISHED GOODS COST missing/0 (fallback may have applied)")

                note = "; ".join(note_bits)

                Update.create({
                    "batch_id": batch.id,
                    "row_index": row_idx,
                    "main_product_id": fg.product_id.id,
                    "metal_amount": metal_amount,
                    "outer_carton_amount": outer_carton_amount,
                    "filler_amount": filler_amount,
                    "pollybag_amount": pollybag_amount,  # double 'l' field name
                    "status": "prepared",
                    "note": note,
                })
                created += 1

            if not created:
                raise UserError(_("Nothing to stage.\nNo FINISHED_GOODS lines with a mapped product were found in this batch."))

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Cost splits prepared"),
                "message": _("%s rows staged.") % created,
                "type": "success",
                "sticky": False,
            },
        }




    # ---------- Button: Apply Cost Splits ----------

    # def action_apply_cost_splits(self):
    #     """Create/Update product.cost.split and its lines for each staged FG entry."""
    #     Split = self.env["product.cost.split"].sudo()            # sudo: avoid ACL hiccups creating/updating
    #     SplitLine = self.env["product.cost.split.line"].sudo()
    #     Product = self.env["product.product"]                    # browse components as user is fine

    #     # Map your fixed component product IDs
    #     COMPONENT_PRODUCT_IDS = {
    #         "METAL": 2901,
    #         "OUTER_CARTON": 2900,
    #         "POLYBAG": 2897,
    #         "FILLER": 2895,
    #     }
    #     comp_prods = {k: Product.browse(v) for k, v in COMPONENT_PRODUCT_IDS.items()}

    #     for batch in self:
    #         if not batch.cost_split_update_ids:
    #             raise UserError(_("No cost split updates staged. Click 'Prepare Cost Splits' first."))

    #         # sanity: ensure component products exist
    #         missing = [k for k, p in comp_prods.items() if not p.exists()]
    #         if missing:
    #             raise UserError(_("Missing component products for: %s") % ", ".join(missing))

    #         for upd in batch.cost_split_update_ids:
    #             main_prod = upd.main_product_id
    #             if not main_prod:
    #                 upd.status = "error"
    #                 upd.note = _("No main product.")
    #                 continue

    #             # find or create split (sudo)
    #             split = Split.search([("main_product_id", "=", main_prod.id)], limit=1)
    #             if not split:
    #                 split = Split.create({
    #                     "main_product_id": main_prod.id,
    #                     # "machine": some_value_if_you_have_it,
    #                 })

    #             # helper: upsert one component line (sudo on write/create)
    #             def upsert_line(component_prod, amount):
    #                 amount = float(amount or 0.0)
    #                 line = split.line_ids.filtered(lambda l: l.component_product_id.id == component_prod.id)[:1]
    #                 if line:
    #                     line.sudo().write({"amount": amount})
    #                 else:
    #                     SplitLine.create({
    #                         "split_id": split.id,
    #                         "component_product_id": component_prod.id,
    #                         "amount": amount,
    #                     })

    #             upsert_line(comp_prods["METAL"], upd.metal_amount)
    #             upsert_line(comp_prods["OUTER_CARTON"], upd.outer_carton_amount)
    #             upsert_line(comp_prods["POLYBAG"], upd.pollybag_amount)
    #             upsert_line(comp_prods["FILLER"], upd.filler_amount)

    #             upd.sudo().write({"split_id": split.id, "status": "applied", "note": _("Applied")})

    #     return {
    #         "type": "ir.actions.client",
    #         "tag": "display_notification",
    #         "params": {
    #             "title": _("Cost splits applied"),
    #             "message": _("All staged cost splits were applied."),
    #             "type": "success",
    #             "sticky": False,
    #         },
    #     }

    def action_prepare_cost_splits(self):
        """
        Stage cost-split updates for FINISHED_GOODS using per-row JSON from inventory.adjust.raw.

        Amounts (per FG unit):
        metal_amount        = (METAL COST * USED METAL) / PRODUCED FINISHED GOODS
        outer_carton_amount = OUTER CARTON COST
        filler_amount       = FILLER COST * USED FILLERS
        pollybag_amount     = (POLLYBAG COST * USED POLYBAGS) / PRODUCED FINISHED GOODS   # <— changed
        """
        Update = self.env["inventory.cost.split.update"].sudo()
        RawRow = self.env["inventory.adjust.raw"].sudo()

        import re
        def _num(v):
            try: return float(v or 0.0)
            except Exception: return 0.0
        def _nk(k: str) -> str:
            return re.sub(r"[^a-z0-9]+", "_", (k or "").strip().lower()).strip("_")
        def _norm_dict(d: dict) -> dict:
            return {_nk(k): v for k, v in (d or {}).items()} if isinstance(d, dict) else {}
        def _from_row(row_norm: dict, original_header: str) -> float:
            return _num(row_norm.get(_nk(original_header)))

        for batch in self:
            if not batch.processing_ids:
                raise UserError(_("No processing lines found. Run 'Prepare Processing' first."))
            if batch.cost_split_update_ids:
                batch.cost_split_update_ids.sudo().unlink()

            Currency = batch.company_id.currency_id
            _r = Currency.round

            raw_rows = RawRow.search([("batch_id", "=", batch.id)])
            raw_by_idx = {int(r.row_index or 0): _norm_dict(r._row_as_dict()) for r in raw_rows}

            by_row = {}
            for l in batch.processing_ids:
                by_row.setdefault(int(l.row_index or 0), []).append(l)

            created = 0
            for row_idx, row_lines in by_row.items():
                fg = next((x for x in row_lines
                        if (x.family or "").upper() == "FINISHED_GOODS" and x.product_id), None)
                if not fg:
                    continue

                row = raw_by_idx.get(int(row_idx), {}) or {}
                note_bits = []
                if not row:
                    note_bits.append("no row_json for this row_index")

                # Column names via SKU_COLUMNS map
                METAL_COST_COL   = SKU_COLUMNS["METAL"][2]           # "METAL COST"
                METAL_QTY_COL    = SKU_COLUMNS["METAL"][1]           # "USED METAL"
                OUTER_COST_COL   = SKU_COLUMNS["OUTER_CARTON"][2]    # "OUTER CARTON COST"
                FILLER_COST_COL  = SKU_COLUMNS["FILLER"][2]          # "FILLER COST"
                FILLER_QTY_COL   = SKU_COLUMNS["FILLER"][1]          # "USED FILLERS"
                FG_QTY_COL       = SKU_COLUMNS["FINISHED_GOODS"][1]  # "PRODUCED FINISHED GOODS"

                # NEW: Pollybag columns (note: header spelled "POLLYBAG COST" in your map)
                PB_COST_COL      = SKU_COLUMNS["POLYBAG"][2]         # "POLLYBAG COST"
                PB_QTY_COL       = SKU_COLUMNS["POLYBAG"][1]         # "USED POLYBAGS"

                # Pull inputs
                metal_cost    = _from_row(row, METAL_COST_COL)
                used_metal    = _from_row(row, METAL_QTY_COL)
                outer_cost    = _from_row(row, OUTER_COST_COL)
                filler_cost   = _from_row(row, FILLER_COST_COL)
                used_fillers  = _from_row(row, FILLER_QTY_COL)
                produced_fg   = _from_row(row, FG_QTY_COL)

                # NEW: Pollybag inputs
                pollybag_cost = _from_row(row, PB_COST_COL)
                used_pollybag = _from_row(row, PB_QTY_COL)

                
                outer_carton_amount = outer_cost
                filler_amount = filler_cost
                
                # FG cost (prefer JSON, fallback to FG line’s production_cost)
                fg_cost = _from_row(row, "FINISHED GOODS COST")
                if not fg_cost:
                    fg_cost = _num(getattr(fg, "production_cost", 0.0))

                # Compute per-FG amounts (defensive for division by zero)
                if produced_fg <= 0:
                    metal_amount = 0.0
                    pollybag_amount = 0.0  # NEW: per spec, division would be invalid
                    note_bits.append("PRODUCED FINISHED GOODS is 0; metal/pollybag set to 0")
                else:
                    # metal_amount = (metal_cost * used_metal) / produced_fg
                    # NEW: Polly bag per box
                    pollybag_amount = (pollybag_cost * used_pollybag) / produced_fg
                    metal_amount = fg_cost - (pollybag_amount + outer_carton_amount + filler_amount)


                metal_amount        = _r(metal_amount)
                outer_carton_amount = _r(outer_carton_amount)
                filler_amount       = _r(filler_amount)
                pollybag_amount     = _r(pollybag_amount)

                # (Optional) If you still want to see reconciliation vs FG total, compute residual for notes only:
                residual = _r(fg_cost - (metal_amount + outer_carton_amount + filler_amount + pollybag_amount))
                if abs(residual) > 1e-6:
                    note_bits.append(f"residual vs FG cost: {residual}")

                # Diagnostics
                if metal_cost == 0:        note_bits.append(f"{METAL_COST_COL} missing/0")
                if used_metal == 0:        note_bits.append(f"{METAL_QTY_COL} missing/0")
                if outer_cost == 0:        note_bits.append(f"{OUTER_COST_COL} missing/0")
                if filler_cost == 0:       note_bits.append(f"{FILLER_COST_COL} missing/0")
                if used_fillers == 0:      note_bits.append(f"{FILLER_QTY_COL} missing/0")
                if pollybag_cost == 0:     note_bits.append(f"{PB_COST_COL} missing/0")
                if used_pollybag == 0:     note_bits.append(f"{PB_QTY_COL} missing/0")
                if fg_cost == 0:           note_bits.append("FINISHED GOODS COST missing/0 (fallback may have applied)")

                note = "; ".join(note_bits)

                Update.create({
                    "batch_id": batch.id,
                    "row_index": row_idx,
                    "main_product_id": fg.product_id.id,
                    "metal_amount": metal_amount,
                    "outer_carton_amount": outer_carton_amount,
                    "filler_amount": filler_amount,
                    "pollybag_amount": pollybag_amount,  # double 'l' field name
                    "status": "prepared",
                    "note": note,
                })
                created += 1

            if not created:
                raise UserError(_("Nothing to stage.\nNo FINISHED_GOODS lines with a mapped product were found in this batch."))

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Cost splits prepared"),
                "message": _("%s rows staged.") % created,
                "type": "success",
                "sticky": False,
            },
        }



    def action_open_import_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Import Excel",
            "res_model": "import.inventory.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_batch_id": self.id},
        }



    def action_update_product_cost(self):
        for batch in self:
            lines = batch.processing_ids.filtered(lambda l: l.status == "ready" and l.product_id)
            if not lines:
                raise UserError(_("No 'Ready' lines with a mapped product found."))

            lines.action_update_product_cost()


class InventoryAdjustRaw(models.Model):
    _name = "inventory.adjust.raw"
    _description = "Raw Excel Row (verbatim)"
    _order = "row_index asc"

    batch_id = fields.Many2one("inventory.adjust.batch", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="batch_id.company_id", store=True, readonly=True)
    row_index = fields.Integer(string="Row # (sheet)", help="1-based index from Excel (excluding header).")
    row_json = fields.Json(string="Row JSON", help="Full source row as key/value pairs (header -> cell value).")

    def _row_as_dict(self):
        self.ensure_one()
        return dict(self.row_json or {})


class InventoryAdjustLine(models.Model):
    _name = "inventory.adjust.line"
    _description = "Normalized Per-SKU Processing Line"
    _order = "row_index, id"

    batch_id = fields.Many2one("inventory.adjust.batch", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="batch_id.company_id", store=True, readonly=True)

    row_index = fields.Integer(string="Source Row #")
    family = fields.Selection([
        ("METAL", "METAL"),
        ("FINISHED_GOODS", "FINISHED GOODS"),
        ("OUTER_CARTON", "OUTER CARTON"),
        ("POLYBAG", "POLYBAG"),
        ("SCRAP", "SCRAP"),
        ("FILLER", "FILLER"),
    ], string="SKU Family", required=True)

    sku = fields.Char(required=True, help="Matched to product.product.default_code")
    product_id = fields.Many2one("product.product", string="Product")
    uom_id = fields.Many2one("uom.uom", string="UoM", readonly=True)

    qty_on_hand = fields.Float(string="Quantity On Hand", digits="Product Unit of Measure", readonly=True)
    qty_update = fields.Float(string="Quantity Update (+/-)", digits="Product Unit of Measure",
                              help="Positive = produce (increase); Negative = consume (decrease).")
    final_qty = fields.Float(string="Final Quantity", digits="Product Unit of Measure", readonly=True)

    current_cost = fields.Float(string="Current Product Cost", digits="Product Price", readonly=True)
    production_cost = fields.Float(string="Production Cost", digits="Product Price")

    note = fields.Char()
    status = fields.Selection([
        ("ready", "Ready"),
        ("error", "Error"),
        ("applied", "Applied"),
    ], default="ready", tracking=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.uom_id = line.product_id.uom_id
                # Recompute OH and final if needed
                batch = line.batch_id
                if batch and batch.location_id:
                    line.qty_on_hand = line.product_id.with_context(location=batch.location_id.id).qty_available
                    line.final_qty = line.qty_on_hand + (line.qty_update or 0.0)
                line.current_cost = line.product_id.standard_price or 0.0


    def action_update_product_cost(self):
        for l in self:
            if not l.product_id:
                raise UserError(_("No product found for line [Row %s] %s.") % (l.row_index, l.sku))
            cost = float(l.production_cost or 0.0)
            if cost <= 0.0:
                raise UserError(_("Cannot update cost for [Row %s] %s: Production Cost is 0.") % (l.row_index, l.sku))

            tmpl = l.product_id.product_tmpl_id.with_company(l.company_id or l.batch_id.company_id)
            tmpl.standard_price = cost
        return True
    

class InventoryCostSplitUpdate(models.Model):
    _name = "inventory.cost.split.update"
    _description = "Staged Update for Product Cost Split"
    _order = "row_index, id"
    _rec_name = "split_name"

    batch_id = fields.Many2one("inventory.adjust.batch", required=True, ondelete="cascade")
    row_index = fields.Integer()
    main_product_id = fields.Many2one("product.product", string="Main Product", required=True)
    split_id = fields.Many2one("product.cost.split", string="Linked Cost Split", readonly=True)

    metal_amount = fields.Float(string="Metal Amount")
    outer_carton_amount = fields.Float(string="Outer Carton Amount")
    pollybag_amount = fields.Float(string="Polly Bag Amount")
    filler_amount = fields.Float(string="Filler Amount")

    status = fields.Selection(
        [("prepared", "Prepared"), ("applied", "Applied"), ("error", "Error")],
        default="prepared"
    )
    note = fields.Char()
    split_name = fields.Char(string="Cost Split", compute="_compute_split_name")

    def _compute_split_name(self):
        for rec in self:
            rec.split_name = rec.sudo().split_id.display_name if rec.split_id else ""
