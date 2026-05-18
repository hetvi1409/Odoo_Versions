
from odoo import api, fields, models


class CemeteryBurialReport(models.Model):
    _name = "cemetery.gravesite.availability.report"
    _description = "Total Burial Per Cemetery"
    _auto = False

    cemetery_id = fields.Many2one('cemetery.cemetery', string="Cemetery")
    section_id = fields.Many2one('cemetery.section', string="Section")
    grave_id = fields.Many2one('grave.grave', string="Grave")

    @property
    def _table_query(self):
        query = """SELECT cemetery.name AS cemetery_name, 
                    cemetery.id as cemetery_id, grave.id as id, 
                    grave.id as grave_id, section.id as section_id
                    FROM cemetery_cemetery cemetery
                    LEFT JOIN grave_grave as grave ON grave.cemetery_id = cemetery.id
                    LEFT JOIN cemetery_section as section ON grave.section_id = section.id
                    GROUP BY cemetery.name,cemetery.id, grave.id, section.id"""
        return query
