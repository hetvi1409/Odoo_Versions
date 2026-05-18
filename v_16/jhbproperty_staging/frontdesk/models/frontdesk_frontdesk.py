# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import uuid

from werkzeug.urls import url_join
from datetime import datetime, timedelta

from odoo import models, fields, api, tools, _

ASK_FIELDS_SELECTION = [
    ("required", "Required"),
    ("optional", "Optional"),
    ("none", "None"),
]

PLANNED_VISITOR_TIME = 45


class Frontdesk(models.Model):
    _name = 'frontdesk.frontdesk'
    _description = 'Frontdesk'

    name = fields.Char('Frontdesk Name', required=True)
    responsible_ids = fields.Many2many('res.users', string='Responsibles', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    theme = fields.Selection(selection=[("light", "Light"), ("dark", "Dark")], default='light')
    image = fields.Image("Image")
    host_selection = fields.Boolean('Host Selection', groups='frontdesk.frontdesk_group_user')
    authenticate_guest = fields.Boolean('Authenticate Guest', default=True, groups='frontdesk.frontdesk_group_user')
    ask_phone = fields.Selection(string='Phone', selection=ASK_FIELDS_SELECTION, default='required', required=True)
    ask_company = fields.Selection(string='Organization', selection=ASK_FIELDS_SELECTION, default='optional',
                                   required=True)
    ask_email = fields.Selection(string='Email', selection=ASK_FIELDS_SELECTION, default='none', required=True)
    notify_email = fields.Boolean('Notify by email', groups='frontdesk.frontdesk_group_user')
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain="[('model', '=', 'frontdesk.frontdesk')]",
        default=lambda self: self.env.ref('frontdesk.frontdesk_mail_template', raise_if_not_found=False)
    )
    notify_sms = fields.Boolean('Notify by SMS', groups='frontdesk.frontdesk_group_user')
    sms_template_id = fields.Many2one(
        'sms.template',
        string='SMS Template',
        domain="[('model', '=', 'frontdesk.frontdesk')]",
        default=lambda self: self.env.ref('frontdesk.frontdesk_sms_template', raise_if_not_found=False)
    )
    self_check_in = fields.Boolean('Self Check-In', groups='frontdesk.frontdesk_group_user',
                                   help='Shows a QR code in the interface, for guests to check in from their mobile phone.'
                                   )
    drink_offer = fields.Boolean('Offer Drinks', groups='frontdesk.frontdesk_group_user')
    drink_ids = fields.Many2many('frontdesk.drink')
    notify_discuss = fields.Boolean('Notify by discuss', default=True, groups='frontdesk.frontdesk_group_user')
    description = fields.Html(groups='frontdesk.frontdesk_group_user')
    visitor_ids = fields.One2many('frontdesk.visitor', 'station_id', string='Visitors')
    guest_on_site = fields.Integer('Guests On Site', compute='_compute_dashboard_data')
    pending = fields.Integer('Pending', compute='_compute_dashboard_data')
    drink_to_serve = fields.Integer('Drinks to Serve', compute='_compute_dashboard_data')
    latest_check_in = fields.Char(compute='_compute_dashboard_data')
    visitor_properties_definition = fields.PropertiesDefinition('Visitor Properties')
    access_token = fields.Char("Security Token", default=lambda self: str(uuid.uuid4()), required=True, copy=False,
                               readonly=True)
    kiosk_url = fields.Char('Kiosk URL', compute='_compute_kiosk_url', groups='frontdesk.frontdesk_group_user')
    is_favorite = fields.Boolean('Is Favorite')
    active = fields.Boolean('Active', default=True)
    department_id = fields.Many2one("hr.department", string="Department")
    host_ids = fields.Many2one('hr.employee', string='Host Name', domain="[('user_id', '!=', False)]")

    def _compute_dashboard_data(self):
        """Computes the number of guests currently on site, pending visitors, drinks to serve, and latest check-in time."""

        # Read visitor data grouped by station and state
        visitor_data = self.env['frontdesk.visitor'].read_group(
            [('state', 'in', ('checked_in', 'planned')), ('station_id', 'in', self.ids)],
            ['state', 'station_id'],
            ['state', 'station_id'],lazy=False
        )

        # Initialize mappings
        checked_in_mapped = {}
        planned_mapped = {}
        for record in visitor_data:
            station_id = record.get('station_id', False)
            if station_id and isinstance(station_id, tuple):  # Ensures station_id is valid
                station_id = station_id[0]
                if record['state'] == 'checked_in':
                    checked_in_mapped[station_id] = record.get('__count', 0)
                elif record['state'] == 'planned':
                    planned_mapped[station_id] = record.get('__count', 0)

        # Read drink data grouped by station
        drinks_data = self.env['frontdesk.visitor'].read_group(
            [('drink_ids', '!=', False), ('served', '=', False), ('station_id', 'in', self.ids)],
            ['station_id'],
            ['station_id'],lazy=False
        )

        drinks_data_mapped = {d['station_id'][0]: d.get('__count', 0) for d in drinks_data if
                              'station_id' in d and isinstance(d['station_id'], tuple)}

        for frontdesk in self:
            guest_on_site = checked_in_mapped.get(frontdesk.id, 0)
            pending = planned_mapped.get(frontdesk.id, 0)
            drink_to_serve = drinks_data_mapped.get(frontdesk.id, 0)

            # Find the latest check-in time
            latest_check_in = False
            last_visitors = frontdesk.visitor_ids.filtered(lambda v: v.state == 'checked_in').sorted('check_in',
                                                                                                     reverse=True)
            if last_visitors:
                latest_check_in_time = last_visitors[0].check_in
                if latest_check_in_time:
                    total_seconds = (datetime.now() - latest_check_in_time).total_seconds()
                    if total_seconds < 3600:
                        latest_check_in = _("Last Check-In: %s minutes ago") % int(total_seconds / 60)
                    else:
                        latest_check_in = _("Last Check-In: %s hours ago") % int(total_seconds / 3600)

            # Update the computed fields
            frontdesk.guest_on_site = guest_on_site
            frontdesk.pending = pending
            frontdesk.drink_to_serve = drink_to_serve
            frontdesk.latest_check_in = latest_check_in

    @api.depends('access_token')
    def _compute_kiosk_url(self):
        for frontdesk in self:
            frontdesk.kiosk_url = url_join(frontdesk.get_base_url(),
                                           '/kiosk/%s/%s' % (frontdesk.id, frontdesk.access_token))

    def get_host_data_frontdesk(self, station_id):
        """get_host_data_frontdesk"""
        frontdesk = self.env['frontdesk.frontdesk'].browse(int(station_id))
        host = frontdesk.host_ids
        return {
            # 'department_id': frontdesk.department_id.id,
            'hostName' : host.name,
            'hostId' : host.id,
            'inputDepartment' : frontdesk.department_id.id,
            'inputPropertyType': "social_lease"
        }

    def action_open_kiosk(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.kiosk_url,
            'target': 'new',
        }

    def action_open_visitors(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Visitors"),
            'res_model': 'frontdesk.visitor',
            'view_mode': 'tree,form,kanban,graph,pivot,calendar,gantt',
            'context': {
                "search_default_state_is_planned": 1,
                "search_default_state_is_checked_in": 1,
                "search_default_today": 1
            },
            'domain': [('station_id.id', '=', self.id)],
        }

    def _get_frontdesk_field(self):
        return ['description', 'host_selection', 'drink_offer', 'self_check_in', 'theme',
                'drink_ids', 'ask_email', 'ask_phone', 'ask_company', 'authenticate_guest']

    def _get_frontdesk_data(self):
        """ Returns the data to the frontend. """
        self.ensure_one()
        data = {
            'company': {'name': self.company_id.name, 'id': self.company_id.id},
            'langs': [{'code': lang[0], 'name': lang[1]} for lang in self.env['res.lang'].get_installed()],
            'station': self.search_read([('id', '=', self.id)], self._get_frontdesk_field()),
        }
        if self.drink_offer:
            data['drinks'] = self.env['frontdesk.drink'].search_read([('id', 'in', self.drink_ids.ids)], ['name'])
        return data

    def _get_planned_visitors(self):
        """ Returns the planned visitors for quick sign in to the frontend. """
        time_min = datetime.now() - timedelta(minutes=PLANNED_VISITOR_TIME)
        time_max = datetime.now() + timedelta(minutes=PLANNED_VISITOR_TIME)
        visitors = self.env['frontdesk.visitor'].sudo().search_read(
            [('check_in', '>=', time_min), ('check_in', '<=', time_max), ('state', '=', 'planned'),
             ('station_id.id', '=', self.id)],
            ['name', 'company', 'message', 'host_ids'])
        if visitors:
            return [{
                **visitor,
                'host_ids': [{'id': host.id, 'name': host.name} for host in
                             self.env['hr.employee'].browse(visitor['host_ids'])]
            } for visitor in visitors]
        return []

    def _get_tmp_code(self):
        self.ensure_one()
        return tools.hmac(self.env(su=True), 'kiosk-mobile', (self.id, fields.Date.to_string(fields.Datetime.now())))

    def action_open_frontdesk(self):
        return self.env["ir.actions.actions"]._for_xml_id("frontdesk.open_frontdesk_action")
