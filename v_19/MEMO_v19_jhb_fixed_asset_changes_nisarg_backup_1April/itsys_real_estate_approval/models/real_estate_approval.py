# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from email.policy import default

from odoo import api, fields, models
import datetime
from odoo.tools.translate import _
import calendar
from odoo.exceptions import UserError, AccessError
from datetime import time, datetime, date, timedelta


class BuildingApproval(models.Model):
    _name = "building.approval"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', size=16)
    region_id = fields.Many2one('regions', 'Region', )
    partner_id = fields.Many2one('res.partner', 'Owner',required=True)
    purchase_date = fields.Date('Purchase Date')
    launch_date = fields.Date(string="Launch Date")
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    company_id = fields.Many2one('res.company', string="Company", groups="base.group_multi_company")
    active = fields.Boolean('Active',
                            help="If the active field is set to False, it will allow you to hide the top without removing it.",
                            default=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('send', 'Send for Approval'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    redirect_url = fields.Char(compute="_compute_redirect_url",store=True)
    latitude = fields.Float("Latitude", digits=(9, 6), required=True)
    longitude = fields.Float("Longitude", digits=(9, 6), required=True)
    asset_id = fields.Many2one('building')
    document_id = fields.Binary(string="Approval Document",required=True)


    @api.depends('state')
    def _compute_redirect_url(self):
        for record in self:
            if record.state != 'approved':
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                base_url += '/web#id=%d&view_type=list&model=%s' % (record.id, 'building.approval')
                record.redirect_url = base_url
            else:
                asset_id = self.env['building'].search([('approval_request_id','=',record.id)])
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                base_url += '/web#id=%d&view_type=list&model=%s' % (asset_id.id, 'building')
                record.redirect_url = base_url



    def action_approve(self):
        for record in self:
            record.state = 'approved'
            message_body = (
                f" Asset {record.name} has been approved. "
            )
            mail_values = {}

            if record.partner_id.email:  # Ensure the partner has an email address
                mail_values = {
                    'email_to': record.partner_id.email,
                    # Other values can be set as needed
                }
            # Send to all followers and specifically to the Impairment Manager group
            vals = {
                'name': record.name,
                'code':record.code,
                'region_id':record.region_id.id if record.region_id else False,
                'partner_id':record.partner_id.id if record.partner_id else False,
                'purchase_date':record.purchase_date,
                'launch_date':record.launch_date,
                'account_analytic_id':record.account_analytic_id.id if record.account_analytic_id else False,
                'company_id':record.company_id.id if record.company_id else False,
                'latitude': record.latitude,
                'longitude': record.longitude,
                'approval_request_id':record.id

            }

            property_id = self.env['building'].create(vals)

            record.asset_id = property_id.id

            template = self.env.ref('itsys_real_estate_approval.email_template_approval_confirmed')
            template.send_mail(record.id, force_send=True, email_values=mail_values)

            record.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[record.partner_id.id],
            )



    def action_reject(self):
            for record in self:
                record.state = 'reject'
                message_body = (
                    f" Asset {record.name} has been rejected. "
                )
                mail_values = {}

                if record.partner_id.email:  # Ensure the partner has an email address
                    mail_values = {
                        'email_to': record.partner_id.email,
                        # Other values can be set as needed
                    }
                # Send to all followers and specifically to the Impairment Manager group
                template = self.env.ref('itsys_real_estate_approval.email_template_rejected')
                template.send_mail(record.id, force_send=True, email_values=mail_values)

                record.message_post(
                    body=message_body,
                    message_type='email',
                    subtype_xmlid='mail.mt_comment',
                    partner_ids=[record.partner_id.id],
                )

    def action_submit_for_approval(self):
            """ Submit the asset for approval """
            self.write({'state': 'send'})
            manager_group = self.env.ref('itsys_real_estate_approval.group_property_approval_manager')

            # Get partner objects
            mail_values = {}

            partners = manager_group.user_ids.mapped('partner_id')

            for partner in partners:
                if partner.email:  # Ensure the partner has an email address
                    mail_values = {
                        'email_to': partner.email,
                        # Other values can be set as needed
                    }
            template = self.env.ref('itsys_real_estate_approval.email_template_to_confirm')
            template.send_mail(self.id, force_send=True, email_values=mail_values)

            # Send an in-app notification
            for asset in self:
                message_body = (
                    f" Asset {asset.name} has been submitted for approval. "
                )
                # Send to all followers and specifically to the Impairment Manager group
                manager_group = self.env.ref('itsys_real_estate_approval.group_property_approval_manager')

                partner_ids = manager_group.user_ids.mapped('partner_id.id')

                asset.message_post(
                    body=message_body,
                    message_type='email',
                    subtype_xmlid='mail.mt_comment',
                    partner_ids=partner_ids,
                )

    def action_view_building(self):
        """Opens the related building form view."""
        self.ensure_one()  # Ensure the record exists
        if self.asset_id:  # Check if the building exists
            return {
                'type': 'ir.actions.act_window',
                'name': 'Building',
                'res_model': 'building',
                'view_mode': 'form',
                'res_id': self.asset_id.id,  # Open the specific building
                'target': 'current',  # Open in the current window
            }


class Building(models.Model):
    _inherit = "building"

    approval_request_id = fields.Many2one('building.approval')
    latitude = fields.Float("Latitude", digits=(9, 6), required=False)
    longitude = fields.Float("Longitude", digits=(9, 6), required=False)
    state = fields.Selection([('free', 'Available'),
                              ('reserved', 'Booked'),
                              ('on_lease', 'Leased'),
                              ('sold', 'Sold'),
                              ('blocked', 'Blocked'),
                            ('disposed', 'Disposed'),
                              ], 'State', default='free')

    def action_remove_asset(self):
        """Opens the Building Removal Approval form view"""
        self.ensure_one()
        record_id = self.env['building.removal.approval'].search([('building_id','=',self.id)])
        if record_id:
            property_condition_label = dict(self._fields['property_condition'].selection).get(self.property_condition)

            record_id.write({
                'notes': property_condition_label
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Remove Building',
                'res_model': 'building.removal.approval',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id':record_id.id,
                'target': 'current',  # Opens in a new window
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Remove Building',
                'res_model': 'building.removal.approval',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'default_building_id': self.id,
                    # 'default_notes': dict(self._fields['property_condition'].selection).get(self.property_condition)# Pre-fill the building in the removal approval form
                },
                'target': 'current',  # Opens in a new window
            }



class BuildingRemovalApproval(models.Model):
    _name = "building.removal.approval"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'building_id'

    removal_date = fields.Date('Removal Request Date', required=True,default=lambda self: fields.Date.context_today(self))
    removal_reason = fields.Text('Reason for Removal', required=True)
    building_id = fields.Many2one('building', 'Building', required=True)
    company_id = fields.Many2one('res.company', string="Company", groups="base.group_multi_company")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('send', 'Sent for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', required=True, readonly=True, tracking=True, default='draft')

    redirect_url = fields.Char(compute="_compute_redirect_url", store=True)
    notes = fields.Html()
    user_id = fields.Many2one('res.users',default=lambda self: self.env.user)
    document_id = fields.Binary(string="Council Approval",required=True)
    selling_input = fields.Float(string='Sell Value')

    attachment_id = fields.Binary(string="Sale Agreement",required=True)
    disposal_method = fields.Selection([
        ('sale', 'Sale'),
        ('donation', 'Donation'),
    ], string='Disposal Method', required=True)


    @api.depends('state')
    def _compute_redirect_url(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            if record.state != 'approved':
                base_url += '/web#id=%d&view_type=list&model=%s' % (record.id, 'building.removal.approval')
            else:
                base_url += '/web#id=%d&view_type=list&model=%s' % (record.building_id.id, 'building')
            record.redirect_url = base_url

    def action_submit_for_approval(self):
        """ Submit the removal request for approval """
        self.write({'state': 'send'})
        manager_group = self.env.ref('itsys_real_estate_approval.group_property_approval_manager')

        mail_values = {}
        partners = manager_group.user_ids.mapped('partner_id')

        for partner in partners:
            if partner.email:
                mail_values = {'email_to': partner.email}

        template = self.env.ref('itsys_real_estate_approval.email_template_removal_to_confirm')
        template.send_mail(self.id, force_send=True, email_values=mail_values)

        for removal in self:
            message_body = f"Removal request for building {removal.building_id.name} has been submitted for approval."
            partner_ids = manager_group.user_ids.mapped('partner_id.id')
            removal.message_post(body=message_body, message_type='email', subtype_xmlid='mail.mt_comment',
                                 partner_ids=partner_ids)

    def action_approve(self):
        """ Approve the removal request """
        for record in self:
            record.state = 'approved'
            record.building_id.active = False  # Mark the building as inactive (removed)

            record.building_id.state = 'disposed'
            message_body = f"Building {record.building_id.name} has been approved for removal."
            mail_values = {}
            if record.user_id.partner_id.email:
                mail_values = {'email_to': record.user_id.partner_id.email}

            template = self.env.ref('itsys_real_estate_approval.email_template_removal_approved')
            template.send_mail(record.id, force_send=True, email_values=mail_values)

            record.message_post(body=message_body, message_type='email', subtype_xmlid='mail.mt_comment',
                                partner_ids=[record.user_id.partner_id.id])

    def action_reject(self):
        """ Reject the removal request """
        for record in self:
            record.state = 'rejected'

            message_body = f"Removal request for building {record.building_id.name} has been rejected."
            mail_values = {}
            if record.user_id.partner_id.email:
                mail_values = {'email_to': record.user_id.partner_id.email}

            template = self.env.ref('itsys_real_estate_approval.email_template_removal_rejected')
            template.send_mail(record.id, force_send=True, email_values=mail_values)

            record.message_post(body=message_body, message_type='email', subtype_xmlid='mail.mt_comment',
                                partner_ids=[record.user_id.partner_id.id])
