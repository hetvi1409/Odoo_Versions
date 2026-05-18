from odoo import models, fields, api, _
from datetime import datetime, date
from ast import literal_eval
# from mock.mock import self
from odoo.exceptions import UserError, ValidationError
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_due = fields.Monetary(compute='_compute_for_followup', store=False, readonly=True)

    # def _compute_for_followup(self):
    #     for record in self:
    #         total_due = 0
    #         invoice = self.env['account.move'].search([('partner_id', '=', self.id), ('state', '=', 'open')])
    #         for rec in invoice:
    #             total_due += rec.residual

    #         record.total_due = total_due


    def _compute_for_followup(self):
        for record in self:
            total_due = 0
            # use record.id, not self.id
            invoices = self.env['account.move'].search([
                ('partner_id', '=', record.id),
                ('state', '=', 'open'),
            ])
            for inv in invoices:
                total_due += inv.residual

            record.total_due = total_due

    def open_action_followup(self):
        self.ensure_one()
        partner_id = self.env['account.move'].search([('partner_id', '=', self.id), ('state', '=', 'open')])
        if partner_id:
            if len(partner_id) == 1:
                return {
                    'name': 'Due Invoice',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'res_id': partner_id.id,
                }
            else:
                return {
                    'name': 'Due Invoice',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree,form',
                    'domain': [('partner_id', '=', self.id), ('state', '=', 'open')],
                    'res_model': 'account.move',
                }


class res_partner(models.Model):
    _inherit = 'res.partner'

    def name_get(self):
        if not self._context.get('patient_ctx_toms'):
            return super(res_partner, self).name_get()
        return [(rec.id, '%s' % rec.name) for rec in self]

    def get_links(self):
        web_link_1 = self.env['ir.config_parameter'].sudo().get_param("external_links")
        web_link_2 = self.env['ir.config_parameter'].sudo().get_param("aeye_url")
        web_link_3 = self.env['ir.config_parameter'].sudo().get_param("disc_url")
        web_link_4 = self.env['ir.config_parameter'].sudo().get_param("isoleso_url")
        self.external_links = web_link_1
        self.aeye_url_contact = web_link_2
        self.disc_url_contact = web_link_3
        self.isoleso_url_contact = web_link_4


    is_a_medical_aid = fields.Boolean(string="Is a Medical Aid")
    is_a_medical_aid_administrator = fields.Boolean(string="Is a Medical Aid Administrator")
    medical_aid_plan_ids = fields.One2many('medical.aid.plan', 'medical_aid_id', string="Plans")
    administrator_id = fields.Many2one('res.partner', string="Administrator")
    destination_code = fields.Char(string="Destination Code")
    msv_allowed = fields.Boolean(string="MSV Allowed")
    scr_allowed = fields.Boolean(string="SwitchClaim Reversal Allowed")
    st_allowed = fields.Boolean(string="Statistical Transactions Allowed")
    mpc_allowed = fields.Boolean(string="Member Paid Claims Allowed")
    era_active = fields.Boolean(string="eRA Active")
    ba_allowed = fields.Boolean(string="Benefit Availability Allowed")
    bc_allowed = fields.Boolean(string="Benefit Check Allowed")
    period_cycle = fields.Char(string="Period/Cycle")
    is_contracted = fields.Boolean(string="Contracted")
    admin_code = fields.Char(string="Admin Code")
    medical_aid_key = fields.Char(string="Medical Aid Key")
    patient_number = fields.Char(string="Patient Number")
    surname = fields.Char(string="Surname")
    medical_aid_id = fields.Many2one('res.partner', string="Medical Aid")
    option_id = fields.Many2one('medical.aid.plan', string="Plan")
    plan_option_id = fields.Many2one('medical.aid.plan.option', string="Option", domain="[('plan_id','=',option_id)]")
    medical_aid_no = fields.Char(string="Medical Aid No")
    dependent_code = fields.Char(string="Dependent Code", size=3)
    initials = fields.Char(string="Initials")
    first_name = fields.Char(string="First Name")
    nick_name = fields.Char(string="Nickname")
    id_number = fields.Char(string="ID Number", size=13)
    birth_date = fields.Date(string="Birthday")
    gender = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Gender")
    employer = fields.Char(string="Employer")
    occupation = fields.Many2one('customer.occupation', string='Occupation')
    function_id = fields.Many2one('customer.function', string="Job Description")
    communication = fields.Selection([('cell_phone', 'Cell Phone'),
                                      ('email', 'Email'),
                                      ('fax', 'Fax'),
                                      ('post', 'Post'),
                                      ('telephone_home', 'Telephone - Home'),
                                      ('telephone_work', 'Telephone - Work'),
                                      ])
    file_no = fields.Integer(string="File No")
    old_system_no = fields.Char(string="Old System No")
    work_address = fields.Char(string="Work Address")
    work_phone = fields.Char(string="Work Phone")
    # source_ids = fields.Many2many('customer.source', string="Source")
    source_id = fields.Many2one('customer.source', string="Source")
    individual_internal_ref = fields.Char(string="")
    home_street = fields.Char(string="")
    home_street2 = fields.Char(string="")
    home_city = fields.Char(string="")
    home_state_id = fields.Many2one('res.country.state', string="")
    home_zip = fields.Char(string="")
    home_country_id = fields.Many2one('res.country', string="")
    work_street = fields.Char(string="")
    work_street2 = fields.Char(string="")
    work_city = fields.Char(string="")
    work_state_id = fields.Many2one('res.country.state', string="")
    work_zip = fields.Char(string="")
    work_country_id = fields.Many2one('res.country', string="")
    is_key_member = fields.Boolean(string="Is Key Member", default=True)
    is_dependent = fields.Boolean(string="Is Dependent")
    contact_type = fields.Selection([('contact', 'Contact')], default="contact")
    msv_later_button = fields.Boolean(string="MSV Later")
    msv_partner_id = fields.Many2one('res.partner', string="Msv's Partner")
    msv_latest_date = fields.Datetime(string="Latest Msv Date")
    msv_status = fields.Text(string="MSV Status")
    sport = fields.Many2many('hway.sport', string="Do You Play Sport")
    hobby = fields.Many2many('hway.hobby', string="Do You have a hobby")
    doyou = fields.Many2many('hway.doyou', string="Do You")
    doesyour = fields.Many2many('hway.doesyour', string="Does your")
    secondary_mobile = fields.Char(string="Secondary Mobile")
    customer_language = fields.Many2one('customer.language', string='Patient Language')
    external_links = fields.Boolean(compute=get_links, store=False)
    aeye_url_contact = fields.Boolean(compute=get_links, store=False)
    disc_url_contact = fields.Boolean(compute=get_links, store=False)
    isoleso_url_contact = fields.Boolean(compute=get_links, store=False)
    previous_optom = fields.Many2one('res.users', string="Previous Optometrist")



    def isoleso_url(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Redirect to the Website for isolesso",
            'target': 'new',
            'url': "https://rem.isoleso.co.za/"
        }
    def aeye_url(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Redirect to the Website for a eye",
            'target': 'new',
            'url': "https://www.africavisioninstitute.co.za/"
        }

    def disc_url(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Redirect to the Website for discovery",
            'target': 'new',
            'url': "https://id.discovery.co.za/Account/Login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fresponse_type%3Dcode%26client_id%3DC99441A5246AAA4DE541%26scope%3Dopenid%2520offline_access%2520sso%26redirect_uri%3Dhttps%253A%252F%252Fwww.discovery.co.za%252Fportal%252Fddid%252Flogin.do%26state%3De30%253D"
        }
    @api.onchange('display_name','surname','nick_name','first_name','name')
    def _title_case(self):
        if self.display_name:
            self.display_name = str(self.display_name).title()
        if self.surname:
            self.surname = str(self.surname).title()
        if self.nick_name:
            self.nick_name = str(self.nick_name).title()
        if self.first_name:
            self.first_name = str(self.first_name).title()
        if self.name:
            self.name = str(self.name).title()
        if self.employer:
            self.employer = str(self.employer).title()

    @api.onchange('company_type')
    def onchange_company_type(self):
        super(res_partner, self).onchange_company_type()
        if self.company_type == 'person' and not self.parent_id:
            self.medical_aid_id = self.env.ref("TOMS.medical_aid_private")
        else:
            self.medical_aid_id = False

    @api.onchange('medical_aid_id')
    def _onchange_medical_aid(self):
        if self.medical_aid_id.name == 'Private':
            self.property_payment_term_id = self.env.ref('account.account_payment_term_immediate').id
        else:
            self.property_payment_term_id = self.env.ref('account.account_payment_term_15days').id

    @api.model
    def create(self, vals):
        # self = self.with_context(key='from_create')
        # if vals.get('customer') and vals.get('company_type') == 'person':
        #     vals.update({'name': vals.get('first_name', '') + ' ' + vals.get('surname', '')})
        # if vals.get('email'):
        #     if not re.search(r'\w+@\w+', vals.get('email')):
        #         raise ValidationError(_("Invalid Email Address"))
        res = super(res_partner, self).create(vals)

        return res

    def write(self, vals):

        # Email validation
        if vals.get('email'):
            if not re.search(r'\w+@\w+', vals.get('email')):
                raise ValidationError(_("Invalid Email Address"))

        for record in self:

            first_name = vals.get('first_name', record.first_name or '')
            surname = vals.get('surname', record.surname or '')

            # Build name safely
            name_parts = []
            if first_name:
                name_parts.append(first_name)
            if surname:
                name_parts.append(surname)

            if name_parts:
                vals['name'] = " ".join(name_parts)

        # Call super ONCE
        res = super(res_partner, self).write(vals)

        # Handle key member logic AFTER write
        for record in self:
            if record.is_key_member and not record.parent_id:
                for child in record.child_ids:
                    child.with_context(is_write=True).write({
                        'option_id': vals.get('option_id', record.option_id.id),
                        'phone': vals.get('phone', record.phone),
                        'medical_aid_id': vals.get('medical_aid_id', record.medical_aid_id.id),
                        'plan_option_id': vals.get('plan_option_id', record.plan_option_id.id),
                    })

        return res

    # def write(self, vals):
    #     for id in self:
    #         if vals.get('email'):
    #             if not re.search(r'\w+@\w+', vals.get('email')):
    #                 raise ValidationError(_("Invalid Email Address"))
    #         first_name = vals.get('first_name', '')
    #         surname = vals.get('surname', '')
    #         if first_name and surname:
    #             vals['name'] = ''
    #             if first_name:
    #                 vals['name'] += (first_name)
    #             if surname:
    #                 vals['name'] += ' ' + (surname)
    #         if first_name and not surname:
    #             vals['name'] = ''
    #             if first_name:
    #                 vals['name'] += (first_name)
    #                 vals['name'] += ' ' + (id.surname)
    #         if surname and not first_name:
    #             vals['name'] = ''
    #             if surname:
    #                 vals['name'] += (id.first_name)
    #                 vals['name'] += ' ' + (surname)
    #         res = super(res_partner, self).write(vals)
    #         if id.is_key_member and not id.parent_id:
    #             for each in id.child_ids:
    #                 each.with_context(is_write=True).write({
    #                     'option_id': vals.get('option_id') or id.option_id.id,
    #                     'phone': vals.get('phone') or id.phone,
    #                     'medical_aid_id': vals.get('medical_aid_id') or id.medical_aid_id.id,
    #                     'plan_option_id': vals.get('plan_option_id') or id.plan_option_id.id
    #                 })
    #         return res

    # def write(self, vals):
    #
    #     if 'email' in vals and vals['email']:
    #         if not re.search(r'\w+@\w+', vals['email']):
    #             raise ValidationError(_("Invalid Email Address"))
    #
    #     for record in self:
    #         first_name = vals.get('first_name', record.first_name) or ''
    #         surname = vals.get('surname', record.surname) or ''
    #
    #         if 'first_name' in vals or 'surname' in vals:
    #             vals['name'] = " ".join(filter(None, [first_name, surname]))
    #
    #     res = super().write(vals)
    #
    #     for record in self.filtered(lambda r: r.is_key_member and not r.parent_id):
    #         record.child_ids.with_context(is_write=True).write({
    #             'option_id': vals.get('option_id', record.option_id.id),
    #             'phone': vals.get('phone', record.phone),
    #             'medical_aid_id': vals.get('medical_aid_id', record.medical_aid_id.id),
    #             'plan_option_id': vals.get('plan_option_id', record.plan_option_id.id),
    #         })
    #
    #     return res

    @api.model
    def default_get(self, fields):
        rec = super(res_partner, self).default_get(fields)
        rec.update(
            country_id=self.env.ref('base.za').id
        )
        return rec

    def res_partner_company_form(self):
        return {
            'name': 'Create Contact',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_id': self.env.ref('TOMS.aspl_res_partner_company_form').id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_parent_id': self.id, 'default_company_type': 'company'}
        }

    def res_partner_child_form(self):
        return {
            'name': 'Create Contact',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_id': self.env.ref('TOMS.view_partner_dependent_contact_form').id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_parent_id': self.id,
                'default_medical_aid_id': self.medical_aid_id.id,
                'default_option_id': self.option_id.id,
                'default_plan_option_id': self.plan_option_id.id,
                'default_home_street': self.home_street,
                'default_home_street2': self.home_street2,
                'default_home_city': self.home_city,
                'default_home_zip': self.home_zip,
                'default_home_state_id': self.home_state_id.id,
                'default_home_country_id': self.home_country_id.id,
                'default_is_dependent': True,
                'default_individual_internal_ref': self.individual_internal_ref,
                'default_country_id': self.env.ref('base.za').id,
                'default_medical_aid_no': self.medical_aid_no,
            }
        }

    def res_partner_existing_dependant(self):
        return {
            'name': 'Add Dependant',
            'type': 'ir.actions.act_window',
            'res_model': 'existing.customer.add',
            'view_id': self.env.ref('TOMS.view_existing_dependant_form').id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    def save_child_contact(self):
        pass

    def res_compnay_contact(self):
        pass

    def save_medical_aid(self):
        pass

    def copy_postal_address_to_home_add(self):
        self.home_street = self.street
        self.home_street2 = self.street2
        self.home_city = self.city
        self.home_state_id = self.state_id.id
        self.home_zip = self.zip
        self.home_country_id = self.country_id.id

    @api.onchange('id_number')
    def compute_birthdate(self):
        self.birth_date = False
        if self.id_number:
            if len(self.id_number) == 13:
                if (int(self.id_number[2:4]) <= 12 and int(self.id_number[4:6]) <= 31):
                    curr_year = str(date.today().year)[2:4]
                    year = 19 if int(self.id_number[0:2]) > int(curr_year) else 20
                    birth_date = self.id_number[2:4] + '/' + self.id_number[4:6] + '/' + str(year) + self.id_number[0:2]
                    birth_date = datetime.strptime(birth_date, '%m/%d/%Y').date()
                    self.birth_date = birth_date

    @api.constrains('id_number')
    def check_duplicate_idnumber(self):
        if self.id_number:
            if len(self.id_number) == 13:
                idnumber = self.env['res.partner'].search([('id_number', '=', self.id_number), ('id', '!=', self.id)])
                if idnumber:
                    raise ValidationError(_('Duplicate ID Number Found.!!!'))

    @api.onchange('first_name', 'surname')
    def onchange_first_name(self):
        self.name = False
        name = self.first_name if self.first_name else ''
        sname = self.surname if self.surname else ''
        name = name + ' ' + sname
        self.name = name.strip()


class customer_language(models.Model):
    _name = 'customer.language'
    _description = 'Preferred Language of customer'

    name = fields.Char()


class customer_language(models.Model):
    _name = 'customer.language'
    _description = 'Preferred Language of customer'

    name = fields.Char()


class customer_occupation(models.Model):
    _name = 'customer.occupation'
    _description = 'Preferred occupation of customer'

    name = fields.Char()


class customer_source(models.Model):
    _name = 'customer.source'
    _description = 'Customer Source'

    name = fields.Char(string="Source")


class customer_funtion(models.Model):
    _name = 'customer.function'
    _description = 'Customer Function'

    name = fields.Char(string="Job Position")


class inherit_res_partner(models.Model):
    _inherit = 'res.partner'

    last_exam_date = fields.Date(string="Last Exam Date")
    recall_exam_date = fields.Date(string="Recall Date")
    exam_id = fields.Many2one('clinical.examination')

    @api.model
    def scheduler_recall_customer(self):
        customer_id = self.search([('customer_rank', '>', 0), ('recall_exam_date', '=', date.today())])
        # sms_template_id = self.env.ref('TOMS.recall_sms_template')
        # if sms_template_id:
        #     for each in customer_id:
        #         if each.mobile:
        #             sms_compose = self.env['sms.compose'].create({
        #                 'sms_template_id': sms_template_id.id,
        #                 # 'from_mobile_id': sms_template_id.from_mobile_verified_id.id,
        #                 'to_number': each.mobile,
        #                 'sms_content': sms_template_id.template_body,
        #                 'media_id': sms_template_id.media_id,
        #                 'model': self._name,
        #                 'record_id': each.id
        #             })
        #             if sms_compose:
        #                 sms_compose.with_context(from_cron=True).send_entity()


class ExistingCustomerAdd(models.TransientModel):
    _name = 'existing.customer.add'
    _description = 'Existing Customer Add'

    name = fields.Many2one('res.partner', string="Existing Dependant",
                           domain=[('is_a_medical_aid', '=', False), ('customer_rank', '>', 0)])

    def add_existing_dependant(self):
        if self.name:
            parent_id = self.env['res.partner'].browse(int(self.env.context.get('active_id')))
            self.name.parent_id = int(self.env.context.get('active_id'))
            self.name.medical_aid_id = parent_id.medical_aid_id.id
            self.name.option_id = parent_id.option_id.id
            self.name.plan_option_id = parent_id.plan_option_id.id
