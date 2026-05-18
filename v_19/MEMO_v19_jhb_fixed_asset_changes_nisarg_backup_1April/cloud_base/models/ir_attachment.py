# python
# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

FORBIDDENSYMBOLS = ['~', '#', '&', ':', '{', '}', '*', '?', '"', "'", '<', '>', '|', '+', '%', '!', '@', '\\', '/']
SPECIAL_MIMETYPES = [
    "application/vnd.google-apps.spreadsheet", "application/vnd.google-apps.document",
    "application/vnd.google-apps.presentation",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
]
FOLDER_MIMETYPES = ["application/vnd.google-apps.folder", "dir"]
NOT_SYNCED_MIMETYPES = ["text/html", "text/css", "text/javascript", "application/javascript", "text/xml",
    "application/xml"]
MAX_NAME_LEN = 180

def check_allowed_mimetypes(mimetype):
    """
    This mimetype is required only for "special" mimetypes. Standard ones are defined by Odoo
    """
    available_mimetypes = SPECIAL_MIMETYPES + FOLDER_MIMETYPES
    if not mimetype or mimetype not in (SPECIAL_MIMETYPES + FOLDER_MIMETYPES):
        mimetype = False
    elif mimetype in FOLDER_MIMETYPES:
        mimetype = "special_cloud_folder"
    return mimetype

class ir_attachment(models.Model):
    """
    Overwriting to prepare method for cloud api methods.
    Note: do NOT add a field named `active` on ir.attachment (core asserts active-name not supported).
    Use `is_active` instead to avoid the base assertion.
    """
    _inherit = "ir.attachment"

    @api.depends("store_fname", "db_datas")
    def _compute_raw(self):
        """
        Fully re-write core function to pass cloud_key to file-read
        """
        for attach in self:
            if attach.type == "url" and attach.cloud_key:
                try:
                    attach.raw = self._file_read(attach.store_fname, attach)
                except Exception:
                    attach.raw = False
            elif attach.store_fname:
                attach.raw = attach._file_read(attach.store_fname)
            else:
                attach.raw = attach.db_datas

    def _inverse_datas(self):
        """
        Overwrite to avoid writing on cloud datas into Odoo
        """
        for attach in self:
            if not attach.cloud_key:
                super(ir_attachment, attach)._inverse_datas()

    def _inverse_raw(self):
        """
        Overwrite to avoid writing on cloud datas into Odoo
        """
        for attach in self:
            if not attach.cloud_key:
                super(ir_attachment, attach)._inverse_raw()

    for_delete = fields.Boolean(default=False, string="Marked for delete")
    is_active = fields.Boolean(string="Active", default=True)  # renamed to avoid core assertion
    clouds_folder_id = fields.Many2one(
        "clouds.folder",
        string="Folder",
        index=True,
        ondelete="set null",
    )
    sync_cloud_folder_id = fields.Many2one("clouds.folder", string="Folder used for sync")
    sync_client_id = fields.Many2one("clouds.client", string="Client used for sync")
    cloud_key = fields.Char(string="Cloud key", copy=False)
    cloud_tag_ids = fields.Many2many(
        "clouds.tag",
        "clouds_tag_ir_attachment_rel_table",
        "tag_id",
        "ir_attachment_id",
        string="Tags",
    )
    # introduced for inheritance purposes to filter not-syncing attachments
    handler = fields.Char(string="Handler")
    url = fields.Char(size=4096)  # with very long names, sync URL might be also very long

    ####################################################################################################################
    ##################################   CORE methods   ################################################################
    ####################################################################################################################
    @api.model
    def check(self, mode, values=None):
        """
        Re-write to pass context for clouds.folder reference
        """
        super(ir_attachment, self.with_context(ir_attachment_security=True)).check(mode=mode, values=values)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Re-write to make sure that if an attachment has a linked record it would immediately linked to its folder
        """
        for values in vals_list:
            if values.get("clouds_folder_id"):
                values.update(self._get_res_params_by_folder(values.get("clouds_folder_id")))
            else:
                values.update(self._get_folder_by_res_params(values.get("res_model"), values.get("res_id")))
        return super(ir_attachment, self).create(vals_list)

    def write(self, vals):
        """
        Re-write to change attachment values if folder is changed

        Fixed context lookup: use self.env.context.get(...)
        """
        folder_id = False
        if not self.env.context.get("no_folder_update") and vals.get("clouds_folder_id") is not None:
            if vals.get("clouds_folder_id"):
                update_vals = self._get_res_params_by_folder(vals.get("clouds_folder_id"), True)
                vals.update(update_vals)
            else:
                # 1
                vals.update({"res_model": False, "res_id": 0})
        return super(ir_attachment, self).write(vals)

    def unlink(self):
        """
        Overwrite unlink to guarantee that a synced attachment would be deleted only after deletion is done per client.
        Synced attachments are deleted as 2 steps-process:
         1. mark for delete
         2. during the next unlink - delete an item
        """
        if not self:
            return True
        self.check("unlink")
        for_delete = self.filtered(lambda at: at.for_delete or not at.cloud_key)
        mark_for_delete = self - for_delete
        # use is_active instead of active
        mark_for_delete.write({"for_delete": True, "is_active": False})
        result = super(ir_attachment, for_delete).unlink()
        return result

    def _file_delete_special(self, fname):
        """
        The special method to remove file, since store_fname is not any more writeable
        """
        self._file_delete(fname)
        query = "UPDATE ir_attachment SET store_fname = NULL WHERE id = %s"
        self._cr.execute(query, (self.id,))
        self._cr.commit()

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None,active_test=True, bypass_access=False):
        """
        Ensure extra keyword arguments (e.g. active_test) are accepted and forwarded.
        Also force the security context used for attachment lookups.
        """
        self = self.with_context(ir_attachment_security=True)
        return super(ir_attachment, self)._search(domain, offset=offset, limit=limit, order=order,active_test=active_test, bypass_access=bypass_access)

    def copy(self, default=None):
        """
        Overwrite to make proper copy when synced or deleted
        """
        self.check("write")
        default = default or {}
        default.update({"for_delete": False, "cloud_key": False})
        if (default.get("res_model") or default.get("res_id")) and not default.get("clouds_folder_id"):
            default.update({"clouds_folder_id": False})
        return super(ir_attachment, self).copy(default)

    @api.model
    def _file_read(self, fname, attach_cloud_id=False):
        """
        Rewrite to read files from Cloud client
        """
        if not attach_cloud_id:
            r = super(ir_attachment, self)._file_read(fname=fname)
        else:
            r = attach_cloud_id.sudo()._upload_attachment_from_cloud()
            if not r:
                raise ValidationError(_("Unexpected error: binary content cannot be retrieved from clouds"))
        return r

    def action_retrieve_url(self):
        """
        Return topical URL for the attachment.
        """
        return self.sync_client_id and self.cloud_key \
            and self.sync_client_id._retrieve_url(self) or self.url or False

    def action_retrieve_url_window(self):
        """
        Returns the window action for opening the URL.
        """
        return {
            "name": "{}".format(self.name),
            "type": "ir.actions.act_url",
            "url": self.action_retrieve_url(),
        }

    def _attachment_format(self, legacy=False):
        """
        Re-write to pass cloud parameters
        """
        res_list = super(ir_attachment, self)._attachment_format(legacy=legacy)
        for res_dict in res_list:
            attachment_id = self.env["ir.attachment"].browse(res_dict.get("id"))
            res_dict.update({
                "cloudSynced": bool(attachment_id.cloud_key),
                "cloudDownloadable": attachment_id.mimetype != "application/octet-stream",
                "cloudURL": attachment_id.url or False,
                "forDelete": attachment_id.for_delete,
            })
        return res_list

    def action_return_all_pages_ids(self, domain):
        """
        The method to search attachments by js domain
        """
        all_attachments = set(self.ids + self.search(domain).ids)
        return list(all_attachments)

    def _upload_attachment_from_cloud(self):
        """
        Method to upload attachment from cloud
        """
        ctx = self._context.copy()
        cfolder = self.sync_cloud_folder_id or self.clouds_folder_id
        cclient = cfolder.client_id
        if "cclients" not in ctx.keys():
            new_ctx = cclient.sudo()._return_specific_client_context()
            ctx.update(new_ctx)
        self = self.with_context(ctx)
        cfolder = self.sync_cloud_folder_id or self.clouds_folder_id
        cclient = cfolder.client_id
        return cclient._upload_attachment_from_cloud(cfolder, self, self.cloud_key, {})

    def _get_res_params_by_folder(self, cloud_folder_id, from_write=False):
        """
        The method to calculate res_model and res_param by updated folder
        """
        updated_values = {}
        real_folder_id = isinstance(cloud_folder_id, int) and cloud_folder_id or int(cloud_folder_id)
        folder_id = self.sudo().env["clouds.folder"].browse(real_folder_id).exists()
        if folder_id:
            if not folder_id.res_id:
                updated_values.update({"res_model": "clouds.folder", "res_id": folder_id.id})
            else:
                if folder_id.res_model == "documents.document":
                    pass
                else:
                    updated_values.update({"res_model": folder_id.res_model, "res_id": folder_id.res_id})
        elif from_write:
            updated_values.update({"res_model": False, "res_id": 0})
        return updated_values

    def _get_folder_by_res_params(self, res_model, res_id):
        """
        The method to find a folder for updated attachment.
        """
        updated_values = {}
        if res_model and res_id:
            res_domain = [("res_id", "=", res_id), ("res_model", "=", res_model)]
            folder_id = self.sudo().with_context(active_test=False).env["clouds.folder"].search(res_domain, limit=1)
            if folder_id:
                updated_values = {"clouds_folder_id": folder_id.id}
        return updated_values

    ####################################################################################################################
    ##################################   SYNC-related helpers ##########################################################
    ####################################################################################################################
    def _filter_non_synced_attachments(self):
        """
        The method to filter system attachments
        """
        mime_types = NOT_SYNCED_MIMETYPES
        mime_types_conf = self.env["ir.config_parameter"].sudo().get_param("cloud_base.notsynced_mimetypes", "")
        if mime_types_conf:
            mime_types += mime_types_conf.split(",")
        attachments = self
        for attachment in self:
            if attachment.handler or attachment.mimetype in mime_types  \
                    or (attachment.type == "url" and not attachment.cloud_key) \
                    or attachment.name.startswith("/") or (attachment.url and attachment.url.startswith("/")) \
                    or attachment.res_field:
                attachments -= attachment
        return attachments

    @api.model
    def _remove_illegal_characters(self, s, safe_name="NOT CORRECT NAME", check_extension=False):
        """
        Replace not safe file system characters and trim long names.
        """
        def find_index_dot(s_list):
            start = 0
            for symbol in s_list:
                if symbol in [".", " "]:
                    start += 1
                else:
                    break
            return start
        s = s or safe_name
        for symbol in FORBIDDENSYMBOLS:
            s = s.replace(symbol, "-")
        start = find_index_dot(s)
        end = find_index_dot(reversed(s))
        if start:
            s = s[start:]
        if end:
            s = s[:-end]
        if len(s) > MAX_NAME_LEN:
            if not check_extension:
                s = s[:MAX_NAME_LEN]
            else:
                last_dot = s.rfind(".")
                if last_dot == -1 or (len(s)-last_dot > 50):
                    s = s[:MAX_NAME_LEN]
                else:
                    s1 = s[:last_dot]
                    s2 = s[last_dot:]
                    s1 = s1[:MAX_NAME_LEN-len(s2)]
                    s = s1 + s2
        else:
            s = s or safe_name
        return s
