import json

from odoo import http
from odoo.http import request


class OpmsDynamicLabels(http.Controller):
    @http.route("/opms/labels/mapping", type="http", auth="user", methods=["GET"], csrf=False)
    def opms_labels_mapping(self):
        payload = request.env["opms.label.service"].sudo().get_runtime_replacements()
        return request.make_response(
            json.dumps(payload),
            headers=[
                ("Content-Type", "application/json"),
                ("Cache-Control", "no-store"),
            ],
        )