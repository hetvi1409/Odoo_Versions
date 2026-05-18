# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    default_code = fields.Char(string="Product Internal Reference", readonly=True)
    commercial_partner_ref = fields.Char(string="Customer Account No", readonly=True)
    customer_ref = fields.Char(string="Customer Reference", readonly=True)
    delivery_date = fields.Datetime(string="Delivery Date", readonly=True)
    net_weight = fields.Float(string="Net Weight", readonly=True)
    warehouse_qty_summary = fields.Text(string="Warehouse Qty Summary", readonly=True)
    weight = fields.Float(string="Gross Weight", readonly=True)
    period = fields.Char(string="Period", readonly=True)

    @api.model
    def _select(self) -> SQL:
        base = super()._select()
        return SQL(
            """
            %s,
            product.default_code AS default_code,
            commercial_partner.ref AS commercial_partner_ref,
            move.ref AS customer_ref,
            -- Use sale order commitment_date when available, otherwise invoice date
            COALESCE(so.commitment_date, move.invoice_date) AS delivery_date,

            (template.net_weight *
                (line.quantity / NULLIF(COALESCE(uom_line.factor, 1) /
                                        COALESCE(uom_template.factor, 1), 0.0))
            ) AS net_weight,

            (template.weight *
                (line.quantity / NULLIF(COALESCE(uom_line.factor, 1) /
                                        COALESCE(uom_template.factor, 1), 0.0))
            ) AS weight,

            (
                SELECT STRING_AGG(sl.complete_name || ' - ' || q.quantity::text, ', ')
                FROM stock_quant q
                JOIN stock_location sl ON q.location_id = sl.id
                WHERE q.product_id = line.product_id
                  AND sl.usage = 'internal'
            ) AS warehouse_qty_summary,

            TO_CHAR(move.invoice_date, 'YYYY-MM') AS period
            """,
            base
        )

    @api.model
    def _from(self) -> SQL:
        base = super()._from()
        return SQL(
            """
            %s
            LEFT JOIN sale_order so ON so.name = move.invoice_origin
            """,
            base
        )

    @api.model
    def _group_by(self) -> SQL:
        base = super()._group_by()
        return SQL(
            """
            %s,
            product.default_code,
            commercial_partner.ref,
            move.ref,
            COALESCE(so.commitment_date, move.invoice_date),
            template.net_weight,
            template.weight,
            TO_CHAR(move.invoice_date, 'YYYY-MM')
            """,
            base
        )