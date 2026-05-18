# -*- coding: utf-8 -*-
##############################################################################
#
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class BuildingImages(models.Model):
    _inherit = 'building.images'

    outdoor_id = fields.Many2one("outdoor.advertisement")


class BuildingAttachmentLine(models.Model):
    _inherit = 'building.attachment.line'

    outdoor_id = fields.Many2one("outdoor.advertisement")
    title_deeds_id = fields.Many2one("building")
    contract_id = fields.Many2one("building")
