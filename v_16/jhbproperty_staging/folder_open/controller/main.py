from odoo import http
from odoo.http import request
import os
import urllib.parse

class FolderOpenController(http.Controller):
    BASE_FOLDER = '/home/cybro-megha/odoo16/BRTA/'  # change to your actual path

    @http.route('/folder_open', auth='user', type='http')
    def folder_open(self, path='', **kwargs):
        # Sanitize path to avoid directory traversal
        safe_path = os.path.normpath(path).lstrip(os.sep)
        full_path = os.path.join(self.BASE_FOLDER, safe_path)

        if not os.path.exists(full_path):
            return "<h2>Folder not found</h2>"

        html = f"<h2>📂 Browsing: /{safe_path}</h2><ul style='font-size:16px;'>"

        # Add back button if not in root
        if safe_path:
            parent_path = os.path.dirname(safe_path)
            html += f"<li><a href='/folder_open?path={urllib.parse.quote(parent_path)}'>🔙 .. (Up)</a></li>"

        for entry in sorted(os.listdir(full_path)):
            entry_path = os.path.join(full_path, entry)
            rel_path = os.path.join(safe_path, entry)
            encoded_path = urllib.parse.quote(rel_path)

            if os.path.isdir(entry_path):
                html += f"<li>📁 <a href='/folder_open?path={encoded_path}'>{entry}</a></li>"
            else:
                html += f"<li>📄 <a href='/folder_open/file/{encoded_path}' target='_blank'>{entry}</a></li>"
        html += "</ul>"
        return html

    @http.route('/folder_open/file/<path:filename>', auth='user', type='http')
    def serve_file(self, filename, **kwargs):
        full_path = os.path.normpath(os.path.join(self.BASE_FOLDER, filename))
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            return request.not_found()
        return http.send_file(full_path)
