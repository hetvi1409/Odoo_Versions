from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssetImpairment(models.TransientModel):
    _name = 'asset.impairment'
    _description = "Asset Impairment"
    """Class for Asset Impairment"""

    asset_id = fields.Many2one('account.asset', string="Asset",
                               help="ID of the asset")
    asset_ids = fields.Many2many('account.asset', string="Asset", help="List of asset", domain="[('state', '!=', 'model')]")
    asset_id_no = fields.Char(string="Asset Id no", help="Asset Identity number")
    cessation = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Cessation, or near cessation',
                               help="Cessation, or near cessation, of "
                                    "the demand or need for services "
                                    "provided by the asset.")
    long_term_change = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Significant long-term changes',
                                      help="Significant long-term changes with "
                                           "an adverse effect on the entity have"
                                           " taken place during the period or "
                                           "will take place in the near future, "
                                           "in the technological, legal or "
                                           "government policy environment in "
                                           "which the entity operates.")
    evidence = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Evidence is available',
                              help='Evidence is available of obsolescence or '
                                   'physical damage of an asset')
    evidence_document_ids = fields.Many2many('ir.attachment',
                                             string="Evidence document",
                                             help='Evidence document details')
    significant_long_term_change = fields.Selection([('yes', 'Yes'), ('no', 'No')],
        string="Significant long-term "
               "changes",
        help="Significant long-term changes with "
             "an adverse effect on the entity have "
             "taken place during the period, or "
             "are expected to take place in the "
             "near future, in the extent to which, "
             "or manner in which, an asset is used "
             "or is expected to be used. These "
             "changes include the asset becoming"
             " idle, plans to discontinue or "
             "restructure the operation to which an"
             " asset belongs, plans to dispose of "
             "an asset before the previously "
             "expected date and reassessing the "
             "useful life of an asset as finite "
             "rather than indefinite.")
    decision = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Decision to halt the construction of '
                                     'the asset',
                              help="decision to halt the construction of the "
                                   "asset before it is complete or in a "
                                   "usable condition.")
    evidence_internal_report = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Evidence internal report',
                                              help="Evidence is available from internal "
                                                   "reporting that indicates that the "
                                                   "service performance of an asset is, "
                                                   "or will be, significantly worse "
                                                   "than expected.")
    evidence_internal_report_document_ids = fields.Many2many('ir.attachment',
                                                             'evidence_internal_report',
                                                             string="Evidence document",
                                                             help='Evidence document details')
    reason_impairment = fields.Char(string='Reason impairment', help='Reason for impairment')

    def _default_currency_id(self):
        """get currency id"""
        return self.env.user.company_id.currency_id

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True,
                                  default=lambda
                                      self: self._default_currency_id())
    is_service_amount = fields.Boolean(string="Is service amount",
                                       help="Is service amount")
    recoverable_service_amount = fields.Monetary(string='Service amount',
                                                 help="Recoverable service amount",
                                                 compute="_compute_recoverable_service_amount")
    impairment_date = fields.Date(string='Impairment date')

    @api.onchange('cessation', 'long_term_change', 'evidence', 'decision',
                  'significant_long_term_change', 'evidence_internal_report')
    def onchange_service_amount(self):
        """To calculate the service amount"""
        if self.asset_id:
            if self.cessation == 'yes' or self.long_term_change == 'yes' or \
                    self.evidence == 'yes' or \
                    self.significant_long_term_change == 'yes' or \
                    self.decision == 'yes' or self.evidence_internal_report == 'yes':
                self.is_service_amount = True
                if self.asset_id.value_in_use == self.asset_id.fair_value_less_cost_to_sell:
                    self.recoverable_service_amount = self.asset_id.value_in_use
                elif self.asset_id.value_in_use > self.asset_id.fair_value_less_cost_to_sell:
                    self.recoverable_service_amount = self.asset_id.value_in_use
                else:
                    self.recoverable_service_amount = self.asset_id.fair_value_less_cost_to_sell
            else:
                self.is_service_amount = False

    @api.depends('asset_id', 'cessation', 'long_term_change', 'evidence',
                 'decision',
                 'significant_long_term_change', 'evidence_internal_report')
    def _compute_recoverable_service_amount(self):
        """Calculate the amount for recoverable_service_amount"""
        for rec in self:
            if self.asset_id:
                if rec.cessation == 'yes' or rec.long_term_change == 'yes'\
                        or rec.evidence == 'yes' or \
                        rec.significant_long_term_change == 'yes'\
                        or rec.decision == 'yes' or rec.evidence_internal_report == 'yes':
                    if rec.asset_id.value_in_use == rec.asset_id.fair_value_less_cost_to_sell:
                        rec.recoverable_service_amount = rec.asset_id.value_in_use
                    elif rec.asset_id.value_in_use > rec.asset_id.fair_value_less_cost_to_sell:
                        rec.recoverable_service_amount = rec.asset_id.value_in_use
                    else:
                        rec.recoverable_service_amount = rec.asset_id.fair_value_less_cost_to_sell
                else:
                    rec.recoverable_service_amount = 0.0
            else:
                rec.recoverable_service_amount = 0.0

    def action_asset_impairment(self):
        """Asset Impairment"""
        for asset in self.asset_ids:
            if asset.state in ['close', 'cancelled', 'impaired']:
                raise ValidationError(_("Can't impaired this asset, it is already in cancelled or impaired state."))
        if self.asset_id:
            if self.recoverable_service_amount == self.asset_id.carrying_amount:
                pass
            elif self.recoverable_service_amount > self.asset_id.carrying_amount:
                self.asset_id.impairment = 0.0
            else:
                self.asset_id.impairment = self.asset_id.carrying_amount - self.recoverable_service_amount
                self.asset_id.cessation = self.cessation
                self.asset_id.long_term_change = self.long_term_change
                self.asset_id.evidence = self.evidence
                for evidence in self.evidence_document_ids:
                    self.asset_id.evidence_document_ids = [(4, evidence.id)]
                self.asset_id.significant_long_term_change = self.significant_long_term_change
                self.asset_id.decision = self.decision
                self.asset_id.evidence_internal_report = self.evidence_internal_report
                self.asset_id.reason_impairment = self.reason_impairment
                for evidence_report in self.evidence_internal_report_document_ids:
                    self.asset_id.evidence_internal_report_document_ids = [(4, evidence_report.id)]
                self.asset_id.set_to_cancelled()
                self.asset_id.state = 'impaired'
                self.asset_id.is_impaired = True
                self.asset_id.impairment_date = self.impairment_date
        else:
            if not self.asset_ids and not self.asset_id_no:
                raise ValidationError(_('Please select any asset or add a asset id'))
            if self.asset_id_no:
                assets = self.env['account.asset'].search(
                    [('alternative_ref', '=', self.asset_id_no)])
                if not assets:
                    raise ValidationError(
                        _('There is no asset with identifier number'))
            if self.asset_ids:
                assets = self.asset_ids
            for asset in assets:
                if asset.state not in ['impaired', 'cancelled']:
                    recoverable_service_amount = 0
                    if asset.value_in_use == asset.fair_value_less_cost_to_sell:
                        recoverable_service_amount = asset.value_in_use
                    elif asset.value_in_use > asset.fair_value_less_cost_to_sell:
                        recoverable_service_amount = asset.value_in_use
                    else:
                        recoverable_service_amount = asset.fair_value_less_cost_to_sell
                    if recoverable_service_amount == asset.carrying_amount:
                        pass
                    elif recoverable_service_amount > asset.carrying_amount:
                        asset.impairment = 0.0
                    else:
                        asset.impairment = asset.carrying_amount - recoverable_service_amount
                        asset.cessation = self.cessation
                        asset.long_term_change = self.long_term_change
                        asset.evidence = self.evidence
                        for evidence in self.evidence_document_ids:
                            asset.evidence_document_ids = [(4, evidence.id)]
                        asset.significant_long_term_change = self.significant_long_term_change
                        asset.decision = self.decision
                        asset.evidence_internal_report = self.evidence_internal_report
                        asset.reason_impairment = self.reason_impairment
                        for evidence_report in self.evidence_internal_report_document_ids:
                            asset.evidence_internal_report_document_ids = [
                                (4, evidence_report.id)]
                        asset.set_to_cancelled()
                        asset.state = 'impaired'
                        asset.is_impaired = True
                        asset.impairment_date = self.impairment_date
                else:
                    raise ValidationError(_("Can't impair the asset with impaired or cancelled state"))
