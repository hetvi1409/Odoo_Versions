from odoo import models, fields, api, _
from datetime import datetime


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    clinical_exam_id = fields.Many2one('clinical.examination', string="Exam")
    final_rx_id = fields.Many2one('clinical.final.rx', string="Final Rx")
    contact_final_rx_id = fields.Many2one('clinical.final.rx.contact', string="Contact Final Rx")
    project_task_id = fields.Many2one('project.task', string="Job")
    job_number = fields.Char(related="project_task_id.job_number")
    job_number = fields.Char(related="project_task_id.job_number")
    px_name = fields.Many2one(related="clinical_exam_id.partner_id", string="Patient")

    def action_view_invoice(self):
        res = super(purchase_order, self).action_view_invoice()
        res['context'].update({'default_invoice_picking_id': self.picking_ids[0].id})
        return res

    def delivery_fee(self):
        pass
        # product_delivery_id = self.env.ref('TOMS.add_delivery_fee')
        # delivery_product = self.order_line.filtered(lambda x: x.product_id.id == product_delivery_id.id)
        # if not delivery_product and len(self.order_line.ids) >= 1:
        #     vals = {
        #         'product_id': product_delivery_id.id,
        #         'name': product_delivery_id.default_code,
        #         'product_qty': 1,
        #         'date_planned': datetime.now(),
        #         'product_uom': 1,
        #         'price_unit': product_delivery_id.standard_price
        #     }
        #     self.write({'order_line': [(0, 0, vals)]})
