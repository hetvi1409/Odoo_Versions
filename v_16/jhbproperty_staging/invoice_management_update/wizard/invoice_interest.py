import base64
from odoo import fields, models, _


class InvoiceInterest(models.Model):
    """Model for method interest"""
    _name = 'invoice.interest'
    _description = 'Invoice interest'

    invoice_id = fields.Many2one('account.move',
                                 domain="[('move_type', '=', 'out_invoice')]")
    partner_id = fields.Many2one(related='invoice_id.partner_id')
    payment_state = fields.Selection(related='invoice_id.payment_state')

    def action_submit(self):
        """Method for submit the interest"""

        if self.payment_state in ['in_payment', 'paid']:
            payment = self.env['account.payment'].search(
                [('ref', '=', self.invoice_id.name)])
            attachment = []
            payment_name = ''
            for pay in payment:
                if payment_name:
                    payment_name = payment_name + ', ' + pay.name
                else:
                    payment_name = pay.name
                report_template_id = self.env[
                    'ir.actions.report']._render_qweb_pdf(
                    report_ref='account.action_report_payment_receipt',
                    data=None,
                    res_ids=payment.ids,
                )
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                    'name': "Payment Receipt %s" % self.invoice_id.name,
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/x-pdf',
                    'res_model': 'account.move',
                    'res_id': self.invoice_id.id
                }
                data_id = self.env['ir.attachment'].create(ir_values)
                attachment.append(data_id)
            mail_content = _('Hi %s,<br>'
                             'Your payment for the invoice %s has been '
                             'completed. Please check the proof of attachment.'
                             'Here is your payment receipt %s amounting to %s from %s.'
                             ) % \
                           (self.partner_id.name, self.invoice_id.name, payment_name, self.invoice_id.amount_total, self.invoice_id.company_id.name)
            main_content = {
                'subject': _('Payment was completed for the invoice %s') % self.invoice_id.name,
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': self.partner_id.email,

            }
            mail_id = self.env['mail.mail'].sudo().create(main_content)
            mail_id.mail_message_id.body = mail_content
            for attach in attachment:
                mail_id.attachment_ids = [(4, attach.id)]
            mail_id.sudo().send()
        else:
            product = self.env.ref('invoice_management_update.product_product_invoice_interest')
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner_id.id,
                'invoice_date': fields.Date.today(),
                'date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'product_id': product.id,
                    'price_unit': 10,
                    # 'tax_ids': [(6, 0, self.tax_purchase_a.ids)],
                })]
            })
