import base64

from odoo import http
from odoo.http import request


class WebsiteComplaint(http.Controller):
    @http.route('/complaint', type='http', auth='public', website=True)
    def complaint_form(self, **kwargs):
        Ticket = request.env['helpdesk.ticket'].sudo()

        team_id = kwargs.get('team_id')
        team = None
        if team_id:
            team = request.env['helpdesk.team'].sudo().browse(int(team_id))

        # Safely fetch selection values for 'region' and 'category'
        categories = Ticket._fields['category'].selection or []
        regions = request.env['res.municipality'].sudo().search([])

        return request.render('customer_care.complaint_form_template', {
            'categories': categories,
            'regions': regions,
            'team': team,
        })

    @http.route('/complaint/submit', type='http', auth='public', website=True, methods=['POST'])
    def submit_complaint(self, **kwargs):
        team_id = kwargs.get('team_id')
        existing_partner = request.env['res.partner'].sudo().search([
            ('email', '=', kwargs.get('email_from', '')),
        ], limit=1)
        if not existing_partner:
            existing_partner = request.env['res.partner'].sudo().create({
                'name': kwargs.get('name', ''),
                'phone': kwargs.get('contact_number', ''),
                'email': kwargs.get('email_from', ''),
            })
        ticket_vals = {
            'team_id':int(team_id) if team_id else request.env.ref('customer_care.customer_carehelpdesk_team').id,
            'name': kwargs.get('subject', ''),
            'enquirer_name': kwargs.get('name', ''),
            'enquirer_surname': kwargs.get('surname', ''),
            'id_number': kwargs.get('id_number', ''),
            'contact_number': kwargs.get('contact_number', ''),
            'email': kwargs.get('email_from', ''),
            'region': kwargs.get('region', False),
            'category': kwargs.get('category', False),
            'channel': 'website',
            'description': kwargs.get('description', ''),
            'partner_id': existing_partner.id,
            'partner_phone': existing_partner.phone or '',
            'email_cc': existing_partner.email or ''
        }
        ticket = request.env['helpdesk.ticket'].sudo().create(ticket_vals)

        # Handle attachments
        uploaded_files = request.httprequest.files.getlist('attachment')
        attachment_ids = []

        for file in uploaded_files:
            if file:
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': file.filename,
                    'res_model': 'helpdesk.ticket',
                    'res_id': ticket.id,
                    'type': 'binary',
                    'datas': base64.b64encode(file.read()),
                    'mimetype': file.content_type,
                })
                attachment_ids.append(attachment.id)

        # Link attachments to the ticket
        if attachment_ids:
            ticket.write({'attachment_ids': [(6, 0, attachment_ids)]})

        return request.redirect('/complaint/thankyou')

    @http.route('/complaint/thankyou', type='http', auth='public', website=True)
    def complaint_thankyou(self, **kwargs):
        return request.render('customer_care.complaint_thankyou_template')
