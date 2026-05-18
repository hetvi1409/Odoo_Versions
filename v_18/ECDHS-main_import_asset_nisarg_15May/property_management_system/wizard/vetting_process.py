from odoo import models, fields, api


class VettingProcess(models.TransientModel):
    _name = "vetting.process.wizard"
    _description = "Vetting Process"

    enquiry_id = fields.Many2one('property.enquiry', required=True)

    # --- ASSETS ---
    bank_accounts = fields.Float("Bank Accounts")
    savings_accounts = fields.Float("Savings Accounts")
    cash_other = fields.Float("Other Cash Assets")

    stock_investment = fields.Float("Stocks / Shares")
    unit_trusts = fields.Float("Unit Trusts")
    brokerage_other1 = fields.Float("Other Investment 1")
    brokerage_other2 = fields.Float("Other Investment 2")

    primary_residence = fields.Float("Primary Residence")
    secondary_residence = fields.Float("Secondary Residence")
    rental_property = fields.Float("Rental Property")
    investment_property = fields.Float("Investment Property")
    vehicle_1 = fields.Float("Vehicle 1")
    vehicle_2 = fields.Float("Vehicle 2")
    property_other = fields.Float("Other Property")

    life_cash_value = fields.Float("Life Policy Cash Value")
    furnishings = fields.Float("Furnishings")
    other_asset1 = fields.Float("Other Asset 1")
    other_asset2 = fields.Float("Other Asset 2")

    # --- LIABILITIES ---
    credit_card1 = fields.Float("Credit Card 1")
    credit_card2 = fields.Float("Credit Card 2")
    credit_card3 = fields.Float("Credit Card 3")
    short_term_other = fields.Float("Other Short-Term")

    loan_primary = fields.Float("Primary Residence Loan")
    loan_secondary = fields.Float("Secondary Residence Loan")
    loan_rental = fields.Float("Rental Property Loan")
    loan_investment = fields.Float("Investment Property Loan")
    loan_vehicle1 = fields.Float("Vehicle Loan 1")
    loan_vehicle2 = fields.Float("Vehicle Loan 2")
    student_loans = fields.Float("Student Loans")
    business_loans = fields.Float("Business Loans")
    loan_other = fields.Float("Other Loans")

    other_liability1 = fields.Float("Other Liability 1")
    other_liability2 = fields.Float("Other Liability 2")
    other_liability3 = fields.Float("Other Liability 3")

    # Computed
    total_assets = fields.Float(string="Total Assets", compute="_compute_totals")
    total_liabilities = fields.Float(string="Total Liabilities", compute="_compute_totals")
    net_worth = fields.Float(string="Net Worth", compute="_compute_totals")

    @api.depends(
        'bank_accounts','savings_accounts','cash_other',
        'stock_investment','unit_trusts','brokerage_other1','brokerage_other2',
        'primary_residence','secondary_residence','rental_property',
        'investment_property','vehicle_1','vehicle_2','property_other',
        'life_cash_value','furnishings','other_asset1','other_asset2',
        'credit_card1','credit_card2','credit_card3','short_term_other',
        'loan_primary','loan_secondary','loan_rental','loan_investment',
        'loan_vehicle1','loan_vehicle2','student_loans','business_loans','loan_other',
        'other_liability1','other_liability2','other_liability3'
    )
    def _compute_totals(self):
        for rec in self:
            # Assets
            total_cash = rec.bank_accounts + rec.savings_accounts + rec.cash_other
            total_brokerage = rec.stock_investment + rec.unit_trusts + rec.brokerage_other1 + rec.brokerage_other2
            total_property = (
                rec.primary_residence + rec.secondary_residence + rec.rental_property +
                rec.investment_property + rec.vehicle_1 + rec.vehicle_2 + rec.property_other
            )
            total_other_assets = rec.life_cash_value + rec.furnishings + rec.other_asset1 + rec.other_asset2

            rec.total_assets = total_cash + total_brokerage + total_property + total_other_assets

            # Liabilities
            total_short_term = rec.credit_card1 + rec.credit_card2 + rec.credit_card3 + rec.short_term_other
            total_loans = (
                rec.loan_primary + rec.loan_secondary + rec.loan_rental + rec.loan_investment +
                rec.loan_vehicle1 + rec.loan_vehicle2 + rec.student_loans + rec.business_loans + rec.loan_other
            )
            total_other = rec.other_liability1 + rec.other_liability2 + rec.other_liability3

            rec.total_liabilities = total_short_term + total_loans + total_other

            rec.net_worth = rec.total_assets - rec.total_liabilities

    def action_apply_to_lead(self):
        self.enquiry_id.write({
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities,
            'net_worth': self.net_worth,
            'state': 'pending'
        })
        return {'type': 'ir.actions.act_window_close'}
