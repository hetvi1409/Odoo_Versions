
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaterialRequisition(models.Model):
    _name = "material.requisition"
    _description = "Material Requisition"

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee', required=True)
    department_id = fields.Many2one('hr.department', required=True)
    date = fields.Date('Requisition Date')
    job_card_id = fields.Many2one('job.card')
    line_ids = fields.One2many('material.requisition.line', 'line_id')
    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approve'),
         ('po', 'Purchase Order')], default='draft')
    po_order_ids = fields.Many2many('purchase.order', copy=False)

    @api.model
    def create(self, vals_list):
        """create sequence"""
        sequence_code = 'material.requisition.sequence'
        vals_list['name'] = self.env['ir.sequence'].next_by_code(sequence_code)
        res = super(MaterialRequisition, self).create(vals_list)
        return res

    def action_submit(self):
        """submit button"""
        for rec in self:
            if not rec.line_ids.ids:
                raise ValidationError(
                    'You cant submit the job card without instruction lines')
            else:
                rec.state = 'submit'

    def action_approve(self):
        """approve button"""
        for rec in self:
            rec.state = 'approve'

    def create_purchase_order(self):
        """create purchase order"""
        for rec in self:
            lines = []
            for line in rec.line_ids:
                value = (0, 0, {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'price_unit': line.product_id.standard_price,
                    'product_qty': line.quantity,
                })
                lines.append(value)
                po = self.env['purchase.order'].create({
                    'partner_id': line.vendor_id.id,
                    'order_line': lines,
                    'origin': rec.name
                })
                rec.state = 'po'
                rec.po_order_ids = [(4, po.id)]
    def get_purchase_order(self):
        """Returns purchase orders"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            # 'res_ids': self.po_order_ids.ids,
            'domain': [('id', 'in', self.po_order_ids.ids)]
        }

class MaterialRequisitionLine(models.Model):
    _name = "material.requisition.line"
    _description = 'Material Requisition Line'

    line_id = fields.Many2one("material.requisition")
    name = fields.Char()
    product_id = fields.Many2one('product.product', required=True)
    quantity = fields.Float(required=True)
    uom = fields.Many2one('uom.uom')
    vendor_id = fields.Many2one('res.partner', required=True)