from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class SharePointAuthController(http.Controller):

    @http.route('/sharepoint/auth/callback', type='http', auth='public')
    def sharepoint_auth_callback(self, **kwargs):
        """Handles the callback from Microsoft OAuth and exchanges the auth code for tokens."""
        auth_code = kwargs.get("code")
        if not auth_code:
            _logger.error("No authorization code received from Microsoft.")
            return "Authorization failed. Please try again."

        sharepoint_sync = request.env['document.sharepoint.sync'].sudo()
        access_token = sharepoint_sync.get_access_token(auth_code)

        if access_token:
            return "Authorization successful! You can now close this window."
        else:
            return "Authorization failed. Check Odoo logs for details."
