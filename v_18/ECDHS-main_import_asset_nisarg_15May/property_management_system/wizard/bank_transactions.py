from odoo import fields, models


class BankTransactions(models.TransientModel):
    _name = "bank.transactions"
    _description = "Create Bank Transaction"

    enquiry_id = fields.Many2one(
        'property.enquiry',
        string="Property Enquiry"
    )
    name = fields.Char('name')
    date = fields.Char(string="Date")
    description = fields.Char(string="Description")
    amount = fields.Float(string="Amount")
    transaction_type = fields.Selection([
        ('alcohol', 'Alcohol Transaction'),
        ('fuel', 'Fuel Transaction'),
        ('toll', 'Toll Transaction'),
        ('pharmacy', 'Pharmacy Transaction'),
        ('booking_in', 'Booking – Money In'),
        ('booking_out', 'Booking – Money Out'),
        ('debit_reversal', 'Debit Other Reversals'),
        ('gambling', 'Gambling / Betting Transaction'),
    ], string="Transaction Type")

    outside_of_approval_area = fields.Boolean(string="Outside of Approved Area")

    bank_name = fields.Char(string="Bank Name")
    score_card = fields.Char(string="Score Card")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    ind_or_comp = fields.Char(string="Ind/Comp")
    weekend_weekday = fields.Char(string="Weekday/Weekend")

    def action_save(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}


