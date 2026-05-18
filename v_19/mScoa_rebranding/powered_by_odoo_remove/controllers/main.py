import base64

from imghdr import what as image_what

from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound


class RebrandingImageController(http.Controller):
    _PARAM_BY_IMAGE_TYPE = {
        "login_background": "powered_by_odoo_remove.login_background_image",
        "app_background": "powered_by_odoo_remove.app_background_image",
    }

    @http.route("/powered_by_odoo_remove/image/<string:image_type>",type="http",auth="public",website=False,sitemap=False)
    def rebranding_image(self, image_type, **kwargs):
        param_name = self._PARAM_BY_IMAGE_TYPE.get(image_type)
        if not param_name:
            raise NotFound()

        image_b64 = request.env["ir.config_parameter"].sudo().get_param(param_name)
        if not image_b64:
            raise NotFound()

        image_bytes = base64.b64decode(image_b64)
        image_extension = image_what(None, image_bytes) or "png"
        image_mimetype = "image/jpeg" if image_extension == "jpeg" else f"image/{image_extension}"
        headers = [
            ("Content-Type", image_mimetype),
            ("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0"),
        ]
        return request.make_response(image_bytes, headers=headers)
