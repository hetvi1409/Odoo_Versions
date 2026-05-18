from odoo import models, fields, api

class AnnualProcurementPlanLine(models.Model):
    _name = "annual.procurement.plan.line"
    _description = "Annual Procurement Plan Line"
    _order = "sequence"

    def action_open_record(self):
        self.ensure_one()
        view = self.env.ref('sa_government_tender.view_annual_procurement_plan_line_form', False)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Open Record',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(view.id, 'form')] if view else False,
            'target': 'new',
        }

    plan_id = fields.Many2one("annual.procurement.plan", string="Plan", required=False)

    sequence = fields.Integer(string="Item ID")
    name = fields.Char(string="Ref Number")

    class_of_procurement = fields.Char(string="Class of Procurement",default='Works')
    object_code = fields.Char(string="Object Code",default='5E+07')

    product_id = fields.Many2one("product.product", string="Requirements")
    requirements = fields.Char(string="Requirements Description")

    user_id = fields.Many2one("res.users", string="PMO / End User")

    # DEPRECATED: Legacy field - kept for backward compatibility, computed from procurement_method_config_id
    procurement_method = fields.Selection([
        ('rfq', 'Request for Quotation'),
        ('Request for Proposal', 'Request for Proposal'),
        ('Request for Quotation', 'Request for Quotation'),
        ('Request For Quotations method', 'Request For Quotations method'),
        ('tender', 'Competitive Tender'),
        ('Open Tender', 'Open Tender'),
        ('single_source', 'Single Source'),
        ('unsolicited', 'Unsolicited Proposal'),
        ('emergency', 'Emergency Procurement'),
        ('Pre Qualification', 'Pre Qualification'),
        ('Restricted Tender', 'Restricted Tender'),
        ('Restricted Bidding Method', 'Restricted Bidding Method'),
        ('Direct Procurement', 'Direct Procurement / Benchmarking'),
        ('Direct Procurement Method', 'Direct Procurement Method / Benchmarking'),
        ('Framework Agreement', 'Framework Agreement'),
        ('Competitive Bidding Method', 'Competitive Bidding Method'),
        ('Single-source selection method', 'Single-source selection method'),
        ('Selection of Individual consultant method', 'Selection of Individual consultant method'),
        ('Selection Amongst Community Service Organizations', 'Selection Amongst Community Service Organizations'),
        ('Expression of Intrest', 'Expression of Intrest'),
        ('other', 'Other'),
    ], string='Procurement Method (Legacy)', compute='_compute_legacy_fields', store=True, readonly=True,
       help='DEPRECATED: Use procurement_method_config_id instead. This field is auto-computed for compatibility.')

    procurement_method_config_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method Configuration',
        help='Recommended procurement method based on line value'
    )
    preference_point_system_config_id = fields.Many2one(
        'sagovpreference.point.system',
        string='Preference Point System Configuration',
        help='Recommended preference point system based on line value'
    )

    eoi_publication_date = fields.Date(string="EOI Publication Date")
    eoi_closing_date = fields.Date(string="EOI Closing Date")

    tender_notice_date = fields.Date(string="Tender Notice Publication Date")
    tender_closing_date = fields.Date(string="Tender Closing Date")
    award_publication_date = fields.Date(string="Publication of Award Notice")
    contract_signing_date = fields.Date(string="Contract Signing")

    cycle_work_days = fields.Integer(string="Cycle (Work Days) Tender Award Notice")
    lead_time_days = fields.Integer(string="Lead Time (Days)")

    spoc_required = fields.Selection([
        ("yes", "Y"),
        ("no", "N")
    ], string="SPOC Required")

    source_of_funds = fields.Char(string="Source of Funds")

    uom_id = fields.Many2one("uom.uom", string="UoM")
    quantity = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    mode = fields.Float(string="Mode")
    co = fields.Float(string="CO")
    total = fields.Float(
        string="Total(Mode+CO)",
        compute="_compute_total",
        store=True,
    )
    comment = fields.Char(string="Comment")

    # link to created tender to avoid duplicates
    tender_id = fields.Many2one('tender.tender', string='Tender')
    tender_created = fields.Boolean(string="Tender Created", default=False)

    # link to sagov annual procurement plan
    sagov_app_id = fields.Many2one('sagovtender.annual.procurement.plan', string='Approved APP')
    sagov_app_created = fields.Boolean(string="Sagov APP Created", default=False)

    @api.depends("mode", "co")
    def _compute_total(self):
        for line in self:
            line.total = (line.mode or 0) + (line.co or 0)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._set_procurement_config_defaults()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(key in vals for key in ['total', 'unit_price', 'quantity', 'mode', 'co']):
            self._set_procurement_config_defaults()
        return res

    def _get_line_estimated_value(self):
        self.ensure_one()
        if self.total:
            return self.total
        if self.unit_price and self.quantity:
            return self.unit_price * self.quantity
        return 0.0

    @api.onchange('total', 'unit_price', 'quantity', 'mode', 'co')
    def _onchange_line_value(self):
        for line in self:
            estimated_value = line._get_line_estimated_value()
            if estimated_value:
                method = line.env['sagovprocurement.method'].get_applicable_method(
                    estimated_value
                )
                if method:
                    line.procurement_method_config_id = method
                    if method.preference_point_system_ids:
                        line.preference_point_system_config_id = method.preference_point_system_ids[0]

    @api.depends('procurement_method_config_id')
    def _compute_legacy_fields(self):
        """Compute legacy field from configuration field for backward compatibility"""
        for line in self:
            if line.procurement_method_config_id:
                # Map config method to selection value
                method_name = line.procurement_method_config_id.name
                if 'RFQ' in method_name or 'Quotation' in method_name:
                    line.procurement_method = 'rfq'
                elif 'Competitive' in method_name or 'Tender' in method_name:
                    line.procurement_method = 'tender'
                elif 'Single' in method_name or 'Sole' in method_name:
                    line.procurement_method = 'single_source'
                elif 'Emergency' in method_name:
                    line.procurement_method = 'emergency'
                else:
                    line.procurement_method = 'other'
            else:
                line.procurement_method = False

    @api.onchange('procurement_method_config_id')
    def _onchange_procurement_method_config(self):
        """When procurement method changes, update related fields and trigger dependent calculations"""
        for line in self:
            if line.procurement_method_config_id:
                if line.procurement_method_config_id.preference_point_system_ids:
                    line.preference_point_system_config_id = (
                        line.procurement_method_config_id.preference_point_system_ids[0]
                    )

    @api.onchange('preference_point_system_config_id')
    def _onchange_preference_point_system_config(self):
        """When preference point system changes, trigger dependent calculations"""
        # Ensure dependent fields are properly recalculated on form change
        pass

    def _set_procurement_config_defaults(self):
        for line in self:
            estimated_value = line._get_line_estimated_value()
            if not estimated_value:
                continue
            if line.procurement_method_config_id:
                continue
            method = line.env['sagovprocurement.method'].get_applicable_method(
                estimated_value
            )
            if method:
                line.procurement_method_config_id = method
                if method.preference_point_system_ids:
                    line.preference_point_system_config_id = method.preference_point_system_ids[0]
