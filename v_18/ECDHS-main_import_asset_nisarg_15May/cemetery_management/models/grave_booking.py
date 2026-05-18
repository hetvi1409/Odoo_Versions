import base64

from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GraveBooking(models.Model):
    """Grave Booking: grave purchase and grave lease"""
    _name = "grave.booking"
    _description = "Grave Booking"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_country_id(self):
        """Returns Country"""
        return self.env.ref('base.za').id

    def _get_province_data(self):
        """Returns province data"""
        return self.env.ref('cemetery_management.province_province_kwaZulu_natal').id

    def _get_municipality(self):
        """Returns municipality data"""
        municipality = self.env['municipality.municipality'].search([('company_id', '=', self.env.company.id)], limit=1)
        return municipality.id

    type = fields.Selection([('purchase', 'Purchase'), ('lease', 'Lease')],
                            string="Type", tracking=True)
    user_type = fields.Selection([('undertaker', 'Undertaker'), ('general', 'General')], tracking=True)
    name = fields.Char(string="Application", default='New', tracking=True)
    date = fields.Date(string="Date Received", default=fields.Date.today())
    state = fields.Selection([('new', 'New'), ('submitted', 'Submitted'),
                              ('verified', 'Verified'),
                              ('allocation', 'Allocation'),
                              ('quotation', 'Quotation'),
                              ('approved', "Approved"),
                              ('rejected', "Rejected")],
                             string="State", default='new', tracking=True)
    ward_id = fields.Many2one('ward.ward', string="Ward",)
    # polt requirements
    interment_type = fields.Selection([
        ('burial', 'Burial'),
        ('cremation', 'Cremation'),
        ('memorial', 'Memorial')
    ], string='Interment Type', required=True, tracking=True)
    grave_number = fields.Char(string="Grave Number")
    attended_by = fields.Selection([('family', 'Attended By Family'),
                                    ('unattended', 'Unattended')],
                                   string="Attended By")
    no_attendees = fields.Integer(string="Number of Attendants")
    time_of_use = fields.Selection([('immediate', "Immediate"),
                                    ('future', 'Future')],
                                   string="Timing of use")
    burial_order = fields.Binary(string="Original burial order signed and "
                                        "stamped by DOHA")
    id_card = fields.Binary(string="Certified copy of Deceased ID or ID card.",
                            help="Certified copy of Deceased ID or ID card. "
                                 "(If it is a Homeless persons with no ID "
                                 "document must produce a SAPS affidavit "
                                 "relating to the deceased.)")
    informant_id_card = fields.Binary(string="Certified copy of Informant/ "
                                             "next of kin ID or ID card")
    death_certificate = fields.Binary(string="Certified copy of Death "
                                             "Certificate or Notice of "
                                             "Death certified")
    cemetery_id = fields.Many2one('cemetery.cemetery', string="Cemetery", required=True,
                                 domain="[('municipality_id', '=?', municipality_id)]", tracking=True)
    field = fields.Integer(string='Field')
    row = fields.Integer(string='Row')
    section_id = fields.Many2one('cemetery.section', string='Section',
                                 domain="[('cemetery_id', '=', cemetery_id)]", tracking=True)
    category = fields.Selection([('general', 'General'), ('vip', 'VIP')],
                                string='Category', required=True)
    municipality_id = fields.Many2one('municipality.municipality',
                                      string="Municipality", readonly=True, default=_get_municipality)
    other_specification = fields.Char(string="Other Specification")
    # Applicant’s details
    applicant_name = fields.Char(string="Full name")
    applicant_email = fields.Char(string="Email")
    applicant_phone = fields.Char(string="Phone")
    street = fields.Char(string="Street",
                         help="Name of the street")
    street2 = fields.Char(string="Street 2",
                          help="Name of the street")
    zip = fields.Char(string="Postal Code", help="Zip code")
    city = fields.Char(string="City", help="Name of the city")
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]",
                               help="Name of the State")
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict', default=_get_country_id,
                                 help="Name of the country")
    province_id = fields.Many2one('province.province', string="Province",
                                  required=False, default=_get_province_data,
                                  domain="[('country_id', '=?', country_id)]")
    applicant_municipality_id = fields.Many2one('municipality.municipality',
                                      string="Municipality",
                                      domain="[('province_id', '=?', province_id)]", default=_get_municipality)

    # Authorisation
    is_same = fields.Boolean(string="Same as the applicant Details")
    authorisation_name = fields.Char(string="Full name")
    authorisation_email = fields.Char(string="Email")
    authorisation_phone = fields.Char(string="Phone")
    authorisation_street = fields.Char(string="Street",
                         help="Name of the street")
    authorisation_street2 = fields.Char(string="Street 2",
                          help="Name of the street")
    authorisation_zip = fields.Char(string="Postal Code", help="Zip code")
    authorisation_city = fields.Char(string="City", help="Name of the city")
    authorisation_state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', authorisation_country_id)]",
                               help="Name of the State")
    authorisation_country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict', default=_get_country_id,
                                 help="Name of the country")
    authorisation_province_id = fields.Many2one('province.province', string="Province",
                                  required=False, default=_get_province_data,
                                  domain="[('country_id', '=?', authorisation_country_id)]")
    authorisation_municipality_id = fields.Many2one('municipality.municipality',
                                                string="Municipality",
                                                domain="[('province_id', '=?', authorisation_province_id)]", default=_get_municipality)

    party_ids = fields.One2many('grave.parties', 'booking_id', string="")

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 help="Company Name",
                                 default=lambda self: self.env.company)
    grave_administrator_ids = fields.One2many('grave.administrator.details', 'booking_id')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', copy=False, tracking=True)
    invoice_count = fields.Integer(string="Invoice Count", compute='_compute_invoice_count')
    invoice_id = fields.Many2one('account.move', copy=False)
    invoice_paid_state = fields.Selection([('paid', 'Paid'),
                                           ('partially', "Partially Paid"),
                                           ('not_paid', 'Not Paid')], compute='_compute_invoice_paid_status')
    allocated_grave_id = fields.Many2one('grave.grave', string='Grave', copy=False, tracking=True)
    approved_date = fields.Datetime(string="Approved Date", readonly=True)
    approved_by_id = fields.Many2one('res.users', string="Approved By", readonly=True)
    rejected_date = fields.Datetime(string="Rejected Date", readonly=True)
    rejected_by_id = fields.Many2one('res.users', string="Rejected By", readonly=True)

    @api.constrains('zip', 'authorisation_zip')
    def constrains_id_number(self):
        """Constrains functionality used to indicate or raise an
        UserError when we adding zip"""
        if self.zip:
            if len(self.zip) != 4 or not (self.zip).isdigit():
                raise UserError(_(
                    "Postal code must be 4 digits"))
        if self.authorisation_zip:
            if len(self.authorisation_zip) != 4 or not (self.authorisation_zip).isdigit():
                raise UserError(_(
                    "Postal code must be 4 digits"))

    @api.model
    def create(self, vals):
        res = super(GraveBooking, self).create(vals)
        if res.type == 'purchase':
            res.name = self.env['ir.sequence'].next_by_code(
                'grave.purchase')
        if res.type == 'lease':
            res.name = self.env['ir.sequence'].next_by_code('grave.lease')
        return res

    def action_submit(self):
        if not self.applicant_name:
            raise UserError(_("Please add the Applicant Full name"))
        if not self.applicant_email:
            raise UserError(_("Please add the Applicant Email"))
        if not self.applicant_phone:
            raise UserError(_("Please add the Phone Number"))
        if not self.street:
            raise UserError(_("Please add the Street"))
        if not self.city:
            raise UserError(_("Please add the City"))
        if not self.country_id:
            raise UserError(_("Please add the Country"))
        if not self.section_id:
            raise UserError(_("Please add the Section"))
        if not self.applicant_municipality_id:
            raise UserError(_("Please add the Municipality"))

        mail_template = self.env.ref(
            'cemetery_management.email_template_grave_booking_created')
        recipient_ids = self.env.ref(
            'cemetery_management.group_cemetery_admin').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.state = 'submitted'

    @api.onchange('is_same', 'applicant_name', 'applicant_email',
                  'street', 'street2', 'city', 'state_id',
                  'applicant_municipality_id',)
    def _onchange_is_same(self):
        """Is same as the applicant details, ath value in the
        authorizations will be auto-populates."""
        if self.is_same:
            self.authorisation_name = self.applicant_name
            self.authorisation_email = self.applicant_email
            self.authorisation_phone = self.applicant_phone
            self.authorisation_street = self.street
            self.authorisation_street2 = self.street
            self.authorisation_city = self.city
            self.authorisation_state_id = self.state_id.id
            self.authorisation_municipality_id = self.applicant_municipality_id.id
            self.authorisation_country_id = self.country_id.id
            self.authorisation_province_id = self.province_id.id

    def get_list_url(self):
        """To generate the link to redirect to booking from the mail"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=grave.booking&view_type=form' % self.id)
        return Urls

    def action_verify(self):
        """Verify the authorization"""
        # if len(self.grave_administrator_ids.ids) < 2:
        #     raise UserError(_('Please add the cemetery administration'))
        self.state = 'verified'

    def action_create_quote(self):
        """Create quotation"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.company_id.partner_id.id,
        })
        product = ""
        if self.interment_type == 'burial':
            product = self.env.ref('cemetery_management.product_product_standard_burial') if self.category == 'general' else self.env.ref('cemetery_management.product_product_vip_burial')
        elif self.interment_type == 'cremation':
            product = self.env.ref('cemetery_management.product_product_standard_cremation') if self.category == 'general' else self.env.ref('cemetery_management.product_product_vip_cremation')
        elif self.interment_type == 'memorial':
            product = self.env.ref('cemetery_management.product_product_standard_memorial') if self.category == 'general' else self.env.ref('cemetery_management.product_product_vip_memorial')
        order_line = self.env['sale.order.line'].create({
            'product_id': product.id,
            'price_unit': product.lst_price,
            'order_id': sale_order.id
        })
        self.sale_order_id = sale_order.id
        self.state = 'quotation'

    def action_view_sale(self):
        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.sale_order_id.id
            }

    def action_view_grave(self):
        return {
            'name': _('Allocated Grave'),
            'type': 'ir.actions.act_window',
            'res_model': 'grave.grave',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.allocated_grave_id.id
            }

    @api.depends('sale_order_id')
    def _compute_invoice_count(self):
        """Compute invoice count"""
        for rec in self:
            count = 0
            if rec.sale_order_id:
                count = len(rec.sale_order_id.mapped('invoice_ids'))
            rec.invoice_count = count

    @api.depends('sale_order_id')
    def _compute_invoice_paid_status(self):
        for rec in self:
            invoice_paid_state = ""
            status = ""
            if self.grave_administrator_ids:
                if self.sale_order_id.invoice_ids:
                    invoice_paid_state = "paid"
                else:
                    invoice_paid_state = "not_paid"
            else:
                if self.sale_order_id.invoice_ids:
                    status = list(set(self.sale_order_id.invoice_ids.mapped('payment_state')))
                if len(status) == 0:
                    invoice_paid_state = 'not_paid'
                elif len(status) == 1:
                    if 'paid' in status:
                        invoice_paid_state = 'paid'
                    elif 'in_payment' in status:
                        invoice_paid_state = 'paid'
                    elif 'partial' in status:
                        invoice_paid_state = 'partially'
                    else:
                        invoice_paid_state = 'not_paid'
                else:
                    if 'paid' in status:
                        invoice_paid_state = 'partially'
                    elif 'partial' in status:
                        invoice_paid_state = 'partially'
                    else:
                        invoice_paid_state = 'not_paid'
            rec.invoice_paid_state = invoice_paid_state

    def action_view_invoice(self):
        invoices = self.sale_order_id.mapped('invoice_ids')
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.sale_order_id.partner_id.id,
                'default_partner_shipping_id': self.sale_order_id.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.sale_order_id.payment_term_id.id or self.sale_order_id.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.sale_order_id.name,
            })
        action['context'] = context
        return action

    def action_quotation_send(self):
        """Send quotation mail"""
        if self.sale_order_id.state == 'cancel':
            raise UserError(_('Quotation was cancelled'))
        report_template_id = self.env['ir.actions.report']._render_qweb_pdf(
            'sale.action_report_saleorder', data = {
            'ids': self.sale_order_id.ids,
            'model': 'sale.order',
            'form': self.env['sale.order'].search([('id', '=', self.sale_order_id.id)])
        })
        data_record = base64.b64encode(report_template_id[0])
        ir_values = {
            'name': "Sale Quotation",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
            'res_id': self.id,
            'res_model': self._name
        }
        data_id = self.env['ir.attachment'].create(ir_values)
        ir_model_data = self.env['ir.model.data']
        try:
            if self.sale_order_id.state not in ['sale', 'cancel']:
                template_id = ir_model_data._xmlid_lookup(
                    'cemetery_management.email_template_grave_booking_sale_order_created')[
                    1]
            if self.sale_order_id.state == 'sale':
                template_id = ir_model_data._xmlid_lookup(
                    'cemetery_management.email_template_grave_booking_sale_order_confirmed')[
                    1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                'mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': self._name,
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, data_id.ids)]
        })
        action = {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        return action

    def action_invoice_send(self):
        """View invoices"""
        for rec in self.sale_order_id.invoice_ids:
            self.invoice_id = rec.id
            if rec.state != 'posted':
                raise UserError(_('Invoice %s was not in posted')% rec.name)
            report_template_id = self.env['ir.actions.report']._render_qweb_pdf(
                'account.account_invoices', data={
                    'ids': rec.ids,
                    'model': 'account.move',
                    'form': self.env['account.move'].search(
                        [('id', '=', rec.id)])
                })
            data_record = base64.b64encode(report_template_id[0])
            ir_values = {
                'name': "Invoice",
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/x-pdf',
                'res_id': self.id,
                'res_model': self._name
            }
            data_id = self.env['ir.attachment'].create(ir_values)
            if rec.state == 'posted' and rec.payment_state == 'paid':
                template_id = self.env.ref(
                    'cemetery_management.email_template_grave_booking_invoice_paid')
            else:
                template_id = self.env.ref(
                    'cemetery_management.email_template_grave_booking_invoice_created')
            email_values = {
                'attachment_ids': [(6, 0, data_id.ids)]
            }
            template_id.send_mail(self.id, force_send=True,
                                    email_values=email_values)

    def action_allocation(self):
        """Allocation of graves"""
        return {
            'name': _('Allocation'),
            'type': 'ir.actions.act_window',
            'res_model': 'grave.allocation',
            'view_mode': 'form',
            'target': 'new',
            'context':
                {
                    'default_booking_id': self.id,
                    'default_section_id': self.section_id.id
                }
        }

    def action_approve(self):
        """Approve the records"""
        self.state ='approved'
        if self.type == 'purchase':
            self.allocated_grave_id.purchased = True
        else:
            self.allocated_grave_id.rented = True
        self.approved_by_id = self.env.user.id
        self.approved_date = fields.Datetime.now()
        template_id = self.env.ref(
            'cemetery_management.email_template_grave_booking_approved')
        template_id.send_mail(self.id, force_send=True,)

    def action_reject(self):
        """Reject the records"""
        self.state = 'rejected'
        if self.type == 'purchase':
            self.allocated_grave_id.purchased = False
        else:
            self.allocated_grave_id.rented = False
        self.rejected_by_id = self.env.user.id
        self.rejected_date = fields.Datetime.now()
        template_id = self.env.ref(
            'cemetery_management.email_template_grave_booking_rejected')
        template_id.send_mail(self.id, force_send=True,)
        self.sale_order_id._action_cancel()

    def unlink(self):
        """"Unlink the records"""
        for rec in self:
            if rec.state != 'new':
                raise UserError(_('Only we can delete the application '
                                  'in new state'))
        return super().unlink()


class PartiesToBuried(models.Model):
    """Parties to be buried"""
    _name = "grave.parties"
    _description = "Parties with right of burial"
    _rec_name = 'surname'

    def _get_country_id(self):
        """Returns Country"""
        return self.env.ref('base.za').id

    def _get_province_data(self):
        """Returns Country"""
        return self.env.ref('cemetery_management.province_province_kwaZulu_natal').id

    def _get_municipality(self):
        """Returns Country"""
        municipality = self.env['municipality.municipality'].search([('company_id', '=', self.env.company.id)], limit=1)
        return municipality.id

    booking_id = fields.Many2one('grave.booking')
    surname = fields.Char(string="Surname", required=True)
    first_name = fields.Char(string="First Name", required=True)
    street = fields.Char(string="Street",
                         help="Name of the street")
    street2 = fields.Char(string="Street 2",
                          help="Name of the street")
    zip = fields.Char(string="Postal Code", help="Zip code")
    city = fields.Char(string="City", help="Name of the city")
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]",
                               help="Name of the State")
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict', default=_get_country_id,
                                 help="Name of the country")
    province_id = fields.Many2one('province.province', string="Province",
                                  required=False, default=_get_province_data,
                                  domain="[('country_id', '=?', country_id)]")
    municipality_id = fields.Many2one('municipality.municipality',
                                                string="Municipality", default=_get_municipality,
                                                domain="[('province_id', '=?', province_id)]")
    date_of_birth = fields.Date(string="Date of birth")
    cemetery_id = fields.Many2one('cemetery.cemetery', related='booking_id.cemetery_id')

    @api.constrains('zip')
    def constrains_id_number(self):
        """Constrains functionality used to indicate or raise an
        UserError when we adding zip"""
        if self.zip:
            if len(self.zip) != 4 or not (self.zip).isdigit():
                raise UserError(_(
                    "Postal code must be 4 digits"))


class GraveCemeteryDetails(models.Model):
    """Grave Cemetery Details"""
    _name = 'grave.administrator.details'
    _description = "Grave Administrative Details"

    number = fields.Char(string="Number", required=True)
    document = fields.Binary(string="Document", required=True)
    booking_id = fields.Many2one('grave.booking')
    section_id = fields.Many2one('cemetery.section', string='Section',
                                 related='booking_id.section_id')


class GraveAllocation(models.Model):
    """Grave Allocation"""
    _name = 'grave.allocation'
    _description = "Grave Allocation"

    booking_id = fields.Many2one('grave.booking', string="Booking")
    cemetery_id = fields.Many2one('cemetery.cemetery', string="Cemetery",
                                  related="booking_id.cemetery_id")
    section_id = fields.Many2one('cemetery.section', string="Section",
                                 readonly=True)
    grave_id = fields.Many2one('grave.grave', string="Grave", required=True,
                               domain="[('section_id', '=', section_id), ('state', '=', 'active')]")
    type = fields.Selection([('automatic', 'Automatic'), ('manual', 'Manual')], default='manual')

    @api.onchange('type')
    def _onchange_type(self):
        """Onchange Type"""
        if self.type == 'automatic':
            grave = self.env['grave.grave'].search([('section_id', '=', self.section_id.id), ('state', '=', 'active')], limit=1)
            self.grave_id = grave.id
        else:
            self.grave_id = ""

    def action_submit(self):
        """Submit the allocation"""
        self.booking_id.allocated_grave_id = self.grave_id.id
        if self.booking_id.type == 'purchase':
            self.grave_id.purchased = True
        else:
            self.grave_id.rented = True
        self.booking_id.state = 'allocation'

