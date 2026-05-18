from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
from werkzeug import urls


class Property(models.Model):
    _inherit = "building"

    jmc_number = fields.Char(
        string="JMC Number",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: ('New')
    )
    property_condition = fields.Selection([('very_good', 'Very Good'),
                                           ('good', 'Good'), ('fair', 'Fair'),
                                           ('poor', 'Poor'),
                                           ('very_poor', 'Very Poor')],
                                          string="Condition of property")
    history_amount = fields.Float(string='Amount (R)')
    township = fields.Char(string='Township')
    rental_count = fields.Integer(string="Rental Count", compute="_compute_rental_count")
    ward = fields.Char(string="Ward")
    zoning_id = fields.Many2one('property.zoning', string="Zoning")
    latitude = fields.Float("Latitude", digits=(9, 6), required=True)
    longitude = fields.Float("Longitude", digits=(9, 6), required=True)
    sg_id = fields.Char(string="SG ID")
    department_id = fields.Many2one('property.department',
                                    string="User Department")
    category_id = fields.Many2one('property.category', string="Category")
    category_amp_id = fields.Many2one('property.category.amp',
                                      string="Category AMP")
    current_use = fields.Char(string="Current Use")
    building = fields.Many2one('building', 'Building',
                               copy=False)

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submitted for Approval'),
         ('free', 'Available'),
         ('reserved', 'In-Progress'),
         ('on_lease', 'Leased'),
         ('disposed', 'Disposed'),
         ('sold', 'Sold'),
         ('blocked', 'Blocked'), ('reject', 'Rejected')
         ], 'State', default='draft')
    theoretical_amount = fields.Float(string="Theoretical Value")
    trade_count = fields.Integer(string="Trade Count",
                                 compute="_compute_trade_count")
    leased_state = fields.Selection(
        [('leased', 'Leased'), ('not_leased', 'Not Leased')],
        string="Leased Or Not")
    title_deeds_documents_ids = fields.One2many('building.attachment.line',
                                                'title_deeds_id')
    contract_documents_ids = fields.One2many('building.attachment.line',
                                             'contract_id')
    redirect_url = fields.Char(string='Redirect URL')
    building_documents_ids = fields.One2many(
        'documents.document',
        'jmc_property_id',
        string='Documents',
        copy=False
    )
    zoning_id = fields.Many2one('property.zoning', string="Zoning")


    def get_record_url(self):
        """Generate the URL for the current record"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        self.redirect_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"

    def action_submit_for_approval(self):
        """ Submit the asset for approval of Property Asset Register """
        self.get_record_url()
        self.write({'state': 'submit'})
        manager_group = self.env.ref(
            'itsys_real_estate_approval.group_property_approval_manager')
        mail_values = {}
        partners = manager_group.user_ids.mapped('partner_id')
        for partner in partners:
            if partner.email:
                mail_values = {
                    'email_to': partner.email,
                }
        template = self.env.ref(
            'property_update.email_template_to_confirm_building')
        template.send_mail(self.id, force_send=True, email_values=mail_values)
        for asset in self:
            message_body = (
                f" Asset {asset.name} has been submitted for approval.")
            manager_group = self.env.ref(
                'itsys_real_estate_approval.group_property_approval_manager')
            partner_ids = manager_group.user_ids.mapped('partner_id.id')
            asset.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=partner_ids,
            )

    def action_approve(self):
        """Method for approving the Property Asset Register"""
        for record in self:
            record.state = 'free'
            message_body = (
                f" Asset {record.name} has been approved. "
            )
            mail_values = {}
            if record.partner_id.email:
                mail_values = {
                    'email_to': record.partner_id.email,
                }
            template = self.env.ref(
                'property_update.email_template_approval_confirmed_building')
            template.send_mail(record.id, force_send=True,
                               email_values=mail_values)
            record.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[record.partner_id.id],
            )

    def action_reject(self):
        """Method for rejecting the Property Asset Register"""
        for record in self:
            record.state = 'reject'
            message_body = (
                f" Asset {record.name} has been rejected. "
            )
            mail_values = {}

            if record.partner_id.email:
                mail_values = {
                    'email_to': record.partner_id.email,
                }
            template = self.env.ref(
                'property_update.email_template_rejected_building')
            template.send_mail(record.id, force_send=True,
                               email_values=mail_values)
            record.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[record.partner_id.id],
            )

    def cron_update_rental_count(self, batch_size=1000):
        """ Cron job to update rental count for old records in batches """
        offset = 0
        while True:
            # Fetch records in batches
            buildings = self.env['building'].search([], offset=offset,
                                                    limit=batch_size)
            if not buildings:
                break  # Exit loop if no more records

            buildings.update_rent_count()  # Call compute function on batch
            self._cr.commit()  # Commit after each batch to avoid transaction lock

            offset += batch_size

    def update_rent_count(self):
        """ Compute rental count efficiently """
        RentalContract = self.env['rental.contract']
        # Fetch rental counts in bulk
        rental_data = RentalContract.read_group(
            [('jmc_number', 'in', self.mapped('jmc_number'))],
            ['jmc_number', 'building_count:count(id)'],
            ['jmc_number']
        )

        # Convert to dictionary
        rental_count_map = {data['jmc_number']: data['building_count'] for data
                            in rental_data}
        # Update records in bulk
        for rec in self:
            rental_count = rental_count_map.get(rec.jmc_number, 0)
            rec.write({
                'rental_count': rental_count,
                'leased_state': 'leased' if rental_count >= 1 else 'not_leased',
                'state': 'on_lease' if rental_count >= 1 else 'free',
            })

    @api.model
    def action_move_state_booked(self):
        """Move the state"""
        # Enquiry
        enquiry = self.env['client.enquiry'].search([('state', '!=', 'draft')])
        enquiry_property = enquiry.mapped('property_id')
        for rec in enquiry_property:
            rec.state = 'reserved'
        # Assessment
        assessment = self.env['enquiry.assessment'].search([('state', '=', 'ownership')])
        assessment_property = assessment.mapped('property_id')
        for rec in assessment_property:
            rec.state = 'reserved'
        # assessment_terminated = self.env['enquiry.assessment'].search([('state', '=', 'terminate')])
        # assessment_terminate_property = assessment_terminated.mapped('property_id')
        # for terminate in assessment_terminate_property:
        #     terminate.state = 'blocked'
        # Circulation
        circulation = self.env['circulation.comments'].search([('state', 'not in', ['draft', 'terminate'])])
        circulation_property = circulation.mapped('property_id')
        for circulation in circulation_property:
            circulation.state = 'reserved'
        # terminate_circulation = self.env['circulation.comments'].search(
        #     [('state', 'in', ['terminate'])])
        # circulation_terminate_property = terminate_circulation.mapped('property_id')
        # for circulation_terminate in circulation_terminate_property:
        #     circulation_terminate.state = 'blocked'
        # Valuation
        valuation = self.env['assessment.valuation'].search([('state', 'not in', ['draft', 'terminate'])])
        valuation_property = valuation.mapped('property_id')
        for valuation_rec in valuation_property:
            valuation_rec.state = 'reserved'
        # terminate_valuation = self.env['assessment.valuation'].search([('state', 'in', ['terminate'])])
        # valuation_terminate_property = terminate_valuation.mapped('property_id')
        # for valuation_terminate_rec in valuation_terminate_property:
        #     valuation_terminate_rec.state = 'blocked'
        # Transaction
        transaction = self.env['client.transaction'].search([('state', 'not in', ['draft', 'terminated', 'reject'])])
        transaction_property = transaction.mapped('property_id')
        for transaction_rec in transaction_property:
            transaction_rec.state = 'reserved'
        # transaction_terminate = self.env['client.transaction'].search([('state', 'in', ['terminated', 'reject'])])
        # transaction_terminate_property = transaction_terminate.mapped('property_id')
        # for transaction_terminate_rec in transaction_terminate_property:
        #     transaction_terminate_rec.state = 'blocked'
        # EAC
        eac = self.env['eac.process'].search([('state', 'not in', ['draft'])])
        eac_property = eac.mapped('property_id')
        for eac_rec in eac_property:
            eac_rec.state = 'reserved'
        # Legal
        legal = self.env['project.project'].search([('state', '!=', 'draft'), ('is_matter', '=', True)])
        legal_property = eac.mapped('property_id')
        for legal_rec in legal_property:
            legal_rec.state = 'reserved'
        # Legal
        intelligence = self.env['property.intelligence'].search([('state', 'not in', ['block', 'draft'])])
        intelligence_property = intelligence.mapped('property_id')
        for intelligence_rec in intelligence_property:
            intelligence_rec.state = 'reserved'
        # terminate_intelligence = self.env['property.intelligence'].search([('state', '=', 'block')])
        # terminate_intelligence_property = terminate_intelligence.mapped('property_id')
        # for intelligence_rec in terminate_intelligence_property:
        #     intelligence_rec.state = 'blocked'

    @api.model
    def _compute_rental_count(self):
        for re in self:
            rental = self.env['rental.contract'].search([('building', '=', re.id)])
            re.rental_attachment_document_ids = rental.attach_line.ids
        """Methode to get the rental count"""
        for rec in self:
            rental = self.env['rental.contract'].search_count(
                [('jmc_number', '=', rec.jmc_number)])
            rec.rental_count = rental
            if rental >= 1:
                rec.leased_state = 'leased'
            else:
                rec.leased_state = 'not_leased'

            if rec.leased_state == 'leased':
                rec.state = 'on_lease'
            self.action_move_state_booked()
            # else:
            #     rec.state = 'free'

    def action_archive(self):
        res = super().action_archive()
        for rec in self:
            if rec.state in ['free']:
                raise UserError(_("Can't archive this records, it is in available state"))
        return res

    # def _compute_leased_state(self):
    #     """leased state"""
    #     for rec in self:
    #         state = ""
    #         leased = self.env['rental.contract'].search(
    #             [('building', '=', rec.id)])
    #
            # if self.state == 'free' or self.state in ('draft', 'submit') or :
            #     state = "not_leased"
            # else:
            #     state = "leased"
            # rec.leased_state = state

    def get_rental_contract_details(self):
        """Method for getting rental contract details"""
        rental = self.env['rental.contract'].search(
            [('jmc_number', '=', self.jmc_number)])
        action = {
            'name': _('Budget'),
            'type': 'ir.actions.act_window',
            'res_model': 'rental.contract',
            'context': {'create': False},
        }
        if len(rental) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': rental.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', rental.ids)],
            })
        return action

    def view_trade_rental_contract(self):
        """Method for getting rental contract details"""
        rental = self.env['rental.contract'].search(
            [('building', '=', self.id), ('lease_type', '=', 'trade_lease')])
        action = {
            'name': _('Budget'),
            'type': 'ir.actions.act_window',
            'res_model': 'rental.contract',
            'context': {'create': False},
        }
        if len(rental) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': rental.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', rental.ids)],
            })
        return action

    # def _compute_rental_count(self):
    #     """Methode to get the rental count"""
    #     for rec in self:
    #         rental = self.env['rental.contract'].search_count(
    #             [('jmc_number', '=', rec.jmc_number)])
    #         rec.rental_count = rental

    def _compute_trade_count(self):
        """Methode to get the trade rental count"""
        for rec in self:
            rental = self.env['rental.contract'].search_count(
                [('building', '=', rec.id), ('lease_type', '=', 'trade_lease')])
            rec.trade_count = rental

    def action_create_assessment(self):
        """To create the assessment"""
        return {
            'type': 'ir.actions.act_window',
            'target': 'new',
            'name': _('Assessment'),
            'view_mode': 'form',
            'res_model': 'enquiry.assessment',
            'context': {
                'default_property_id': self.id
            },
        }

    def make_reservation(self):
        for unit_obj in self:
            code = unit_obj.code
            # building_unit = unit_obj.id
            address = unit_obj.address
            floor = unit_obj.floor
            pricing = unit_obj.pricing
            type = unit_obj.type.id
            status = unit_obj.status.id
            building = unit_obj.id
            building_code = unit_obj.code
            region = unit_obj.region_id.id
            building_area = unit_obj.building_area

        vals = {'region': region,
                'building_code': building_code,
                'building': building,
                'unit_code': code,
                'floor': floor,
                'pricing': pricing,
                'type': type,
                'address': address,
                'status': status,
                'building_area': building_area,
                # 'building_unit': building_unit
                }

        reservation_obj = self.env['unit.reservation']
        reservation_id = reservation_obj.create(vals)
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'unit.reservation',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': reservation_id.id,
        }

    @api.model
    def create(self, vals):
        if vals.get('jmc_number', ('New')) == ('New'):
            vals['jmc_number'] = self.env['ir.sequence'].next_by_code(
                'building.jmc_number') or ('New')
        return super(Property, self).create(vals)


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    jmc_property_id = fields.Many2one('building',
                                      string="JMC Number", tracking=True,
                                      context={'list_view_ref':'property_update.building_list'})

    def action_preview_document(self):
        self.ensure_one()
        if not self.attachment_id:
            raise ValidationError("Please first upload document")

        preview_url = f'/web/content/{self.attachment_id.id}?download=false'
        if not preview_url:
            raise ValidationError("Preview not supported for this file type.")
        return {
            'type': 'ir.actions.act_url',
            'url': preview_url,
            'target': 'new',
        }