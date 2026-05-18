from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class PartnerContract(models.Model):
    """"""
    _inherit = 'xf.partner.contract'

    # Fields
    sequence_number = fields.Char(string='Sequence Number', readonly=True,
                                  default=lambda self: _('New'))
    contract_duration = fields.Float(string='Contract Duration(in months)',
                                     compute='_compute_contract_duration')
    remaining_contract_duration = fields.Float(
        string='Remaining Contract Duration(in months)',
        compute='_compute_remaining_contract_duration')
    tender_number = fields.Char(string='Tender Number')
    sla_contract_signed = fields.Binary(string='SLA/Contract Signed')
    arrival_letter = fields.Binary(string='Arrival Letter')
    variation_orders = fields.Binary(string='Variation Orders')
    extension_of_time = fields.Binary(string='Extension of times')
    penalties = fields.Binary(string='Penalties and Other Correspond')
    completion_letter = fields.Binary(string='Completion Certificate/Letter')
    cost_based = fields.Float(string='Cost Based Progress(%)',
                              compute='_compute_cost_based')
    time_based = fields.Float(string='Time Based Progress(%)',
                              compute='_compute_time_based')
    extension_period = fields.Integer(string='Extension Period(in months)')
    revised_end_date = fields.Date(string='Revised End Date',
                                   compute='_compute_revised_end_date')
    variation_order_amt = fields.Float(string='Variation Order Amount')
    variation_order_per = fields.Float(string='Variation Order %',
                                       compute='_compute_variation_order_per',
                                       store=True)
    reversal_contract_amt = fields.Float(string='Reversal Contract Amount',
                                         compute='_compute_reversal_contract_amt')
    classification = fields.Selection(
        selection=[
            ('capital', "Capital"),
            ('operational', "Operational"),
        ],
        string="Classification",
        default='capital')
    contract_amt_type = fields.Selection(
        selection=[
            ('fixed_value', "Fixed Value"),
            ('rate_based', "Rate Based"),
        ],
        string="Contract Amount Type",
        default='fixed_value')
    invoice_list_ids = fields.One2many('list.invoices', 'invoice_list',
                                       string='List of invoice raised')
    total_list_invoices = fields.Float(string='Total',
                                       compute='_compute_total_list_invoices')

    @api.depends('extension_period', 'date_end')
    def _compute_revised_end_date(self):
        for order in self:
            order.revised_end_date = False
            date_1 = order.date_end
            extension = order.extension_period

            if extension:
                if date_1:
                    revised_end_date = date_1 + relativedelta(months=+extension)
                    order.revised_end_date = revised_end_date

    @api.model
    def create(self, vals):
        if vals.get('sequence_number', _('New')) == _('New'):
            # Get the type and generate the prefix accordingly
            contract_type = vals.get('type', False)
            if contract_type:
                if contract_type == 'purchase':
                    contract_type = 'PUR'
                    prefix = f"JPC-{contract_type.upper()}"
                else:
                    contract_type = 'SAL'
                    prefix = f"JPC-{contract_type.upper()}"
            else:
                prefix = "JPC"

            # Generate the sequence number
            sequence_number = self.env['ir.sequence'].next_by_code(
                'xf.partner.contract') or _('New')

            # Generate the current year
            current_year = datetime.now().year

            # Create the ref field value
            ref = f"{prefix}{sequence_number}-{current_year}"

            # Set the ref and sequence_number in the create method
            vals.update({
                'ref': ref,
                'sequence_number': sequence_number,
            })

        res = super(PartnerContract, self).create(vals)
        return res

    @api.onchange('type')
    def onchange_type(self):
        if self.type and self.ref:
            # Change only the type in the ref field
            current_type = 'SAL' if self.type == 'sale' else 'PUR'
            self.ref = self.ref.replace('SAL', current_type).replace('PUR',
                                                                     current_type)

    @api.depends('variation_order_amt', 'amount')
    def _compute_variation_order_per(self):
        for record in self:
            record.variation_order_per = False
            if record.amount and record.variation_order_amt:
                record.variation_order_per = (
                        record.variation_order_amt / record.amount)
                if record.variation_order_per > 20 / 100:
                    raise ValidationError(
                        _('Cannot exceed 20% of the contract amount.'))

    @api.depends('variation_order_amt', 'amount')
    def _compute_reversal_contract_amt(self):
        for record in self:
            record.reversal_contract_amt = False
            if record.amount and record.variation_order_amt:
                record.reversal_contract_amt = record.amount + record.variation_order_amt

    @api.depends('invoice_list_ids.invoice_amount')
    def _compute_total_list_invoices(self):
        for rec in self:
            rec.total_list_invoices = False
            if rec.invoice_list_ids:
                invoice_amounts = sum(
                    rec.invoice_list_ids.mapped('invoice_amount'))
                rec.total_list_invoices = invoice_amounts

    # @api.depends('invoice_list_ids.invoice_amount')
    def _compute_cost_based(self):
        for rec in self:
            rec.cost_based = False
            if rec.total_list_invoices:
                rec.cost_based = rec.total_list_invoices / rec.amount * 100
            # rec.total_list_invoices/rec.amount

    @api.depends('date_start', 'date_end')
    def _compute_contract_duration(self):
        for record in self:
            record.contract_duration = False
            if record.date_start and record.date_end:
                start_date = record.date_start
                end_date = record.date_end
                delta = relativedelta(end_date, start_date)
                record.contract_duration = delta.years * 12 + delta.months

    @api.depends('date_start')
    def _compute_remaining_contract_duration(self):
        for record in self:
            record.remaining_contract_duration = False
            if record.date_start:
                start_date = record.date_start
                current_date = date.today()
                delta = relativedelta(current_date, start_date)
                duration = delta.years * 12 + delta.months
                record.remaining_contract_duration = record.contract_duration - duration

    # @api.depends('invoice_list_ids.invoice_amount')
    def _compute_time_based(self):
        for rec in self:
            rec.time_based = False
            if rec.contract_duration:
                duration_diff = rec.contract_duration - rec.remaining_contract_duration
                rec.time_based = duration_diff / rec.contract_duration * 100
            # rec.total_list_invoices/rec.amount

