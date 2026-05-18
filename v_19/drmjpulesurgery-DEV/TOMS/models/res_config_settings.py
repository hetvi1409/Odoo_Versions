from odoo import models,fields,api,_


class res_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_inventory_lines_limit = fields.Integer(string="Inventory Lines Limit")
    external_links = fields.Boolean(string="Enable External Links")
    isoleso_url = fields.Boolean()
    aeye_url = fields.Boolean()
    disc_url = fields.Boolean()
    recall_date_delta = fields.Integer(string='Recall Months', help='Number of months for recall')
    show_mono_in_refraction = fields.Boolean(string="Show Mono PD's")
    show_seg_heights_in_refraction = fields.Boolean()

    @api.onchange('external_links')
    def on_change_links(self):
        if self.external_links == False:
            self.aeye_url = False
            self.disc_url = False
            self.isoleso_url = False

    @api.model
    def get_values(self):
       res = super(res_config_settings, self).get_values()
       param_obj = self.env['ir.config_parameter']
       res.update(group_stock_multi_locations=bool(param_obj.sudo().get_param('stock.group_stock_multi_locations')))
       res.update(stock_inventory_lines_limit=int(param_obj.sudo().get_param('stock.stock_inventory_lines_limit')))
       res.update(external_links=bool(param_obj.sudo().get_param('external_links')))
       res.update(aeye_url=bool(param_obj.sudo().get_param('aeye_url')))
       res.update(disc_url=bool(param_obj.sudo().get_param('disc_url')))
       res.update(isoleso_url=bool(param_obj.sudo().get_param('isoleso_url')))
       res.update(recall_date_delta=int(param_obj.sudo().get_param('recall_date_delta')))
       res.update(show_mono_in_refraction=bool(param_obj.sudo().get_param('show_mono_in_refraction')))
       res.update(show_seg_heights_in_refraction=bool(param_obj.sudo().get_param('show_seg_heights_in_refraction')))

       return res

    def set_values(self):
       res = super(res_config_settings, self).set_values()
       param_obj = self.env['ir.config_parameter']
       param_obj.sudo().set_param('stock.group_stock_multi_locations', self.group_stock_multi_locations)
       param_obj.sudo().set_param('stock.stock_inventory_lines_limit', self.stock_inventory_lines_limit)
       param_obj.sudo().set_param('external_links', self.external_links)
       param_obj.sudo().set_param('aeye_url', self.aeye_url)
       param_obj.sudo().set_param('disc_url', self.disc_url)
       param_obj.sudo().set_param('isoleso_url', self.isoleso_url)
       param_obj.sudo().set_param('recall_date_delta', self.recall_date_delta)
       param_obj.sudo().set_param('show_mono_in_refraction', self.show_mono_in_refraction)
       param_obj.sudo().set_param('show_seg_heights_in_refraction', self.show_seg_heights_in_refraction)