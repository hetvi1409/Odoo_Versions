# -*- coding: utf-8 -*-

import io
import base64
import json
import zipfile
import unicodedata

from odoo import _, fields, http
from odoo.addons.mail.controllers.discuss import DiscussController
from odoo.addons.web.controllers.binary import clean
from odoo.exceptions import AccessError
from odoo.http import content_disposition, request
from odoo.tools import replace_exceptions


class cloudFiles(DiscussController):
    """
    Controller to manage attachments operations in file manager
    """
    @http.route("/cloud_base/folder", methods=["POST"], type="json", auth="user")
    def cloud_base_check_object_folder(self, thread_model, thread_id, **kwargs):
        """
        Fully re-write to pass clouds folder

        Methods:
         * _attachment_format of ir.attachment
        """
        folder_id = request.env["clouds.folder"].search_count(
            [("res_model", "=", thread_model), ("res_id", "=", thread_id)], limit=1
        )
        return folder_id and True or False

    @http.route("/cloud_base/attachments/data", methods=["POST"], type="json", auth="user")
    def cloud_base_folder_attachments(self, thread_model, thread_id, checked_folder, folder_domain, **kwargs):
        """
        Fully re-write to pass clouds folder

        Methods:
         * _attachment_format of ir.attachment
        """
        thread = request.env[thread_model].with_context(active_test=False).search([("id", "=", thread_id)])
        folder_domain = folder_domain
        if not checked_folder:
            folder_domain = [("res_id", "=", thread_id), ("res_model", "=", thread_model)]
        return request.env["ir.attachment"].search(folder_domain, order="id desc")._attachment_format()

    @http.route("/cloud_base/upload_attachment", type="http", auth="user")
    def upload_to_file_manager(self, clouds_folder_id, ufile, callback=None):
        """
        The method to create folder-related attachment based on uploaded file
        @see web/controllers/binary > upload_attachment
        """
        out = """<script language="javascript" type="text/javascript">
            var win = window.top.window;
            win.jQuery(win).trigger(%s, %s);
        </script>"""
        args = []
        if not clouds_folder_id or clouds_folder_id == "false":
            args.append({"error": _("Please select a folder for uploaded files")})
        else:
            files = request.httprequest.files.getlist("ufile")
            Model = request.env["ir.attachment"]
            for ufile in files:
                filename = ufile.filename
                if request.httprequest.user_agent.browser == "safari":
                    filename = unicodedata.normalize("NFD", ufile.filename)
                try:
                    attachment = Model.create({
                        "name": filename,
                        "datas": base64.encodebytes(ufile.read()),
                        "clouds_folder_id": clouds_folder_id,
                    })
                    attachment._post_add_create()
                except AccessError:
                    args.append({"error": _("You are not allowed to upload an attachment here.")})
                except Exception:
                    args.append({"error": _("Something horrible happened")})
                else:
                    args.append({
                        "filename": clean(filename),
                        "mimetype": ufile.content_type,
                        "id": attachment.id,
                        "size": attachment.file_size
                    })
        return out % (json.dumps(clean(callback)), json.dumps(args)) if callback else json.dumps(args)

    @http.route(["/cloud_base/multiupload/<string:attachments>"], type="http", auth="user")
    def multi_download_file_manager(self, attachments, **kwargs):
        """
        The method to download multiple files as a zip archive

        Methods:
         * _get_stream_from of ir.binary
        """
        attachment_ids = request.env["ir.attachment"]
        if attachments:
            attachment_ids = attachments.split(",")
            attachment_ids = request.env["ir.attachment"].browse([int(art) for art in attachment_ids]).exists()
        stream = io.BytesIO()
        try:
            with zipfile.ZipFile(stream, "w") as zip_archive:
                for attachment_id in attachment_ids:
                    if attachment_id.type == "binary" or (attachment_id.type == "url" and attachment_id.cloud_key):
                        binary_stream = request.env["ir.binary"]._get_stream_from(attachment_id, "raw")
                        zip_archive.writestr(
                            binary_stream.download_name,
                            binary_stream.read(),
                            compress_type=zipfile.ZIP_DEFLATED
                        )
        except zipfile.BadZipfile:
            pass
        content = stream.getvalue()
        archive_title = kwargs.get("archive_name") or "{}".format(fields.Datetime.now())
        headers = [
            ("Content-Type", "zip"),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Length", len(content)),
            ("Content-Disposition", content_disposition("odoo_{}.zip".format(archive_title)))
        ]
        return request.make_response(content, headers)

    @http.route(["/cloud_base/folder_upload/<model('clouds.folder'):folder_id>"], type="http", auth="user")
    def folder_download_file_manager(self, folder_id, **kwargs):
        """
        The method to prepare cloud folder attachments for downloading

        Methods:
         * multi_download_file_manager
        """
        attachment_ids = request.env["ir.attachment"].search([("clouds_folder_id", "=", folder_id.id)]).ids
        att_param = ",".join(str(at) for at in attachment_ids)
        return self.multi_download_file_manager(att_param, archive_name=folder_id.name)

    @http.route(["/cloud_base/export_logs"], type="http", auth="user")
    def cloud_base_export_logs(self, search_name, selected_clients, log_levels):
        """
        The method to prepare txt files with logs

        Methods:
         * _prepare_txt_logs
        """
        content = request.env["clouds.log"]._prepare_txt_logs(
            search_name, json.loads(selected_clients), json.loads(log_levels)
        ).encode("utf-8")
        headers = [
            ("Content-Type", "zip"),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Length", len(content)),
            ("Content-Disposition", content_disposition("cloud_base_{}.logs".format(fields.Datetime.now())))
        ]
        return request.make_response(content, headers)
