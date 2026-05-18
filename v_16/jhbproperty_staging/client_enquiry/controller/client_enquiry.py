import base64
from odoo import http, _
from odoo.http import request


class PropertyEnquiry(http.Controller):

    @http.route('/enquiry', auth='user', website=True, csrf=False)
    def enquiry(self, **kw):
        """Enquiry """
        customer = request.env.user.partner_id
        data = {
            'surname': customer.name,
            'first_name': customer.name,
            'cell_phone': customer.phone,
            'email': customer.email,
        }
        return http.request.render(
            'client_enquiry.enquiry_form_1', data)

    @http.route('/enquiry/submit', auth='user', website=True, csrf=False)
    def enquiry_submit(self, **kw):
        """Enquiry Submit"""
        if not kw.get('stand_number'):
            kw['error'] = "Please Add the Stand Number/ Portion number"
            return http.request.render('client_enquiry.enquiry_form', kw)
        enquiry = request.env['client.enquiry'].sudo().browse(int(kw.get('enquiry')))
        enquiry.sudo().write({
            'stand_number': kw['stand_number'],
            'township': kw['township'],
            'entire_property': kw['entire_property'],
        })
        return http.request.render(
            'client_enquiry.enquiry_form_submit', {'enquiry': enquiry.id})

    @http.route('/enquiry/submit-1', auth='user', website=True, csrf=False)
    def enquiry_submit_1(self, **kw):
        """Enquiry Submit"""
        if not kw['proposed_use']:
            kw['error'] = 'Please add the proposed use'
            return http.request.render(
                'client_enquiry.enquiry_form_1', kw)
        if not kw['surname']:
            kw['error'] = 'Please Add the Surname'
            return http.request.render(
                'client_enquiry.enquiry_form_1', kw)
        if not kw['title']:
            kw['error'] = 'Please Add the Title'
            return http.request.render(
                'client_enquiry.enquiry_form_1', kw)
        if not kw['first_name']:
            kw['error'] = 'Please Add the First name'
            return http.request.render(
                'client_enquiry.enquiry_form_1', kw)
        if not kw['cell_phone']:
            kw['error'] = 'Please Add the Cell Phone number'
            return http.request.render(
                'client_enquiry.enquiry_form_1', kw)

        enquiry = request.env['client.enquiry'].sudo().create({
            'partner_id': request.env.user.partner_id.id,
            'type': kw['type'],
            'proposed_use': kw['proposed_use'],
            'surname': kw['surname'],
            'title': kw['title'],
            'team_id': request.env.ref('client_enquiry.helpdesk_team_website').id,
            'first_name': kw['first_name'],
            'cell_phone': kw['cell_phone'],
            'email': kw['email'],
            'registration_number': kw['registration'],
            'street': kw['street'],
            'street2': kw['street_1'],
            'city': kw['city'],
            'zip': kw['zip_code']
        })
        return http.request.render(
            'client_enquiry.enquiry_form', {'enquiry': enquiry.id})

    @http.route('/assessment-evaluation/<int:id>', auth='user', website=True, csrf=False)
    def assessment_evaluation(self, **kw):
        """To write the circulation report"""
        assessment = request.env['enquiry.assessment'].sudo().browse(
            int(kw.get('id')))
        data = {
            'enquiry': kw.get('id'),
            'name': assessment.name,
        }
        return http.request.render(
            'client_enquiry.assessment_circulation', data)

    @http.route('/assessment/circulation_property', auth='user', website=True, csrf=False)
    def assessment_circulation(self, **kw):
        """To write the circulation report"""
        assessment = request.env['enquiry.assessment'].sudo().browse(int(kw.get('enquiry')))
        attached_files = request.httprequest.files.getlist('file[]')
        attachments = []
        circulation_assessment = request.env['circulation.assessment'].sudo().create({
            'assessment_id': assessment.id,
            'user_id': request.uid,
            'group_ids': request.env['res.users'].sudo().browse(request.uid).sudo().groups_id
        })
        documents = []
        for rec in attached_files:
            if rec.filename == '':
                kw['error'] = "You need to upload the documents for this application"
                return http.request.render(
                    'client_enquiry.assessment_circulation', kw)
            else:
                assessment_folder = request.env.ref('client_enquiry.document_enquiry')
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': rec.filename,
                    'datas': base64.b64encode(rec.read()) if kw.get(
                        'file[]') else False,
                    'res_id': assessment.id,
                    'res_model': assessment._name
                })
                circulation_assessment.sudo().attachment_ids = [(4, attachment.id)]
                if assessment.property_id.sudo().region_id:
                    region = request.env['documents.folder'].sudo().search([
                        (
                        'name', '=', assessment.property_id.sudo().region_id.name),
                        ('parent_folder_id', '=', assessment_folder.id)
                    ])
                    if not region:
                        region = request.env['documents.folder'].sudo().create({
                            'name': assessment.property_id.sudo().region_id.name,
                            'parent_folder_id': assessment_folder.id
                        })
                else:
                    region = request.env['documents.folder'].sudo().search([
                        ('name', '=', "Undefined Region"),
                        ('parent_folder_id', '=', assessment_folder.id)
                    ])
                    if not region:
                        region = request.env['documents.folder'].sudo().create({
                            'name': 'Undefined Region',
                            'parent_folder_id': assessment_folder.id
                        })
                jmc = request.env['documents.folder'].sudo().search([
                    ('name', '=', assessment.jmc_number),
                    ('parent_folder_id', '=', region.id)
                ])
                if not jmc:
                    jmc = request.env['documents.folder'].sudo().create({
                        'name': assessment.jmc_number,
                        'parent_folder_id': region.id,
                    })
                enquiry_folder = request.env['documents.folder'].sudo().search([
                    ('name', '=', assessment.name),
                    ('parent_folder_id', '=', jmc.id)
                ])
                if not enquiry_folder:
                    enquiry_folder = request.env['documents.folder'].create({
                        'name': assessment.name,
                        'parent_folder_id': jmc.id,
                    })
                circulation = request.env['documents.folder'].sudo().search([
                    ('name', '=', 'Circulation for Comment'),
                    ('parent_folder_id', '=', enquiry_folder.id)
                ])
                if not circulation:
                    circulation = request.env['documents.folder'].sudo().create({
                        'name': 'Circulation for Comment',
                        'parent_folder_id': enquiry_folder.id,
                    })
                feedback = request.env['documents.folder'].sudo().search([
                    ('name', '=', 'Feedback on Comments'),
                    ('parent_folder_id', '=', circulation.id)
                ])
                if not feedback:
                    feedback = request.env['documents.folder'].sudo().create({
                        'name': 'Feedback on Comments',
                        'parent_folder_id': circulation.id,
                    })
                document = request.env['documents.document'].sudo().create({
                    'name': attachment.name,
                    'attachment_id': attachment.id,
                    'folder_id': feedback.id
                })
                documents.append(document.id)
                assessment.sudo().write({
                    'circulation_documents_ids': [(4, document.id)]
                })
                assessment.sudo().circulation_folder_id = feedback.id
        return http.request.render(
            'client_enquiry.assessment_circulation_submit')
