import base64

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class RentalContract(models.Model):
    _inherit = "rental.contract"

    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")

    installment_count = fields.Integer(string="Installment", compute="_compute_installment_count")
    attach_line_count = fields.Integer(string="Installment", compute="_compute_installment_count")

    # date_from = fields.Date(string="Beneficial Occupation Date")
    beneficial_occupation_period  = fields.Date(string="Beneficial Occupation Period")
    lease_comm_date  = fields.Date(string="Lease Commencement Date")
    lease_term = fields.Selection([
        ('6', '6 months'),
        ('12', '12 months / 1 year'),
        ('18', '18 months / 1.5 year'),
        ('24', '24 months / 2 years'),
        ('36', '36 months / 3 years'),
        ('48', '48 months / 4 years'),
        ('60', '60 months / 5 years'),
        ('72', '72 months / 6 years'),
        ('120', '120 months / 10 years'),
    ], string='Lease Term')
    # date_to = fields.Date(string="Lease End Date")
    lease_duration_years = fields.Integer(string="Lease Duration Years", compute="_compute_lease_duration")
    lease_duration_months = fields.Integer(string="Lease Duration Months", compute="_compute_lease_duration")
    lease_duration_days = fields.Integer(string="Lease Duration Days", compute="_compute_lease_duration")

    total_agent_commission = fields.Float(string="Total Agent Commission")
    total_com_amount_excluded_vat = fields.Float(string="Total Commission Excluded Vat")

    total_area = fields.Float(string="Total Area (m2)")
    net_rent = fields.Float(string="Net Rent (Rates)")
    net_rent_monthly = fields.Monetary(string="Net Rent (Monthly)", compute="_compute_net_rent_monthly")
    net_rent_annual = fields.Monetary(string="Total Annual Net Rent)", compute="_compute_net_rent_monthly")
    is_tax_rates = fields.Boolean(string="Tax Rates Enabled")
    rates_tax = fields.Monetary(string="Rates & Taxes (p/m2)")
    rates_tax_monthly = fields.Monetary(string="Rates & Taxes (Monthly)",
                                        compute="_compute_rates_tax_monthly")
    rates_tax_annual = fields.Monetary(string="Total Annual Rates & Taxes ",
                                        compute="_compute_rates_tax_monthly")
    is_levy = fields.Boolean(string="Levy Enabled")
    levy_rate = fields.Float(string="Levy Rate (p/m2)")
    levy_rate_monthly = fields.Float(string="Levy Rate (Monthly)", compute="_compute_levy_rate_monthly")
    levy_rate_annual = fields.Float(string="Total Annual Levies Rate", compute="_compute_levy_rate_monthly")
    is_parking = fields.Boolean(string="Parking Enabled")
    parking = fields.Integer(string="No.of Parking")
    parking_bays = fields.Monetary(string="Parking Bays")
    parking_bays_monthly = fields.Monetary(string="Parking Bays (Monthly)",
                                           compute="_compute_parking_bays_monthly")
    parking_bays_annual = fields.Monetary(string="Total Annual Parking Bays",
                                           compute="_compute_parking_bays_monthly")
    sign_template_id = fields.Many2one('sign.template', string="Sign Template", copy=False)
    otl_sign_template_id = fields.Many2one('sign.template', string="OTL Sign Template", copy=False)
    lead_id = fields.Many2one('crm.lead', string="Lead")
    deposit_amount = fields.Monetary(string="Deposit Amount", )
    current_interest_accrued = fields.Float(string="Current Interest Accrued", compute="_compute_current_interest")
    section_number = fields.Char(string="Section Number")
    annual_escalation = fields.Float(string="Annual Escalation")
    additional_area = fields.Float(string="Additional Area")
    additional_area_rate = fields.Float(string="Additional Area Rate")
    additional_area_rate_monthly = fields.Float(string="Additional Area Rate (Monthly)", compute="_compute_additional_area_rate_monthly")

    @api.depends('additional_area', 'additional_area_rate')
    def _compute_additional_area_rate_monthly(self):
        for rec in self:
            rec.additional_area_rate_monthly = rec.additional_area * rec.additional_area_rate

    @api.onchange('levy_rate_monthly', 'parking_bays_monthly',
                  'additional_area_rate_monthly', 'net_rent_monthly',
                  'rates_tax_monthly', 'is_tax_rates',
                  'is_parking', 'is_levy')
    def _onchange_building(self):
        for rec in self:
            rental_fee = rec.net_rent_monthly + rec.additional_area_rate_monthly
            if rec.is_tax_rates:
                rental_fee = rental_fee + rec.rates_tax_monthly
            if rec.is_parking:
                rental_fee = rental_fee + rec.parking_bays_monthly
            if rec.is_levy:
                rental_fee = rental_fee + rec.levy_rate_monthly
            rec.rental_fee = rental_fee

    @api.depends('date_from', 'date_to', 'deposit_amount')
    def _compute_current_interest(self):
        Rate = self.env['property.interset']

        for rec in self:
            if not (
                    rec.date_from and rec.date_to and rec.deposit_amount):
                rec.current_interest_accrued = 0
                continue

            total_interest = 0
            start = rec.date_from
            end = rec.date_to

            # get all interest table records overlapping this lease
            rate_lines = Rate.search([
                ('start_date', '<=', end),
                ('end_date', '>=', start),
            ])
            for line in rate_lines:
                period_start = max(start, line.start_date)
                period_end = min(end, line.end_date or end)

                days = (period_end - period_start).days + 1

                # yearly simple interest
                daily_rate = (line.interest_rate / 100) / 365
                interest_for_period = rec.deposit_amount * daily_rate * days

                total_interest += interest_for_period

            rec.current_interest_accrued = rec.deposit_amount + total_interest

    @api.depends()
    def _compute_installment_count(self):
        for rec in self:
            rec.installment_count = len(rec.loan_line)
            rec.attach_line_count = len(rec.attach_line)

    def action_view_installment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Installments',
            'view_mode': 'list',
            'res_model': 'loan.line.rs.rent',
            'domain': [('id', 'in', self.loan_line.ids)
                       ],
            'context': "{'create': False}"
        }

    def action_view_attach_line(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Installments',
            'view_mode': 'list,form',
            'res_model': 'rental.attachment.line',
            'domain': [('id', 'in', self.attach_line.ids)],
            'context': {'default_contract_id_att': self.id}
        }

    @api.depends('date_to', 'date_from')
    def _compute_lease_duration(self):
        for rec in self:
            lease_duration_years = 0
            lease_duration_days = 0
            lease_duration_months = 0
            if rec.date_to and rec.date_from:
                delta = relativedelta(rec.date_to,
                                      rec.date_from)
                lease_duration_years = delta.years
                lease_duration_months = delta.months
                lease_duration_days = delta.days
            rec.lease_duration_years = lease_duration_years
            rec.lease_duration_days = lease_duration_days
            rec.lease_duration_months = lease_duration_months

    @api.depends('net_rent', 'total_area')
    def _compute_net_rent_monthly(self):
        """Net rent monthly"""
        for rec in self:
            net_rent_monthly = rec.net_rent * rec.total_area
            rec.net_rent_monthly = net_rent_monthly
            rec.net_rent_annual = net_rent_monthly * 12

    @api.depends('rates_tax', 'total_area')
    def _compute_rates_tax_monthly(self):
        """"""
        for rec in self:
            rec.rates_tax_monthly = rec.total_area * rec.rates_tax
            rec.rates_tax_annual = rec.total_area * rec.rates_tax * 12

    @api.depends('levy_rate', 'total_area')
    def _compute_levy_rate_monthly(self):
        """"""
        for rec in self:
            rec.levy_rate_monthly = rec.total_area * rec.levy_rate
            rec.levy_rate_annual = rec.total_area * rec.levy_rate * 12

    @api.depends('parking', 'parking_bays')
    def _compute_parking_bays_monthly(self):
        for rec in self:
            rec.parking_bays_monthly = rec.parking * rec.parking_bays
            rec.parking_bays_annual = rec.parking * rec.parking_bays * 12

    def action_contract_sign_document(self):
        """Contract Sign Document"""
        pdf_report = self.env.ref(
            'real_estate_management.action_rental_contract_sign_report')
        pdf_content, _report_type = self.env['ir.actions.report']._render_qweb_pdf(
            pdf_report.report_name,
            res_ids=self.ids,)

        file_name = f"Rental_Contract_{self.name or 'Contract'}.pdf"
        attachment = self.env['ir.attachment'].search([('res_id', '=', self.id),
                                                       ('name', '=', file_name),
                                                       ('res_model', '=', self._name)], limit=1)
        if not attachment:
            attachment = self.env['ir.attachment'].create({
                'name': file_name,
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'mimetype': 'application/pdf',
                'res_model': 'rental.contract',
                'res_id': self.id,
            })
        sign_template = self.env['sign.template'].sudo().search([
            ('name', '=', f"Rental Contract - {self.name}"),
            ('contract_id', '=', self.id)
        ], limit=1)
        if not sign_template:
            sign_template = self.env['sign.template'].sudo().create({
                'attachment_id': attachment.id,
                'name': f"Rental Contract - {self.name}",
                # 'share_link': random_link,
                # 'privacy': 'employee',
                'contract_id': self.id,
            })
        self.sign_template_id = sign_template.id
        SOURCE_TEMPLATE_ID = self.env['ir.config_parameter'].sudo().get_param('real_estate_management.sign_template_id')
        source_template = self.env['sign.template'].browse(int(SOURCE_TEMPLATE_ID)) if SOURCE_TEMPLATE_ID else self.env['sign.template'].search([], limit=1)
        for item in source_template.sign_item_ids:
            self.env['sign.item'].sudo().create({
                'template_id': sign_template.id,
                'height': item.height,
                'width': item.width,
                'posX': item.posX,
                'posY': item.posY,
                'page': item.page,
                'type_id': item.type_id.id,
                'required': item.required,
                'name': item.name,
                'responsible_id': item.responsible_id.id,
            })

    def go_to_custom_template(self, sign_directly_without_mail=False):
        self.ensure_one()
        return {
            'name': "Template \"%(name)s\"" % {'name': self.sign_template_id.attachment_id.name},
            'type': 'ir.actions.client',
            'tag': 'sign.Template',
            'params': {
                'id': self.sign_template_id.id,
                'sign_directly_without_mail': sign_directly_without_mail,
            },
        }
    def go_to_otl_custom_template(self, sign_directly_without_mail=False):
        self.ensure_one()
        return {
            'name': "Template \"%(name)s\"" % {'name': self.otl_sign_template_id.attachment_id.name},
            'type': 'ir.actions.client',
            'tag': 'sign.Template',
            'params': {
                'id': self.otl_sign_template_id.id,
                'sign_directly_without_mail': sign_directly_without_mail,
            },
        }

    def action_crm_lead(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lead',
            'view_mode': 'form',
            'res_model': self.lead_id._name,
            'res_id': self.lead_id.id,
            'context': "{'create': False}"
        }

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.lead_id:
            res.lead_id.contract_id = res.id
        return res

    def action_contract_otl_sign_report(self):
        """OTL Sign Documents"""
        pdf_report = self.env.ref(
            'real_estate_management.action_rental_contract_report')
        pdf_content, _report_type = self.env['ir.actions.report']._render_qweb_pdf(
            pdf_report.report_name,
            res_ids=self.ids,)

        file_name = f"Rental_Contract_OTL_{self.name or 'Contract'}.pdf"
        attachment = self.env['ir.attachment'].search([('res_id', '=', self.id),
                                                       ('name', '=', file_name),
                                                       ('res_model', '=', self._name)], limit=1)
        if not attachment:
            attachment = self.env['ir.attachment'].create({
                'name': file_name,
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'mimetype': 'application/pdf',
                'res_model': 'rental.contract',
                'res_id': self.id,
            })
        sign_template = self.env['sign.template'].sudo().search([
            ('name', '=', f"Rental_Contract_OTL_{self.name}"),
            ('contract_id', '=', self.id)
        ], limit=1)
        if not sign_template:
            sign_template = self.env['sign.template'].sudo().create({
                'attachment_id': attachment.id,
                'name': f"Rental_Contract_OTL_{self.name}",
                # 'share_link': random_link,
                # 'privacy': 'employee',
                'contract_id': self.id,
            })
        self.otl_sign_template_id = sign_template.id
        SOURCE_TEMPLATE_ID = self.env['ir.config_parameter'].sudo().get_param(
            'real_estate_management.otl_sign_template_id')
        source_template = self.env['sign.template'].browse(
            int(SOURCE_TEMPLATE_ID)) if SOURCE_TEMPLATE_ID else self.env[
            'sign.template'].search([], limit=1)
        for item in source_template.sign_item_ids:
            self.env['sign.item'].sudo().create({
                'template_id': sign_template.id,
                'height': item.height,
                'width': item.width,
                'posX': item.posX,
                'posY': item.posY,
                'page': item.page,
                'type_id': item.type_id.id,
                'required': item.required,
                'name': item.name,
                'responsible_id': item.responsible_id.id,
            })

