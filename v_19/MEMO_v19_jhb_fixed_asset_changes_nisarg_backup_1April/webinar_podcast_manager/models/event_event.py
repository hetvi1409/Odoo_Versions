from odoo import models, fields, _, api

class EventEvent(models.Model):
    _inherit = 'event.event'

    webinar_link = fields.Char(string='Webinar Link')
    podcast_link = fields.Char(string='Podcast Link')
    show_podcast_link = fields.Boolean(string="Show Podcast Link", compute="_compute_show_podcast_link")
    show_webinar_link = fields.Boolean(string="Show Webinar Link", compute="_compute_show_webinar_link")

    @api.depends('tag_ids')
    def _compute_show_podcast_link(self):
        for rec in self:
            rec.show_podcast_link = any(
                tag.name == 'Podcast' for tag in rec.tag_ids)

    @api.depends('tag_ids')
    def _compute_show_webinar_link(self):
        for rec in self:
            rec.show_webinar_link = any(
                tag.name == 'Webinar' for tag in rec.tag_ids)