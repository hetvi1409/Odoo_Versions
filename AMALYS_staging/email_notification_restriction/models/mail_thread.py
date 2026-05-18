# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import is_html_empty
from odoo.tools.misc import get_lang
from collections import defaultdict, Counter
from odoo.fields import Command


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'


    # OVERRIDE
    def _message_auto_subscribe_notify(self, partner_ids, template):
        """ Notify new followers, using a template to render the content of the
        notification message. Notifications pushed are done using the standard
        notification mechanism in mail.thread. It is either inbox either email
        depending on the partner state: no user (email, customer), share user
        (email, customer) or classic user (notification_type)

        :param partner_ids: IDs of partner to notify;
        :param template: XML ID of template used for the notification;
        """
        if not self or self.env.context.get('mail_auto_subscribe_no_notify'):
            return
        if not self.env.registry.ready:
            return

        for record in self:
            model_description = self.env['ir.model']._get(record._name).display_name
            company = record.company_id.sudo() if 'company_id' in record else self.env.company
            values = {
                'access_link': record._notify_get_action_link('view'),
                'company': company,
                'model_description': model_description,
                'object': record,
            }
            assignation_msg = self.env['ir.qweb']._render(template, values, minimal_qcontext=True)
            assignation_msg = self.env['mail.render.mixin']._replace_local_links(assignation_msg)

            # To prevent automatic email notifications in sale order and invoice
            if (record._name == 'sale.order' or record._name == 'account.move' or record._name == 'stock.picking'):
                return

            record.message_notify(
                subject=_('You have been assigned to %s', record.display_name),
                body=assignation_msg,
                partner_ids=partner_ids,
                record_name=record.display_name,
                email_layout_xmlid='mail.mail_notification_layout',
                model_description=model_description,
            )


class MailActivity(models.Model):
    _inherit = 'mail.activity'


    # OVERRIDE
    def action_notify(self):
        if not self:
            return
        for activity in self:
            if activity.user_id.lang:
                # Send the notification in the assigned user's language
                activity = activity.with_context(lang=activity.user_id.lang)

            model_description = activity.env['ir.model']._get(activity.res_model).display_name
            body = activity.env['ir.qweb']._render(
                'mail.message_activity_assigned',
                {
                    'activity': activity,
                    'model_description': model_description,
                    'is_html_empty': is_html_empty,
                },
                minimal_qcontext=True
            )
            record = activity.env[activity.res_model].browse(activity.res_id)

            # To prevent automatic email notifications on creating activity
            if (record._name == 'sale.order' or record._name == 'account.move' or record._name == 'stock.picking'):
                return

            if activity.user_id:
                record.message_notify(
                    partner_ids=activity.user_id.partner_id.ids,
                    body=body,
                    record_name=activity.res_name,
                    model_description=model_description,
                    email_layout_xmlid='mail.mail_notification_layout',
                    subject=_('"%(activity_name)s: %(summary)s" assigned to you',
                              activity_name=activity.res_name,
                              summary=activity.summary or activity.activity_type_id.name),
                    subtitles=[_('Activity: %s', activity.activity_type_id.name),
                               _('Deadline: %s', activity.date_deadline.strftime(get_lang(activity.env).date_format))]
                )