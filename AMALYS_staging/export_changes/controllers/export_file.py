from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import export
import datetime
import logging

_logger = logging.getLogger(__name__)


def custom_filename(self, base):
    """Override filename logic globally"""
    _logger.info("Custom filename override called for base=%s", base)
    if base not in request.env:
        return base or "Export"

    if base == "sale.order":
        model_description = request.env['ir.model']._get(base).name
        today = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{model_description}_{today}"

    # fallback to original logic if needed
    model_description = request.env['ir.model']._get(base).name
    return f"{model_description} ({base})"


export.ExportFormat.filename = custom_filename