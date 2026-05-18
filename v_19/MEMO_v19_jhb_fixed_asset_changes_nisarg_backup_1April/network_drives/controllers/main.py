# controllers/main.py
from odoo import http
from odoo.http import request
import os
import io
import zipfile
import urllib.parse
import mimetypes
from odoo.http import content_disposition


class FileDownloadController(http.Controller):

    @http.route('/folder/open/', type='http', auth='user')
    def open_folder(self, path=None,  **kwargs):
        """Open the folders"""
        """in Windows"""
        # path = f'file:///{path.replace("\\", "/")}'
        # path = fr"{path}"

        if not path or not os.path.exists(path):
            return "<h3>Path not found</h3>"

        if os.path.isfile(path):
            return http.local_redirect(f"/folder/view/?path={path}")

        entries = []
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            entries.append({
                'name': entry,
                'path': full_path,
                'is_dir': os.path.isdir(full_path),
            })

        html = f"<h2>📁 Folder: {path}</h2><ul>"
        for entry in entries:
            if entry['is_dir']:
                html += f"<li>📁 <a href='/folder/open/?path={entry['path']}'>{entry['name']}</a></li>"
            else:
                html += f"<li>📄 <a href='/folder/view/?path={entry['path']}' target='_blank'>{entry['name']}</a></li>"
        html += "</ul>"

        return html

    @http.route('/folder/view/', type='http', auth='user')
    def view_file(self, path=None, **kwargs):
        """Open files"""
        """in Windows"""
        # path = f'file:///{path.replace("\\", "/")}'
        # path = fr"{path}"
        if not path or not os.path.exists(path) or not os.path.isfile(path):
            return "<h3>File not found</h3>"

        file_name = os.path.basename(path)
        mime_type, _ = mimetypes.guess_type(path)
        mime_type = mime_type or 'application/octet-stream'

        with open(path, 'rb') as f:
            file_data = f.read()

        return request.make_response(
            file_data,
            headers=[
                ('Content-Type', mime_type),
                ('Content-Disposition', f'inline; filename="{file_name}"')
            ]
        )

    @http.route('/file/download/<int:record_id>', type='http', auth='user')
    def download_file(self, record_id):
        record = request.env['network.drive.content'].browse(record_id)
        if not record.exists():
            return request.not_found()
        if record.item_type == 'File':
            if record.drive_id.os_type == 'ubuntu' and record.drive_id.is_networkdrive:
                from smbclient import open_file, register_session
                from smbprotocol.exceptions import SMBException
                from smbprotocol.connection import Connection
                from smbprotocol.session import Session
                from uuid import uuid4

                server = record.drive_id.drive_credential_id.server
                username = record.drive_id.drive_credential_id.user_name
                password = record.drive_id.drive_credential_id.password
                try:
                    register_session(server, username=username,
                                     password=password)
                    share = 'test'
                    file_path = 'SHA00619.JPG'
                    conn = Connection(uuid4(), server, 445)
                    # conn = Connection( server=server, port=445)
                    conn.connect()

                    # Create session
                    session = Session(connection=conn, username=username,
                                      password=password)
                    session.connect()

                    #smb_path = fr"\\{server}\{share}\{file_path.replace('/', '\\')}"
                    path = fr"\\{server}\{record.path}"
                    with open_file(path, mode='rb') as f:
                        file_data = f.read()
                        return request.make_response(file_data, [
                            ('Content-Type', 'application/octet-stream'),
                            ('Content-Disposition',
                             f'attachment; filename="{record.name}"')
                        ])
                except SMBException as e:
                    print(f"SMB Error: {e}")
                except Exception as e:
                    print(f"Error reading file: {e}")
                return None
            else:
                with open(record.path, 'rb') as f:
                    file_data = f.read()
                filename = os.path.basename(record.path)
                return request.make_response(file_data, [
                    ('Content-Type', 'application/octet-stream'),
                    ('Content-Disposition',
                     f'attachment; filename="{filename}"')
                ])

        elif record.item_type == 'Folder':
            if record.drive_id.os_type == 'ubuntu' and record.drive_id.is_networkdrive:
                from smbclient import register_session, listdir, open_file, path
                from io import BytesIO
                from zipfile import ZipFile
                from werkzeug.wrappers import Response

                server = "megha.local"
                share_name = "testing"
                username = "user"
                password = "1234"
                server = record.drive_id.drive_credential_id.server
                username = record.drive_id.drive_credential_id.user_name
                password = record.drive_id.drive_credential_id.password

                smb_root = fr"\\{server}/{record.path}"

                try:
                    register_session(server, username=username,
                                     password=password)
                    zip_buffer = BytesIO()
                    with ZipFile(zip_buffer, 'w') as zip_file:
                        for entry in listdir(smb_root):
                            entry_path = os.path.join(smb_root, entry)
                            if not path.isdir(
                                    entry_path):  # skip folders inside
                                with open_file(entry_path, mode='rb') as f:
                                    file_data = f.read()
                                    zip_file.writestr(entry, file_data)

                    zip_buffer.seek(0)

                    return Response(zip_buffer.read(), headers=[
                        ('Content-Type', 'application/zip'),
                        ('Content-Disposition',
                         'attachment; filename="testing_folder.zip"')]
                                    )

                except Exception as e:
                    return Response(f"Error: {str(e)}", status=500)
            else:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w',
                                     zipfile.ZIP_DEFLATED) as zip_file:
                    for root, _, files in os.walk(record.path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, record.path)
                            zip_file.write(file_path, arcname)

                zip_buffer.seek(0)
                zip_data = zip_buffer.read()
                return request.make_response(zip_data, [
                    ('Content-Type', 'application/zip'),
                    ('Content-Disposition',
                     f'attachment; filename="{record.name}.zip"')
                ])

        return request.not_found()
