from odoo import models, fields ,api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    
    department_id = fields.Many2one(
        'account.analytic.account',
        string="Department",
        domain="[('plan_id.name', 'ilike', 'Department')]"
    )

    region_id = fields.Many2one(
        'account.analytic.account',
        string="Region",
        domain="[('plan_id.name', 'ilike', 'Region')]"
    )


    @api.model
    def create(self, vals):
        move = super().create(vals)
        move._set_region_and_department_from_origin()
        try:
            for line in move.invoice_line_ids:
                if not (line.product_id and move.region_id):
                    continue

                # Machinery Component mapping
                component = self.env['machinery.component'].search([
                    ('product_ids', 'in', line.product_id.id)
                ], limit=1)

                account = False
                if component:
                    for income_account in component.income_account_ids:
                        if income_account.region.id == move.region_id.id:
                            account = income_account
                            break

                if account:
                    line.account_id = account.id
        except UserError as e:
            raise UserError(_("Error while setting account from machinery component: %s") % e.name)
        return move
    @api.onchange('partner_id','amount_total', 'invoice_origin')

    def _set_region_and_department_from_origin(self):
        for move in self:
            if move.invoice_origin :
                sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                purchase_order = self.env['purchase.order'].search([('name', '=', move.invoice_origin)], limit=1)
                if move.move_type == 'out_invoice':
                    if sale_order:
                        move.region_id = sale_order.region.id
                        move.department_id = sale_order.department.id
                    
                elif move.move_type == 'in_invoice':
                        if purchase_order:
                            move.region_id = purchase_order.region.id
                            move.department_id = purchase_order.department.id
                    
      

    def action_post(self):
        self._set_region_and_department_from_origin()
        return super().action_post()

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_lines_account_mapping(self):
        for move in self:
            for line in move.invoice_line_ids:
                if not (line.product_id and move.region_id):
                    continue

                # Machinery Component mapping
                component = self.env['machinery.component'].search([
                    ('product_ids', 'in', line.product_id.id)
                ], limit=1)

                account = False
                if component:
                    for income_account in component.income_account_ids:
                        if income_account.region.id == move.region_id.id:
                            account = income_account
                            break

                if account:
                    line.account_id = account.id

    total_net_weight = fields.Float(string="Total Net Weight", compute="_compute_total_net_weight")
    total_gross_weight = fields.Float(string="Total Gross Weight", compute="_compute_total_net_weight")

    @api.depends('invoice_line_ids')
    def _compute_total_net_weight(self):
        for rec in self:
            total_net_weight = 0.0
            total_gross_weight = 0.0
            for line in rec.invoice_line_ids:
                product = line.product_id
                if not product or not product.uom_id:
                    continue
                uom_line = line.product_uom_id
                uom_product = product.uom_id

                qty_in_product_uom = line.quantity / (
                        (uom_line.factor or 1.0) / (uom_product.factor or 1.0)
                )
                total_net_weight += (product.net_weight or 0.0) * qty_in_product_uom
                total_gross_weight += (product.weight or 0.0) * qty_in_product_uom

            rec.total_net_weight = total_net_weight
            rec.total_gross_weight = total_gross_weight

