# -*- coding: utf-8 -*-
import requests
import json
import base64
import hashlib
import os
import logging
import time
import re
import urllib3
from requests.adapters import HTTPAdapter
from datetime import datetime, timedelta
from markupsafe import Markup
from odoo import models, api, fields, _
from msal import ConfidentialClientApplication
from odoo.exceptions import ValidationError, AccessError, UserError

_logger = logging.getLogger(__name__)


# =========================================================
# MAIN SERVICE (Keep your auth logic here)
# =========================================================
class SharePointService(models.Model):
    _name = "sharepoint.service"
    _description = "SharePoint Service"

    def get_authorization_url(self):
        """Generate the Microsoft OAuth2 authorization URL with PKCE."""
        params = self.env["ir.config_parameter"].sudo()

        client_id = params.get_param("sharepoint.client_id")
        tenant_id = params.get_param("sharepoint.tenant_id")
        base_url = params.get_param("web.base.url")

        redirect_uri = f"{base_url}/sharepoint/auth/callback"

        # Generate PKCE challenge
        code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8").rstrip("=")
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode("utf-8")).digest()
        ).decode("utf-8").rstrip("=")

        # Store `code_verifier` in Odoo for later use
        params.set_param("sharepoint.code_verifier", code_verifier)

        authorization_url = (
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?"
            f"client_id={client_id}&response_type=code&redirect_uri={redirect_uri}"
            f"&response_mode=query&scope=https://graph.microsoft.com/.default offline_access"
            f"&code_challenge={code_challenge}&code_challenge_method=S256"
        )

        _logger.info(f"Generated Authorization URL: {authorization_url}")
        return authorization_url

    def get_access_token(self, auth_code=None):
        """Retrieve access token using auth code or refresh token, with PKCE support."""
        params = self.env["ir.config_parameter"].sudo()

        client_id = params.get_param("sharepoint.client_id")
        client_secret = params.get_param("sharepoint.client_secret")  # Optional (not needed if using PKCE)
        tenant_id = params.get_param("sharepoint.tenant_id")
        base_url = params.get_param("web.base.url")

        redirect_uri = f"{base_url}/sharepoint/auth/callback"
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

        # Step 1: Check if a valid token exists
        access_token = params.get_param("sharepoint.access_token")
        expiry_time = params.get_param("sharepoint.token_expiry")

        if access_token and expiry_time:
            expiry_time = int(expiry_time)
            current_time = int(time.time())
            if expiry_time > current_time:
                _logger.info("Using valid stored access token.")
                return access_token

        # Step 2: Attempt refresh token if available
        refresh_token = params.get_param("sharepoint.refresh_token")

        if refresh_token:
            _logger.info("Attempting to refresh access token...")

            data = {
                "client_id": client_id,
                "client_secret": client_secret,  # Only required if not using pure PKCE
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "scope": "https://graph.microsoft.com/.default",
            }

            response = requests.post(token_url, data=data)
            token_response = response.json()

            if "access_token" in token_response:
                # Store new tokens
                params.set_param("sharepoint.access_token", token_response["access_token"])
                params.set_param("sharepoint.refresh_token", token_response.get("refresh_token", refresh_token))
                expiry_time = int(time.time()) + int(token_response.get("expires_in", 3600))
                params.set_param("sharepoint.token_expiry", expiry_time)

                _logger.info("Access token successfully refreshed.")
                return token_response["access_token"]

            else:
                _logger.error(f"Failed to refresh token: {token_response}")

        # Step 3: If no valid access or refresh token, exchange authorization code
        if auth_code:
            _logger.info("Exchanging authorization code for access token...")

            code_verifier = params.get_param("sharepoint.code_verifier")  # Retrieve stored PKCE verifier

            data = {
                "client_id": client_id,
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
                "scope": "https://graph.microsoft.com/.default",
            }

            if client_secret:  # Include client_secret if not using pure PKCE
                data["client_secret"] = client_secret

            response = requests.post(token_url, data=data)
            token_response = response.json()

            if "access_token" in token_response:
                # Store tokens
                params.set_param("sharepoint.access_token", token_response["access_token"])
                params.set_param("sharepoint.refresh_token", token_response.get("refresh_token", ""))
                expiry_time = int(time.time()) + int(token_response.get("expires_in", 3600))
                params.set_param("sharepoint.token_expiry", expiry_time)

                _logger.info("Access token successfully obtained.")
                return token_response["access_token"]

            else:
                _logger.error(f"Failed to obtain access token: {token_response}")

        # Step 4: No valid token, force reauthorization
        _logger.error("No valid token found. User must reauthorize.")

        auth_url = self.get_authorization_url()
        _logger.info(f"User must visit this URL to reauthorize: {auth_url}")

        return None  # No valid token available

    def get_site_id(self, access_token, site_url):
        url = f"https://graph.microsoft.com/v1.0/sites/{site_url}:"
        headers = {"Authorization": f"Bearer {access_token}"}

        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get("id")

        _logger.error(res.text)
        return False

    def list_items(self, access_token, site_id, folder_path=None):
        headers = {"Authorization": f"Bearer {access_token}"}

        if folder_path:
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}:/children"
        else:
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"

        res = requests.get(url, headers=headers)

        # 🔥 HANDLE TOKEN EXPIRY DURING CALL
        if res.status_code == 401:
            access_token = self.get_access_token()
            headers = {"Authorization": f"Bearer {access_token}"}
            res = requests.get(url, headers=headers)

        if res.status_code == 200:
            return res.json().get("value", [])

        _logger.error(res.text)
        return []


# =========================================================
# WIZARD LINE (FILES/FOLDERS)
# =========================================================
class SharePointBrowserLine(models.TransientModel):
    _name = "sharepoint.browser.line"
    _description = "SharePoint Browser Line"

    wizard_id = fields.Many2one("sharepoint.browser.wizard")

    name = fields.Char(required=True)
    item_type = fields.Selection([
        ("folder", "Folder"),
        ("file", "File")
    ], required=True)
    item_id = fields.Char()
    web_url = fields.Char()
    path = fields.Char()
    file_content = fields.Binary("Upload File")
    file_name = fields.Char("File Name")
    is_uploaded = fields.Boolean(default=False)
    is_from_sharepoint = fields.Boolean(default=False)

    def action_upload_to_sharepoint(self):
        self.ensure_one()

        if self.is_uploaded:
            raise UserError("Already uploaded")

        wizard = self.wizard_id
        service = self.env["sharepoint.service"]

        access_token = service.get_access_token()
        site_url = wizard._get_site_url()
        site_id = service.get_site_id(access_token, site_url)

        if not site_id:
            raise ValidationError("Invalid SharePoint Site")

        base_path = wizard.current_path or ""

        if self.item_type == "folder":
            self._create_folder(access_token, site_id, base_path)

        elif self.item_type == "file":
            if not self.file_content:
                raise ValidationError("Please upload file")

            self._upload_file(access_token, site_id, base_path)

        self.is_uploaded = True

        # reload wizard
        wizard.load_items()

        return {
            "type": "ir.actions.act_window",
            "res_model": "sharepoint.browser.wizard",
            "view_mode": "form",
            "res_id": wizard.id,
            "target": "new",
        }

    @api.model
    def create(self, vals):
        _logger.warning(f"CREATE CALLED: {vals}")

        # ✅ VERY IMPORTANT: skip API for SharePoint-loaded records
        if vals.get("is_from_sharepoint"):
            return super().create(vals)

        # 👉 Only user-created records reach here
        record = super().create(vals)

        wizard = record.wizard_id
        service = self.env["sharepoint.service"]

        access_token = service.get_access_token()
        site_id = service.get_site_id(access_token, wizard._get_site_url())

        base_path = wizard.current_path or ""

        if record.item_type == "folder":
            record._create_folder(service, access_token, site_id, base_path, record.name)

        elif record.item_type == "file":
            if not record.file_content:
                raise ValidationError("Please upload file")

            record._upload_file(service, access_token, site_id, base_path, record)
        record.is_uploaded = True
        # 🔁 Reload AFTER creation (safe now)
        wizard.load_items()

        return record

    # def unlink(self):
    #     service = self.env["sharepoint.service"]
    #
    #     for rec in self:
    #         # 🔴 Skip SharePoint delete for auto-loaded records
    #         # if rec.is_from_sharepoint:
    #         #     continue
    #         if self.env.context.get("skip_sp_delete"):
    #             return super().unlink()
    #         # ✅ Only delete if it's user-created / synced record
    #         if rec.item_id:
    #             access_token = service.get_access_token()
    #             site_id = service.get_site_id(access_token, rec.wizard_id._get_site_url())
    #
    #             url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{rec.item_id}"
    #
    #             headers = {"Authorization": f"Bearer {access_token}"}
    #             res = requests.delete(url, headers=headers)
    #
    #             if res.status_code not in (204, 200):
    #                 _logger.error(res.text)
    #                 raise ValidationError("Failed to delete from SharePoint")
    #
    #     return super().unlink()
    #     # return {"type": "ir.actions.client", "tag": "reload"}

    def action_delete_item(self):
        self.ensure_one()

        service = self.env["sharepoint.service"]
        access_token = service.get_access_token()
        site_id = service.get_site_id(access_token, self.wizard_id._get_site_url())

        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{self.item_id}"

        headers = {"Authorization": f"Bearer {access_token}"}

        res = requests.delete(url, headers=headers)

        if res.status_code not in (204, 200):
            raise ValidationError("Failed to delete from SharePoint")

        self.sudo().unlink()
        return {"type": "ir.actions.client", "tag": "reload"}

    def write(self, vals):
        res = super().write(vals)

        if "name" in vals and not self.is_from_sharepoint:
            service = self.env["sharepoint.service"]
            access_token = service.get_access_token()
            site_id = service.get_site_id(access_token, self.wizard_id._get_site_url())

            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{self.item_id}"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            data = {
                "name": vals["name"]
            }

            requests.patch(url, headers=headers, json=data)

        return res

    def _create_folder(self, service, access_token, site_id, base_path, folder_name):
        _logger.info(f"Uploading to path: {base_path}")
        if base_path:
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{base_path}:/children"
        else:
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }

        res = requests.post(url, headers=headers, json=data)

        if res.status_code not in (200, 201):
            _logger.error(res.text)
            raise ValidationError("Failed to create folder in SharePoint")

    def _upload_file(self, service, access_token, site_id, base_path, record):
        file_bytes = base64.b64decode(self.file_content)
        file_name = self.file_name or self.name

        if base_path:
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{base_path}/{file_name}:/content"
        else:
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{file_name}:/content"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream"
        }

        res = requests.put(url, headers=headers, data=file_bytes)

        if res.status_code not in (200, 201):
            _logger.error(res.text)
            raise ValidationError("Failed to upload file in Sharepoint")


    # ------------------------------------------
    # OPEN FILE
    # ------------------------------------------
    def action_open_file(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_url",
            "url": self.web_url,
            "target": "new",
        }

    # ------------------------------------------
    # OPEN FOLDER
    # ------------------------------------------
    def action_open_folder(self):
        self.ensure_one()

        wizard = self.wizard_id

        wizard.current_path = self.path
        wizard.load_items()

        return {
            "type": "ir.actions.act_window",
            "res_model": "sharepoint.browser.wizard",
            "view_mode": "form",
            "res_id": wizard.id,
            "target": "new",
        }

# =========================================================
# MAIN WIZARD
# =========================================================
class SharePointBrowserWizard(models.TransientModel):
    _name = "sharepoint.browser.wizard"
    _description = "SharePoint Browser"

    current_path = fields.Char(string="Current Path")
    line_ids = fields.One2many("sharepoint.browser.line", "wizard_id")

    # ------------------------------------------
    # CONFIG (SET YOUR SITE HERE)
    # ------------------------------------------
    def _get_site_url(self):
        # Example:
        # yourdomain.sharepoint.com:/sites/yoursite
        return self.env["ir.config_parameter"].sudo().get_param("sharepoint.site_url")

    # ------------------------------------------
    # LOAD DATA
    # ------------------------------------------
    def load_items(self):
        service = self.env["sharepoint.service"]
        params = self.env["ir.config_parameter"].sudo()
        access_token = service.get_access_token()
        site_url = self._get_site_url()

        if not access_token:
            auth_url = service.get_authorization_url()
            base_url = params.get_param("web.base.url")
            redirect_url = f"{base_url}/sharepoint/auth/callback"

            # Notify Admin
            message = Markup(_(
                "⚠️ SharePoint integration requires authorization.<br/>"
                "Configure Redirect URL:<br/><br/>"
                "<a href='{redirect_url}' target='_blank'>{redirect_url}</a><br/><br/>"
                "Steps for redirect URL configuration:<br/>"
                "1️⃣ Open Azure Portal<br/>"
                "2️⃣ Navigate to Azure Active Directory<br/>"
                "3️⃣ Go to App Registrations<br/>"
                "4️⃣ Find your app → Go to Authentication<br/>"
                "5️⃣ Under Redirect URLs, check the WEB section<br/>"
                "6️⃣ Add the above Redirect URL and Save<br/><br/>"
                "Please visit the following URL to authorize:<br/><br/>"
                "<a href='{url}' target='_blank'>{url}</a>"
            ).format(redirect_url=redirect_url, url=auth_url))

            admin_user = self.env.ref("base.user_admin")  # Get admin
            mail_values = {
                "subject": "Action Required: SharePoint Authorization",
                "body_html": f"<p>{message}</p>",
                "email_to": admin_user.email,  # Send to admin's email
                "email_from": self.env.user.email or "no-reply@example.com",
            }
            self.env["mail.mail"].sudo().create(mail_values).send()
            # Optional: Raise a warning for instant feedback
            _logger.error("SharePoint authorization is required. Please check your messages for details.")
            raise ValidationError("SharePoint authorization is required. Please check your messages for details.")

        if not access_token or not site_url:
            raise ValidationError("Missing SharePoint configuration")

        site_id = service.get_site_id(access_token, site_url)

        items = service.list_items(access_token, site_id, self.current_path)
        # If no items and it's root (JMC folder missing)
        if not items and self.current_path:
            raise ValidationError(f"No SharePoint folder/file found for: {self.current_path}")
        # clear old lines
        self.line_ids.filtered(lambda l: l.is_from_sharepoint).sudo().with_context(skip_sp_delete=True).unlink()

        lines = []
        for item in items:
            lines.append((0, 0, {
                "name": item.get("name"),
                "item_type": "folder" if "folder" in item else "file",
                "item_id": item.get("id"),
                "web_url": item.get("webUrl"),
                "path": self._compute_path(item),
                "file_name":item.get("name"),
                "is_from_sharepoint": True,
            }))

        self.line_ids = lines

    def _compute_path(self, item):
        parent_path = item.get("parentReference", {}).get("path", "")
        parent_path = parent_path.replace("/drive/root:", "").strip("/")
        name = item.get("name")
        return f"{parent_path}/{name}".strip("/")

    # ------------------------------------------
    # OPEN WIZARD
    # ------------------------------------------
    def action_open_root(self):
        if not self.current_path:
            self.current_path = False
        self.load_items()

        return {
            "type": "ir.actions.act_window",
            "res_model": "sharepoint.browser.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    # # ------------------------------------------
    # # OPEN FOLDER
    # # ------------------------------------------
    # def action_open_folder(self):
    #     line_id = self.env.context.get("active_id")
    #     line = self.env["sharepoint.browser.line"].browse(line_id)
    #
    #     self.current_path = line.path
    #     self.load_items()
    #
    #     return {
    #         "type": "ir.actions.act_window",
    #         "res_model": "sharepoint.browser.wizard",
    #         "view_mode": "form",
    #         "res_id": self.id,
    #         "target": "new",
    #     }
    #
    # # ------------------------------------------
    # # OPEN FILE
    # # ------------------------------------------
    # def action_open_file(self):
    #     line_id = self.env.context.get("active_id")
    #     line = self.env["sharepoint.browser.line"].browse(line_id)
    #
    #     return {
    #         "type": "ir.actions.act_url",
    #         "url": line.web_url,
    #         "target": "new",
    #     }

    # ------------------------------------------
    # GO BACK
    # ------------------------------------------
    def action_go_back(self):
        if not self.current_path:
            return

        parts = self.current_path.split("/")
        self.current_path = "/".join(parts[:-1]) if len(parts) > 1 else False

        self.load_items()

        return {
            "type": "ir.actions.act_window",
            "res_model": "sharepoint.browser.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

