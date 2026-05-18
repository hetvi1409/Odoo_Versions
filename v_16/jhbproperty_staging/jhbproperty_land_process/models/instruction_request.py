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
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from werkzeug import urls
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class instruction_request(models.Model):
    _name = "instruction.request"
    _description = "Instruction/Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char ('Name', required=True, copy=False, readonly=True, default='New')
    property_id = fields.Many2one('building', string="Property", required=True)
    instruction_type = fields.Selection([('social_lease', 'Social Lease/ Sale'),
                             ('commercial_lease',
                              'Commercial Lease/Sale (including residential)'),
                             ('registration',
                              'Registration/ cancellation of a servitude'),
                             ('land', 'Land Regularisation Matter'),
                             ('road', 'Road reserve'),
                             ('user_agreement', 'User Agreement'),
                             ('ptob', 'PTOB'),
                             ('lanes', 'Sanatory Lanes'),
                             ('outdoor', 'Outdoor Advertising')],
                            string='Type of enquiry',required=1)
    property_category = fields.Selection([('commercial', 'Commercial'),
                                          ('industrial', 'Industrial'),
                                          ('residential', 'Residential'),
                                          ('retail', 'Retail/Shop'),
                                          ('vacant', 'Vacant Land')],
                                         string="Property Category")
    property_number = fields.Char(string="Property Number")
    jmc_number = fields.Char(string="JMC Number", help="JMC number")
    instruction_description = fields.Text(string="Instruction Description")
    property_address = fields.Char(string="Address", help="Property Address")
    instruction_notes = fields.Html("Notes", help="Additional notes or comments about the instruction request.")
    instruction_request_documents_ids = fields.One2many(
        'documents.document',
        'instruction_request_id',
        string='Documents',
        copy=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            # Use the next sequence or fallback to the id after creation
            vals['name'] = self.env['ir.sequence'].next_by_code('instruction.request') or '/'
        record = super(instruction_request, self).create(vals)
        return record

    @api.onchange('property_id')
    def onchange_property(self):
        """Onchange property Details and update jmc_property_id on related documents"""
        self.property_number = self.property_id.code
        self.property_address = self.property_id.address
        self.jmc_number = self.property_id.jmc_number
        # Update jmc_property_id for all related documents
        for doc in self.instruction_request_documents_ids:
            doc.jmc_property_id = self.property_id.id


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    instruction_request_id = fields.Many2one(
        comodel_name='instruction.request',
        string="Instruction Request",
        tracking=True,
        context="{'default_instruction_request_id': instruction_request_id}"
    )

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
