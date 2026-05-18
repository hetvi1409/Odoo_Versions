
from odoo.exceptions import UserError,ValidationError
from odoo import api, fields, models, _



class LoanLineRent(models.Model):
    _inherit = 'loan.line.rs.rent'


    def make_invoice(self):
        for rec in self:
            if not rec.loan_id.partner_id.property_account_receivable_id:
                raise UserError(_('Please set receivable account for partner!'))
            if not rec.loan_id.account_income:
                raise UserError(_('Please set income account for this contract!'))
            account_move_obj = self.env['account.move']
            journal_pool = self.env['account.journal']
            journal = journal_pool.search([('type', '=', 'sale')], limit=1)
            inv_dict={'ref': rec.name,
                      'journal_id': journal.id,
                                     'partner_id': rec.contract_partner_id.id,
                                     'move_type': 'out_invoice', 'rental_line_id': rec.id,
                                     'invoice_date_due': rec.date,
                                     'property_owner_id': rec.loan_id.property_owner_id.id,
                                     'ref':(rec.loan_id.name + ' - ' + rec.name),
                                     }
            if not rec.line_account.id:
                rec.line_account = rec.loan_id.account_income
            if self.loan_id.apply_tax:
                inv_dict['invoice_line_ids']= [(0, None, {
                    'name': (rec.loan_id.name + ' - ' + rec.name),
                    'quantity': 1,
                    'account_id': rec.line_account.id,
                    # 'analytic_account_id': rec.loan_id.account_analytic_id.id,
                    'tax_ids': [(6, 0, (self.env.company.account_sale_tax_id.ids))],
                    'price_unit': rec.amount, })]
            else:
                inv_dict['invoice_line_ids']= [(0, None, {
                    'name': (rec.loan_id.name + ' - ' + rec.name),
                    'quantity': 1,
                    'account_id': rec.line_account.id,
                    # 'analytic_account_id': rec.loan_id.account_analytic_id.id,
                    'price_unit': rec.amount, })]
            new = []
            if rec.name == "Rental Fee":
                meters = self.env['utility.meter'].search([('contract_id', '=', rec.loan_id.id)])
                for meter in meters:
                    reading = meter.reading_ids.filtered(
                        lambda r: r.billing_period_start <= rec.date <= r.billing_period_end
                                  and not r.invoice_id)
                    tax = ""
                    if reading:
                        utility_label = meter._fields[
                            'utility_type'].convert_to_export(meter.utility_type,
                                                              meter)
                        if meter.tariff_id.price_includes_tax == "exclusive" and meter.tariff_id.tax_id:
                            tax = meter.tariff_id.tax_id
                        new.append((0, None, {
                            'name': (meter.name + ' : ' + utility_label + ' - ' + "Fee"),
                            'product_id': meter.tariff_id.fixed_product_id.id,
                            'quantity': 1,
                            'account_id': rec.line_account.id,
                            'price_unit': reading.invoice_amount,
                            'tax_ids': [(6, 0,
                                         tax.ids)] if tax else [],
                        }))

            inv_dict['invoice_line_ids'] = inv_dict['invoice_line_ids'] + new
            invoice= account_move_obj.create(inv_dict)
            if rec.name == "Rental Fee":
                for meter in meters:
                    reading = meter.reading_ids.filtered(
                        lambda
                            r: r.billing_period_start <= rec.date <= r.billing_period_end)
                    if reading:
                        reading.invoice_id = invoice.id

            self.invoice_id= invoice.id



class RentalContract(models.Model):
    _inherit = "rental.contract"

    reading_count = fields.Float('Reading Count', compute="_compute_reading_count")
    meter_count = fields.Float('Meter Count', compute="_compute_reading_count")

    def action_open_reading(self):
        """Action Open Reding"""
        meter = self.env['utility.meter'].search([('contract_id', '=', self.id)])
        reading = meter.mapped('reading_ids')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Reading',
            'view_mode': 'list,form',
            'res_model': 'utility.meter.reading',
            'domain': [('id', 'in', reading.ids)],
            'context': "{'create': False}"
        }

    def action_open_meter(self):
        """Action Open Reding"""
        meter = self.env['utility.meter'].search([('contract_id', '=', self.id)])

        return {
            'type': 'ir.actions.act_window',
            'name': 'Reading',
            'view_mode': 'list,form',
            'res_model': 'utility.meter',
            'domain': [('id', 'in', meter.ids)],
            'context': "{'create': False}"
        }

    @api.model
    def _compute_reading_count(self):
        reading_count, meter_count = 0, 0
        for rec in self:
            meter = self.env['utility.meter'].search(
                [('contract_id', '=', self.id)])
            reading_count = len(meter.mapped('reading_ids'))
            meter_count = self.env['utility.meter'].search_count(
                [('contract_id', '=', self.id)])
            rec.reading_count = reading_count
            rec.meter_count = meter_count