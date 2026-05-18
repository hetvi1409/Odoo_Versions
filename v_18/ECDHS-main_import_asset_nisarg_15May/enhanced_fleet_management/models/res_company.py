# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    documents_fleet_settings = fields.Boolean(
        string="Fleet Document Management",
        default=False,
        help="Enable integration with Documents app for Fleet management. Requires Documents module."
    )
    # Note: documents_fleet_folder field is NOT defined here to avoid dependency issues
    # If you need this field, install the 'documents' module first
