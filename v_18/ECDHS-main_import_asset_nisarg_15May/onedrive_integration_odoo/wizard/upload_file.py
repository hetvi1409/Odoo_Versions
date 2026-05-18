# -*- coding: utf-8 -*-
###############################################################################
#
#   Cybrosys Technologies Pvt. Ltd.
#
#   Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#   Author: Jumana Haseen ( odoo@cybrosys.com )
#
#   You can modify it under the terms of the GNU AFFERO
#   GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#   You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#   (AGPL v3) along with this program.
#   If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import requests
from odoo import exceptions, fields, models, _


class UploadFile(models.TransientModel):
    """
    For opening wizard view
    """
    _name = "upload.file"
    _description = "Upload File"

    file = fields.Binary(string="Attachment", help="Select a file to upload")
    file_name = fields.Char(string="File Name", help="Name of the attachment")

    def action_upload_file(self):
        """
        Upload file to onedrive
        """
        if not self.file:
            raise exceptions.UserError(_('Please Attach a file to upload.'))
        attachment = self.env["ir.attachment"].search(
            ['|', ('res_field', '!=', False), ('res_field', '=', False),
             ('res_id', '=', self.id),
             ('res_model', '=', 'upload.file')])
        token = self.env['onedrive.dashboard'].search([], order='id desc',
                                                      limit=1)
        folder = self.env['ir.config_parameter'].get_param(
            'onedrive_integration_odoo.folder_id', '')
        if not token or not folder:
            raise exceptions.UserError(
                _('Please setup Access Token and Folder Id.'))
        if token.token_expiry_date <= str(fields.Datetime.now()):
            token.generate_onedrive_refresh_token()
        try:
            # Step 1: Create upload session
            url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder}:/{self.file_name}:/createUploadSession"
            session_response = requests.post(url, headers={
                'Authorization': f'Bearer {token.onedrive_access_token}',
                'Content-Type': 'application/json'
            })
            upload_session = session_response.json()
            if 'uploadUrl' not in upload_session:
                raise exceptions.UserError(
                    "Failed to create upload session. Please check your OneDrive configuration.")
            upload_url = upload_session['uploadUrl']
            with open(attachment._full_path(attachment.store_fname),
                      'rb') as file:
                file_content = file.read()
            file_size = len(file_content)
            headers = {
                'Content-Range': f'bytes 0-{file_size - 1}/{file_size}',
                'Content-Length': str(file_size),
                'Content-Type': 'application/octet-stream'
            }
            response = requests.put(upload_url, headers=headers,
                                    data=file_content)
            if response.status_code in (200, 201):
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'message': 'File has been uploaded successfully. Please refresh.',
                        'next': {'type': 'ir.actions.act_window_close'},
                    }
                }
            else:
                error_message = response.json().get('error', {}).get('message',
                                                                     'Unknown error')
                raise exceptions.UserError(
                    f"Failed to upload file: {error_message}")
        except Exception as error:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': f'Failed to upload: {error}',
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
