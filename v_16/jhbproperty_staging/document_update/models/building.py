from odoo import models,fields
import logging
_logger = logging.getLogger(__name__)


class Building(models.Model):
    """Method for building"""
    _inherit = "building"

    # def name_get(self):
    #     res = []
    #     for record in self:
    #         res.append(
    #             (record.id, '%s' % (record.jmc_number)))
    #     return res
    #     if not self.env.context.get('property_jmc_number', True):
    #         return super(Building, self).name_get()
    #     else:
    #         return [(record.id, record.jmc_number) for record in self]

    folder_id = fields.Many2one('documents.folder', string='Document Folder')


    def cron_link_building_folders(self):
        """Link SharePoint folders to Building based on JMC number"""

        buildings = self.env['building'].sudo().search([
            ('jmc_number', '!=', False),('folder_id','=',False)
        ])

        for building in buildings:
            jmc = building.jmc_number.strip()

            if not jmc:
                continue

            folder = self.env['documents.folder'].sudo().search([
                ('name', '=', jmc)
            ], limit=1)

            if folder:
                if building.folder_id != folder:
                    building.folder_id = folder.id
            else:
                # Optional logging
                _logger.info(f"No folder found for JMC: {jmc}")

    def action_open_sharepoint(self):
        wizard = self.env['sharepoint.browser.wizard'].create({
            "current_path": self.jmc_number or False
        })
        return wizard.action_open_root()