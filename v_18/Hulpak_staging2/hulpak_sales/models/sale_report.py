# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleReport(models.Model):
    _inherit = "sale.report"

    commercial_partner_ref = fields.Char(string="Customer Account No", readonly=True)
    net_weight = fields.Float(string="Net Weight", readonly=True)
    default_code = fields.Char(string="Product Internal Reference", readonly=True)
    warehouse_qty_summary = fields.Text(string="Qty by Warehouse", readonly=True)
    customer_ref = fields.Char(string="Customer Reference", readonly=True)
    delivery_date = fields.Datetime(string="Delivery Date", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res.update({
            'commercial_partner_ref': 'partner.ref',
            'default_code': 'p.default_code',
            'customer_ref': 's.client_order_ref',
            'delivery_date': 's.commitment_date',
            'net_weight': """CASE WHEN l.product_id IS NOT NULL THEN
                SUM(t.net_weight * l.product_uom_qty / u.factor * u2.factor)
                ELSE 0 END""",
            'warehouse_qty_summary': """(
                SELECT STRING_AGG(wq.code || ' - ' || wq.qty::text, ', ')
                FROM (
                    SELECT w.code, ROUND(SUM(q.quantity)::numeric, 2) AS qty
                    FROM stock_quant q
                    JOIN stock_location sl ON q.location_id = sl.id
                    JOIN stock_warehouse w ON sl.parent_path LIKE CONCAT('%%/', w.view_location_id, '/%%')
                    WHERE q.product_id = l.product_id AND sl.usage = 'internal'
                    GROUP BY w.code
                ) AS wq
            )"""
        })
        return res

    def _from_sale(self):
        currency_table = self.env['res.currency']._get_simple_currency_table(self.env.companies)
        currency_table = self.env.cr.mogrify(currency_table).decode(self.env.cr.connection.encoding)
        return f"""
            sale_order_line l
            LEFT JOIN sale_order s ON s.id=l.order_id
            JOIN res_partner partner ON s.partner_id = partner.id
            LEFT JOIN product_product p ON l.product_id=p.id
            LEFT JOIN product_template t ON p.product_tmpl_id=t.id
            LEFT JOIN uom_uom u ON u.id=l.product_uom
            LEFT JOIN uom_uom u2 ON u2.id=t.uom_id
            JOIN {currency_table} ON account_currency_table.company_id = s.company_id
        """

    def _group_by_sale(self):
        return super()._group_by_sale() + """,
            partner.ref,
            t.net_weight,
            p.default_code,
            s.client_order_ref,
            s.commitment_date
        """
