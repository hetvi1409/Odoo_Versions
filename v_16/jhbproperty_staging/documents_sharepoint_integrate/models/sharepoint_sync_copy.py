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

_logger = logging.getLogger(__name__)

# This file sharepoint_sync for fetch only jmcnumber folder

class SharePointSync(models.Model):
    _name = "document.sharepoint.sync"
    _description = "Sync Odoo Documents with SharePoint"

    def get_config_param(self, key):
        """Helper function to get stored system parameters."""
        return self.env["ir.config_parameter"].sudo().get_param(key)

    def generate_pkce_challenge(self):
        """Generate PKCE code_verifier and code_challenge."""
        code_verifier = base64.urlsafe_b64encode(os.urandom(64)).decode('utf-8')
        code_verifier = code_verifier.rstrip("=")  # Remove padding explicitly
        hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(hashed).decode('utf-8')
        code_challenge = code_challenge.rstrip("=")  # Remove padding explicitly
        return code_verifier, code_challenge

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
        """Retrieve the SharePoint Site ID for the given site URL."""
        url = f"https://graph.microsoft.com/v1.0/sites/{site_url}:"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("id")
        else:
            _logger.error(f"Failed to get SharePoint site ID for {site_url}: {response.text}")
            return None

    def create_sharepoint_folder(self, access_token, site_id, folder_path):
        """Create a folder in SharePoint."""
        # site_id = self.get_site_id(access_token)
        # if not site_id:
        #     return

        check_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(check_url, headers=headers)
        if response.status_code == 200:
            _logger.info(f"Folder '{folder_path}' already exists in SharePoint. Skipping creation.")
            return  # Folder already exists, no need to create it
        elif response.status_code == 404:  # Folder not found, so create it
            headers["Content-Type"] = "application/json"

            parent_folder_path = "/".join(folder_path.split("/")[:-1])  # Get only the parent path
            folder_name = folder_path.split("/")[-1]  # Get the actual folder name

            create_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{parent_folder_path}:/children"
            data = json.dumps({
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            })

            create_response = requests.post(create_url, headers=headers, data=data)
            if create_response.status_code in [200, 201]:
                _logger.info(f"Folder '{folder_path}' created in SharePoint")
            else:
                _logger.error(f"Failed to create folder: {create_response.text}")
        else:
            _logger.error(f"Error checking folder existence: {response.text}")

    def file_exists_in_sharepoint(self, access_token, site_id, folder_path, file_name):
        """Check if a file exists in SharePoint."""
        # site_id = self.get_site_id(access_token)
        # if not site_id:
        #     return False

        folder_path = folder_path.strip("/")
        check_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}/{file_name}"

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(check_url, headers=headers)
        return response.status_code == 200  # File exists if response is 200

    def upload_file_to_sharepoint(self, access_token, site_id, folder_path, file_name, attachment):
        """Upload large files to SharePoint using chunked upload session."""

        folder_path = folder_path.strip("/")

        # Correct API URL
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}/{file_name}:/createUploadSession"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Start Upload Session
        response = requests.post(url, headers=headers)
        if response.status_code not in [200, 201]:
            _logger.error(f"Failed to create upload session: {response.text}")
            return

        upload_url = response.json().get("uploadUrl")  # Get the upload URL
        if not upload_url:
            _logger.error("Upload session URL not found.")
            return

        if not attachment.store_fname:
            _logger.error("❌ Attachment is missing or empty.")
            return

        file_path = attachment._full_path(attachment.store_fname)  # Get file path

        # Fix: Check if file exists before uploading
        if not os.path.exists(file_path):
            _logger.error(f"❌ File not found: {file_path}")
            return

        file_size = os.path.getsize(file_path)  # Get file size
        chunk_size = 327680  # 320KB chunks (must be multiple of 320KB)

        _logger.info(f"Uploading '{file_name}' (Size: {file_size} bytes) in chunks to '{folder_path}'.")

        with open(file_path, "rb") as f:
            start = 0
            while start < file_size:
                chunk = f.read(chunk_size)
                end = start + len(chunk) - 1

                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Range": f"bytes {start}-{end}/{file_size}"
                }

                chunk_response = requests.put(upload_url, headers=headers, data=chunk)

                if chunk_response.status_code not in [200, 201, 202]:
                    _logger.error(f"Chunk upload failed: {chunk_response.text}")
                    return

                _logger.info(f"Uploaded {end + 1}/{file_size} bytes.")
                start += len(chunk)

        _logger.info(f"File '{file_name}' uploaded successfully!")

    def compute_sharepoint_folder_path(self, folder):
        """Builds the correct SharePoint path for a given folder, ensuring no duplicate root folders."""
        path_parts = []
        current_folder = folder

        while current_folder:
            if current_folder.name in path_parts:
                _logger.warning(f"Duplicate folder detected in path: {current_folder.name}, skipping...")
                break  # Prevent self-referencing issues

            path_parts.append(current_folder.name)
            current_folder = current_folder.parent_folder_id  # Move to parent folder

            # Prevent the root folder from being added as a child of itself
            if current_folder and current_folder.id == folder.id:
                _logger.warning(f"Prevented infinite loop: {current_folder.name}")
                break

        full_path = "/".join(reversed(path_parts))  # Reverse to get correct top-down structure

        _logger.info(f"Computed SharePoint Path: {full_path}")  # Debugging log
        return full_path

    def sync_folders_to_sharepoint(self, access_token, parent_folder=None, sharepoint_parent_path="",
                                   parent_site_url=None):
        """Sync Odoo document folders with SharePoint structure."""

        domain = [("parent_folder_id", "=", parent_folder.id)] if parent_folder else [("parent_folder_id", "=", False)]
        folders = self.env["documents.folder"].search(domain)

        for folder in folders:
            if parent_folder and folder.id == parent_folder.id:
                _logger.warning(f"Skipping self-referencing folder: {folder.name}")
                continue

            base_url = folder.sharepoint_base_url
            site_name = folder.sharepoint_site_name
            site_url = parent_site_url

            if base_url and site_name:
                base_url = base_url.replace("http://", "").replace("https://", "")
                base_url = re.sub(r'(www.)(?!com)', r'', base_url)
                if base_url.endswith("/"):
                    base_url = base_url[:-1]
                if "/" not in site_name:
                    site_name = f"sites/{site_name}"
                site_url = f"{base_url}:/{site_name}"

            if not site_url:
                _logger.warning(f"Skipping folder '{folder.name}': No SharePoint site URL specified.")
                continue

            site_id = self.get_site_id(access_token, site_url)
            if not site_id:
                _logger.error(f"Skipping folder '{folder.name}': Unable to fetch SharePoint site ID.")
                continue

            # Compute correct full SharePoint path
            folder_path = self.compute_sharepoint_folder_path(folder)

            # Prevent root folder from being placed inside itself
            if parent_folder and folder_path == parent_folder.name:
                _logger.warning(f"Skipping duplicate root folder creation: {folder.name}")
                continue

            _logger.info(f"Processing Folder: '{folder.name}' (Path: {folder_path})")

            if not self.folder_exists_in_sharepoint(access_token, site_id, folder_path):
                _logger.info(f"Creating SharePoint Folder: {folder_path}")
                self.create_sharepoint_folder(access_token, site_id, folder_path)
            else:
                _logger.info(f"Folder already exists in SharePoint: {folder_path}")

            # Upload files
            documents = self.env["documents.document"].search([("folder_id", "=", folder.id)])
            for doc in documents:
                if doc.attachment_id:
                    _logger.info(f"Uploading File: {doc.attachment_id.name} to {folder_path}")
                    self.upload_file_to_sharepoint(access_token, site_id, folder_path, doc.attachment_id.name,
                                                   doc.attachment_id)

            # Sync subfolders only if they are truly subfolders
            subfolders = self.env["documents.folder"].search([("parent_folder_id", "=", folder.id)])
            for subfolder in subfolders:
                if subfolder.id == folder.id:  # Safety check to avoid infinite recursion
                    _logger.warning(f"Skipping recursive loop: {subfolder.name}")
                    continue
                _logger.info(f"Syncing Subfolder: {subfolder.name} (Parent: {folder.name})")
                self.sync_folders_to_sharepoint(access_token, subfolder, folder_path, site_url)

    def folder_exists_in_sharepoint(self, access_token, site_id, folder_path):
        """Check if a folder exists in SharePoint"""
        # site_id = self.get_site_id(access_token)
        headers = {"Authorization": f"Bearer {access_token}"}

        folder_check_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}"

        # Set up retries for the session
        retry_strategy = urllib3.Retry(
            total=5,  # Retry up to 5 times
            backoff_factor=1,  # Wait 1 second between retries
            status_forcelist=[500, 502, 503, 504, 429],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        try:
            response = session.get(folder_check_url, headers=headers)
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error checking folder: {e}")
            return False
        # response = requests.get(folder_check_url, headers=headers)
        #
        # return response.status_code == 200  # Returns True if folder exists

    def get_sharepoint_items_recursive(self, access_token, site_id, folder_path="", processed_folders=set()):
        """Retrieve all folders and files from SharePoint without infinite recursion."""
        if folder_path in processed_folders:
            return []  # Avoid infinite loop

        processed_folders.add(folder_path)  # Mark folder as processed

        items = []
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}:/children" if folder_path else f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            results = response.json().get("value", [])
            for item in results:
                items.append(item)

                # Recursively fetch subfolders
                if "folder" in item:
                    subfolder_path = item.get("parentReference", {}).get("path", "").replace("/drive/root:", "").strip(
                        "/")
                    subfolder_path = f"{subfolder_path}/{item['name']}".strip("/") if subfolder_path else item["name"]

                    sub_items = self.get_sharepoint_items_recursive(access_token, site_id, subfolder_path,
                                                                    processed_folders)
                    items.extend(sub_items)

            return items
        else:
            _logger.error(f"Failed to retrieve SharePoint items: {response.text}")
            return []

    def sync_sharepoint_folders_to_odoo(self, access_token):
        """Sync SharePoint folders into Odoo."""
        root_folders = self.env["documents.folder"].search([("parent_folder_id", "=", False)])
        jmc_pattern = re.compile(r"^JMC\d+$")  # JMC + digits only

        for root_folder in root_folders:
            base_url = root_folder.sharepoint_base_url
            site_name = root_folder.sharepoint_site_name
            site_url = False
            if base_url and site_name:
                base_url = base_url.replace("http://", "").replace("https://", "")
                base_url = re.sub(r'(www.)(?!com)', r'', base_url)
                if base_url.endswith("/"):
                    base_url = base_url[:-1]
                if "/" not in site_name:
                    site_name = f"sites/{site_name}"
                site_url = f"{base_url}:/{site_name}"
            if not site_url:
                _logger.warning(f"Skipping folder '{root_folder.name}': No SharePoint site URL specified.")
                continue

            site_id = self.get_site_id(access_token, site_url)
            if not site_id:
                _logger.error(f"Skipping folder '{root_folder.name}': Unable to fetch SharePoint site ID.")
                continue

            sharepoint_items = self.get_sharepoint_items_recursive(access_token, site_id)
            folder_mapping = {root_folder.name: root_folder}  # Store already created folders
            for item in sharepoint_items:
                if "folder" in item:  # It's a folder
                    folder_name = item["name"]
                    parent_path = item.get("parentReference", {}).get("path", "").replace("/drive/root:", "").strip("/")

                    # 👉 Apply JMC filter ONLY at root level
                    is_root_level = "/" not in parent_path

                    if is_root_level:
                        if not jmc_pattern.match(folder_name):
                            _logger.info(f"⏭ Skipping non-JMC root folder: {folder_name}")
                            continue

                    # Build full path
                    normalized_parent = parent_path.strip("/")
                    full_path = f"{normalized_parent}/{folder_name}".strip("/")

                    # Determine parent folder correctly
                    parent_folder = folder_mapping.get(normalized_parent)

                    # Try splitting the path to locate the correct parent
                    if not parent_folder:
                        parent_parts = normalized_parent.split("/") if normalized_parent else []
                        for i in range(len(parent_parts), 0, -1):  # Try to find the closest existing parent
                            partial_path = "/".join(parent_parts[:i])
                            parent_folder = folder_mapping.get(partial_path)
                            if parent_folder:
                                break

                    # If still not found, find in Odoo
                    if not parent_folder:
                        parent_folder = self.env["documents.folder"].search([("name", "=", parent_path)], limit=1)

                    # If still not found, assign to root_folder as a last resort
                    if not parent_folder:
                        parent_folder = root_folder

                    # Check if the folder already exists in the correct location
                    existing_folder = self.env["documents.folder"].search([
                        ("name", "=", folder_name),
                        ("parent_folder_id", "=", parent_folder.id)
                    ], limit=1)

                    if not existing_folder:
                        _logger.info(f"🔍 Checking Parent for: {folder_name}")
                        _logger.info(f"🔍 Expected Parent Path: {parent_path}")
                        _logger.info(
                            f"🔍 Found Parent Folder in Odoo: {parent_folder.name if parent_folder else '❌ Not Found'}")
                        new_folder = self.env["documents.folder"].create({
                            "name": folder_name,
                            "parent_folder_id": parent_folder.id  # Assign to correct parent
                        })
                        normalized_path = "/".join(parent_path.split("/")).strip("/")
                        folder_mapping[f"{normalized_path}/{folder_name}"] = new_folder
                    else:
                        _logger.info(f"Folder '{folder_name}' already exists in Odoo under '{parent_folder.name}'.")
                        folder_mapping[f"{parent_path}/{folder_name}".strip("/")] = existing_folder  # Prevent duplicate

                # ✅ Process Files in Parallel
                elif "file" in item:
                    file_name = item["name"]
                    parent_path = item.get("parentReference", {}).get("path", "").replace("/drive/root:", "").strip(
                        "/")

                    normalized_path = parent_path.strip("/")

                    # ❗ Only process files inside JMC folders
                    # Check if parent path starts with any JMC folder
                    root_part = normalized_path.split("/")[0] if normalized_path else ""

                    if not jmc_pattern.match(root_part):
                        _logger.info(f"⏭ Skipping file outside JMC folder: {file_name}")
                        continue

                    odoo_folder = folder_mapping.get(normalized_path)

                    # If folder not found, search in Odoo
                    if not odoo_folder:
                        _logger.warning(
                            f"⚠️ Folder '{parent_path}' not found in Odoo for file '{file_name}'. Trying to find it.")
                        folder_parts = normalized_path.split("/")
                        current_parent = None

                        for part in folder_parts:
                            existing_folder = self.env["documents.folder"].search([
                                ("name", "=", part),
                                ("parent_folder_id", "=", current_parent.id if current_parent else False)
                            ], limit=1)

                            if not existing_folder:
                                _logger.error(f"❌ Could not find matching Odoo folder for '{part}'")
                                continue

                            current_parent = existing_folder

                        odoo_folder = current_parent if current_parent else None

                    if not odoo_folder:
                        _logger.error(f"❌ Skipping file '{file_name}' – No matching folder in Odoo.")
                        continue

                    # Check if file already exists
                    existing_file = self.env["documents.document"].search([
                        ("name", "=", file_name),
                        ("folder_id", "=", odoo_folder.id)
                    ], limit=1)

                    # Download file if it doesn't exist
                    if not existing_file or not existing_file.datas:
                        _logger.info(
                            f"📥 Downloading '{file_name}' from SharePoint to Odoo in '{odoo_folder.name}'.")
                        self.download_file_from_sharepoint(access_token, site_id, parent_path, file_name,
                                                           odoo_folder)
                    else:
                        _logger.info(f"✅ File '{file_name}' already exists in Odoo. Skipping download.")

    def download_file_from_sharepoint(self, access_token, site_id, file_path, file_name, odoo_folder):
        """Download a file from SharePoint and store it in Odoo."""
        download_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{file_path}/{file_name}:/content"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(download_url, headers=headers, stream=True)
        if response.status_code == 200:
            file_data = response.content
            attachment = self.env["ir.attachment"].sudo().create({
                "name": file_name,
                "datas": base64.b64encode(file_data),
                "res_model": "documents.document",
                "res_id": 0,  # Set initially to 0 to avoid mislinking
            })

            # Ensure the document is correctly created in the Odoo folder
            document = self.env["documents.document"].sudo().create({
                "name": file_name,
                "folder_id": odoo_folder.id,
                "attachment_id": attachment.id
            })

            _logger.info(
                f"📂 File '{file_name}' linked to Odoo folder '{odoo_folder.name}' (Document ID: {document.id}).")
        else:
            _logger.error(f"Failed to download file '{file_name}': {response.text}")

    def sync_odoo_documents_to_sharepoint(self):
        """Sync Odoo folders and documents with SharePoint."""
        params = self.env["ir.config_parameter"].sudo()
        access_token = self.get_access_token()  # Call the updated method

        if not access_token:
            auth_url = self.get_authorization_url()
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
            return

        _logger.info("Starting SharePoint → Odoo Sync...")
        self.sync_sharepoint_folders_to_odoo(access_token)

        _logger.info("Starting Odoo → SharePoint Sync...")
        self.sync_folders_to_sharepoint(access_token)
