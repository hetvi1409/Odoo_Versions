# -*- coding: utf-8 -*-
# #############################################################################
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

#############################################################################

from odoo.exceptions import ValidationError
from odoo import api, fields, models, tools, _

class Building(models.Model):
    _inherit = "building"

    trim_documents_ids = fields.One2many('trim.documents', 'building_id', string='Trim Documents')

    # This can be a computed field or method if you need to aggregate or filter the related trim documents
    def get_active_trim_documents(self):
        for record in self:
            # This will return all active trim documents related to this building
            return record.trim_documents_ids.filtered(lambda doc: doc.active)

class TrimDocument(models.Model):
    _name = 'trim.documents'
    _description = 'Trim Documents'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active', default=True)
    trim_documentid = fields.Char(string='TrimDocumentID')
    trim_doc_link = fields.Html(string='Trim Doc Link', readonly=True)
    trim_document_file = fields.Binary(string='Trim Document File', attachment=True)
    notes = fields.Text(string='Notes')
    building_id = fields.Many2one('building', string='JMC Number', readonly=True)

    ## This could be a computed field or a function if needed for further processing:
    @api.depends('name')
    def _compute_trim_document_summary(self):
        for record in self:
            record.name = f"Trim Document: {record.name}"

    ## Archive method
    def archive_document(self):
        self.active = False