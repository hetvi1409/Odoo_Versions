# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from lxml import etree
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    documents_fleet_settings = fields.Boolean(
        related='company_id.documents_fleet_settings',
        readonly=False,
        string="Fleet Document Management"
    )
    # Note: documents_fleet_folder field is NOT defined here to avoid dependency issues
    # If you need this field, install the 'documents' module first

    @api.model
    def get_views(self, views, options=None):
        """Override to remove documents-related fields/containers if 'documents' isn't installed.

        This is view-type agnostic (form/list/kanban) and aims to be robust w.r.t.
        different invisibility patterns used in Odoo 18.
        """
        result = super().get_views(views, options=options)

        # Iterate available views and sanitize their arch
        for view_type, view_payload in (result.get('views') or {}).items():
            arch = view_payload.get('arch')
            if not arch:
                continue
            try:
                doc = etree.fromstring(arch)
                modified = False

                # Remove the missing field explicitly
                for node in doc.xpath("//field[@name='documents_fleet_folder']"):
                    parent = node.getparent()
                    if parent is not None:
                        parent.remove(node)
                        modified = True
                        _logger.info("Removed documents_fleet_folder field from view (%s)", view_type)

                # Remove labels referencing the missing field
                for node in doc.xpath("//label[@for='documents_fleet_folder']"):
                    parent = node.getparent()
                    if parent is not None:
                        parent.remove(node)
                        modified = True

                # Remove containers that control visibility via attrs for documents settings/folder
                # Matches any element whose attrs mentions documents_fleet_settings or documents_fleet_folder
                for node in doc.xpath("//*[contains(@attrs, 'documents_fleet_settings') or contains(@attrs, 'documents_fleet_folder')]"):
                    parent = node.getparent()
                    if parent is not None:
                        parent.remove(node)
                        modified = True

                # Backward-compat: remove elements using legacy invisible attr pattern
                for node in doc.xpath("//*[@invisible='not documents_fleet_settings']"):
                    parent = node.getparent()
                    if parent is not None:
                        parent.remove(node)
                        modified = True

                if modified:
                    view_payload['arch'] = etree.tostring(doc, encoding='unicode')
            except Exception as e:
                _logger.warning("Error processing view for documents_fleet_* removal (%s): %s", view_type, e)

        return result

