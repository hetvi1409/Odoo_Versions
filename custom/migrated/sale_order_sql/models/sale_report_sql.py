from odoo import models, fields, tools

class SaleReportSQL(models.Model):
    _name = 'sale.report.sql'
    _description = 'Sales SQL Report'
    _auto = False
    _rec_name = 'partner_id'
    _order = 'total_amount desc'

    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    total_orders = fields.Integer(string='Total Orders', readonly=True)
    total_amount = fields.Float(string='Total Amount', readonly=True)
    average_amount = fields.Float(string='Average Order Amount', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW sale_report_sql AS (
                SELECT
                    MIN(so.id) AS id,
                    so.partner_id AS partner_id,
                    COUNT(so.id) AS total_orders,
                    SUM(so.amount_total) AS total_amount,
                    AVG(so.amount_total) AS average_amount
                FROM sale_order so
                WHERE so.state IN ('sale', 'done')
                GROUP BY so.partner_id
            )
        """)