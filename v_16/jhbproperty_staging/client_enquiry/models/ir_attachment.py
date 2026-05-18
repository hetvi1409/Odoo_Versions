from odoo import api, models, _
from odoo.exceptions import UserError


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def create(self, values):
        """Create a new attachment in enquiry module"""
        res = super().create(values)
        if res.res_model == 'client.enquiry':
            enquiry = self.env['client.enquiry'].browse(res.res_id)
            # if enquiry.team_id.id == self.env.ref('client_enquiry.helpdesk_team_manual').id:
            #     folder = self.env.ref('client_enquiry.document_enquiry_walk_in')
            # if enquiry.team_id.id == self.env.ref('client_enquiry.helpdesk_team_telephone').id:
            #     folder = self.env.ref('client_enquiry.document_enquiry_telephone')
            # if enquiry.team_id.id == self.env.ref('client_enquiry.helpdesk_team_email').id:
            #     folder = self.env.ref('client_enquiry.document_enquiry_email')
            # if enquiry.team_id.id == self.env.ref('client_enquiry.helpdesk_team_website').id:
            #     folder = self.env.ref('client_enquiry.document_enquiry_website')
            # if enquiry.team_id.id == self.env.ref('client_enquiry.document_enquiry_website').id:
            #     folder = self.env.ref('client_enquiry.document_enquiry_walk_in')
            # if enquiry.team_id.id == self.env.ref('client_enquiry.helpdesk_team_whatsapp').id:
            #     folder = self.env.ref('client_enquiry.document_enquiry_whatsApp')
            # jmc_folder = self.env['documents.folder'].sudo().search([
            #     ('name', '=', enquiry.asset_number),
            #     ('parent_folder_id', '=', folder.id)
            # ])
            # if not jmc_folder:
            #     jmc_folder = self.env['documents.folder'].sudo().create({
            #         'name': enquiry.asset_number,
            #         'parent_folder_id': folder.id
            #     })
            # enquiry_folder = self.env['documents.folder'].sudo().search([
            #     ('name', '=', enquiry.name),
            #     ('parent_folder_id', '=', jmc_folder.id)
            # ])
            # if not enquiry_folder:
            #     enquiry_folder = self.env['documents.folder'].sudo().create({
            #         'name': enquiry.name,
            #         'parent_folder_id': jmc_folder.id
            #     })
            # enquiry.enquiry_folder_id = enquiry_folder.id
            # document = self.env['documents.document'].sudo().create({
            #     'name': res.name,
            #     'attachment_id': res.id,
            #     'folder_id': enquiry_folder.id
            # })
        return res

