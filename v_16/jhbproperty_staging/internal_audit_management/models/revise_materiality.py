
from odoo import api, fields, models, _


class ReviseMaterial(models.Model):
    """Determine And Revise Materiality"""
    _name = 'revise.materiality'
    _description = "Revise Materiality"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    materiality_type = fields.Selection([
        ('inventory_value', 'Percentage Of Inventory Value'),
        ('gross_margin_method', 'Gross Margin Method'),
        ('realizable_value', 'Net Realizable Value (NRV) Method'),
        ('goods_sold', 'Cost of Goods Sold (COGS) Method'),
        ('operating_expenditure', 'Total Operating Expenditure (OPCS) Method')],
        string="Difine Materiality", required=True,
        help="""- Percentage of Inventory Value: (Value of Item / Total Inventory Value) x 100
                - Gross Margin Method: (Value of Item / Gross Margin) x 100
                - Net Realizable Value (NRV) Method: (NRV of Item / Total NRV of Inventory) x 100
                - Cost of Goods Sold (COGS) Method: (Value of Item / COGS) x 100
                - Total Operating Expenditure (OPCS) Method: (Value of Item / OPCS) x 100""")
    display_formular = fields.Char(string="Display Formular", readonly=True)
    numerator = fields.Float(string="Numerator")
    abnormal_items_specific = fields.Float(string="Less: Abnormal Items "
                                                   "For Specific Testing")
    final_numerator = fields.Float(string="Final Numerator")
    denominator = fields.Float(string="Denominator")
    materiality = fields.Float(string="Materiality")
    performance_materiality = fields.Char(string="Performance Materiality")
    trivial_amount = fields.Char(string="Trivial Amount")
    revise_materiality_tracking_ids = fields.One2many('revise.materiality.tracking', 'revise_materiality_tracking_id', string='Tracking')
    user_id = fields.Many2one('res.users', tracking=True,
                              string="Responsible User")
    feedback = fields.Char(string="Feedback", tracking=True)
    comment_ids = fields.One2many('audit.comments', 'revise_materiality_id',
                                  tracking=True, string="Comments")

class ReviseMaterialityTracking(models.Model):
    _name = 'revise.materiality.tracking'
    _description = 'Revise Materiality Tracking'

    revise_materiality_tracking_id = fields.Many2one('revise.materiality', string='Revise Materiality')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
                              ('approve', 'Approve')],
                             default="new", string="Previous Stage")
    new_stage_id = fields.Selection([('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
                                  ('approve', 'Approve')],
                                 default="new", string="New Stage")
    comment = fields.Text(string='Comment')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)

class AuditComments(models.Model):
    """Audit Comments"""
    _name = 'audit.comments'
    _description = "Audit Comments"

    name = fields.Text(string="Comments", required=True, tracking=True)
    financial_statement_id = fields.Many2one('financial.statement', string="Financial Information")
    quality_control_id = fields.Many2one('internal.quality.control', string="Internal Quality Control")
    control_peer_id = fields.Many2one('quality.control.peer', string="Quality Control Peer")
    outsourced_peer_id = fields.Many2one('quality.control.outsourced.peer', string="Quality Control Outsource Peer")
    audit_charter_id = fields.Many2one('internal.audit.charter', string="Audit Charter")
    audit_plan_id = fields.Many2one('internal.audit.plan', string="Internal Audit Plan")
    audit_strategy_id = fields.Many2one('audit.strategy', string="Audit Strategy")
    revise_materiality_id = fields.Many2one('revise.materiality', string="Revise Materiality")


