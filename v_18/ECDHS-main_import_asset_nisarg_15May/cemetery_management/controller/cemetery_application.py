import base64

from odoo.http import request, Controller, route


class CemeteryApplication(Controller):

    @route('/cemetery-application', auth='user', website=True)
    def cemetery_application(self, **kwargs):
        if request.env.user.id in request.env.ref('cemetery_management.group_undertaken').sudo().users.ids:
            default_country = request.env['res.country'].sudo().search([('name', '=', 'South Africa')], limit=1)
            default_province = request.env['province.province'].sudo().search([('name', '=', 'KwaZulu-Natal')], limit=1)
            return request.render('cemetery_management.cemetery_application_form', {
                'page': 'first',
                'death_provinces': request.env['province.province'].sudo().search([]),
                'burial_provinces': request.env['province.province'].sudo().search([]),
                'municipalities': request.env['municipality.municipality'].sudo().search([]),
                'provinces': request.env['province.province'].sudo().search([]),
                'countries': request.env['res.country'].sudo().search([]),
                'cause_of_death_id': request.env['cause.death'].sudo().search([]),
                'data': {
                    'country': default_country.id if default_country else None,
                    'province': default_province.id if default_province else None
                },

            })

        return request.render('cemetery_management.cemetery_application_form_not_allowed')

    @route(
        ['/previous-first-page/<model("cemetery.application"):application>'],
        type='http', auth="public", website=True)
    def previous_first_page(self, application):
        """Previous page for the applications"""
        undertaker = request.env['undertaker.undertaker'].sudo().search([])
        data = {
            'page': 'first',
            'undertaker': undertaker,
            'undertaker_id': application.undertaker_id.id,
            'under_taker_id': application.undertaker_id.id,
            'interment_type': application.interment_type,
            'surname': application.surname,
            'application': application.id,
            'forenames': application.forenames,
            'persal_no': application.persal_no,
            'undertaker_id_number': application.undertaker_id_number,
            'designation_number': application.designation_number
        }
        return request.render('cemetery_management.cemetery_application_form', data)

    @route(
        ['/previous-second-page/<model("cemetery.application"):application>'],
        type='http', auth="public", website=True)
    def previous_second_page(self, application):
        """Previous page for the applications"""
        undertaker = request.env.ref(
            'cemetery_management.group_undertaken').sudo().users
        if application.is_deceased:
            is_deceased = "yes"
        else:
            is_deceased = 'no'
        data = {
            'page': 'second',
            'cemeteries': request.env['cemetery.cemetery'].sudo().sudo().search([]),
            'cemeteries_section': request.env['cemetery.section'].sudo().search([]),
            'graves': request.env['grave.grave'].sudo().search([]),
            'application': application.id,
            'serial_number': application.serial_number,
            'barcode_number': application.barcode_number,
            'is_deceased': is_deceased,
            'types': application.interment_type,
            'data': {
                'cemetery': application.cemetery_id.id,
                'section': application.section_id.id,
                'graves': application.grave_id.id,
            }
        }
        return request.render('cemetery_management.cemetery_application_form', data)

    @route(
        ['/previous-third-page/<model("cemetery.application"):application>'],
        type='http', auth="public", website=True)
    def previous_third_page(self, application):
        """Previous page for the applications"""
        undertaker = request.env.ref(
            'cemetery_management.group_undertaken').sudo().users
        if application.foreigner:
            foreigner = "yes"
        else:
            foreigner = 'no'

        data = {
            'page': 'third',
            'application': application.id,
            'death_provinces': request.env['province.province'].sudo().search([]),
            'burial_provinces': request.env['province.province'].sudo().search([]),
            'municipalities': request.env['municipality.municipality'].sudo().search([]),
            'provinces': request.env['province.province'].sudo().search([]),
            'countries': request.env['province.province'].sudo().search([]),
            'id_number': application.id_number,
            'deceased_firstname': application.deceased_firstname,
            'date_of_birth': application.date_of_birth,
            'date_of_death': application.date_of_death,
            'foreigner': foreigner,
            'passport_number': application.passport_number,
            'deceased_surname': application.deceased_surname,
            'street': application.street,
            'street2': application.street2,
            'city': application.city,
            'zip_': application.zip,
            'place_of_death': application.place_of_death,
            'place_of_burial': application.place_of_burial,
            'death_province_id': application.death_province_id,
            'religion': application.religion,
            'burial_province_id': application.burial_province_id,
            'gender': application.gender,
            'deceased_preferred_name': application.deceased_preferred_name,
            'data': {
                'death_province': int(application.death_province_id.id),
                'burial_province': int(application.burial_province_id.id),
                'municipality': int(application.municipality_id.id),
                'province': int(application.province_id.id),
                'country': int(application.country_id.id),
                'gender': application.gender,
            }
        }
        return request.render('cemetery_management.cemetery_application_form', data)

    @route('/cemetery-submit', auth='user', website=True, type='http')
    def cemetery_submit(self, **kwargs):
        error = ""

        if kwargs.get('page') == 'first':
            data = {
                'death_province': "",
                'burial_province': "",
                'graves': "",
                'municipality': "",
                'province': "",
                'country': "",
                'gender': "",
                'cause_of_death_id': "",
            }

            # Validation and field conversions
            if kwargs.get('death_province_id') and kwargs.get('death_province_id').isdigit():
                data['death_province'] = int(kwargs.get('death_province_id'))
            if kwargs.get('burial_province_id'):
                data['burial_province'] = int(kwargs.get('burial_province_id'))
            if kwargs.get('municipality_id'):
                data['municipality'] = int(kwargs.get('municipality_id'))
            if kwargs.get('province_id'):
                data['province'] = int(kwargs.get('province_id'))
            if kwargs.get('country_id'):
                data['country'] = int(kwargs.get('country_id'))
            if kwargs.get('gender'):
                data['gender'] = kwargs.get('gender')

            # Validation messages
            error = None
            foreigner = False
            if 'foreigner' not in kwargs:
                error = "Please select the foreigner details"
            else:
                foreigner = kwargs.get('foreigner') == 'yes'

            if not kwargs.get('place_of_death'):
                error = "Please add the place of death"
            elif not kwargs.get('place_of_burial'):
                error = "Please add the place of burial"
            elif not kwargs.get('deceased_surname'):
                error = "Please add the surname of deceased person"
            elif foreigner:
                passport_number = kwargs.get('passport_number', '')
            elif not foreigner:
                id_number = kwargs.get('id_number', '')
                if not id_number or len(id_number) != 13:
                    error = "The ID Number must be 13 digits"
            elif not kwargs.get('country_id'):
                error = "Please add the country"
            elif not kwargs.get('province_id'):
                error = "Please add the province"
            elif not kwargs.get('municipality_id'):
                error = "Please add the municipality"
            elif not kwargs.get('deceased_firstname'):
                error = "Please add the First name"

            # Dropdown options
            kwargs.update({
                'death_provinces': request.env['province.province'].sudo().search([]),
                'burial_provinces': request.env['province.province'].sudo().search([]),
                'municipalities': request.env['municipality.municipality'].sudo().search([]),
                'provinces': request.env['province.province'].sudo().search([]),
                'countries': request.env['res.country'].search([]),
                'data': data
            })
            # If there is a validation error
            if error:
                kwargs['error'] = error
                return request.render('cemetery_management.cemetery_application_form', kwargs)
            # Values to create/update
            vals = {
                'id_number': kwargs.get('id_number'),
                'date_of_birth': kwargs.get('date_of_birth'),
                'date_of_death': kwargs.get('date_of_death'),
                'foreigner': foreigner,
                'passport_number': kwargs.get('passport_number'),
                'deceased_surname': kwargs.get('deceased_surname'),
                'deceased_firstname': kwargs.get('deceased_firstname'),
                'street': kwargs.get('street'),
                'street2': kwargs.get('street2'),
                'zip': kwargs.get('zip_'),
                'city': kwargs.get('city'),
                'religion': kwargs.get('religion'),
                'deceased_preferred_name': kwargs.get('deceased_preferred_name'),
                'municipality_id': int(kwargs.get('municipality_id')) if kwargs.get('municipality_id') else None,
                'province_id': int(kwargs.get('province_id')) if kwargs.get('province_id') else None,
                'country_id': int(kwargs.get('country_id')) if kwargs.get('country_id') else None,
                'place_of_death': kwargs.get('place_of_death'),
                'gender': kwargs.get('gender'),
                'place_of_burial': kwargs.get('place_of_burial'),
                'death_province_id': int(kwargs.get('death_province_id')),
                'burial_province_id': int(kwargs.get('burial_province_id')),
                'is_deceased': False,
                'cause_of_death_id': int(kwargs.get('cause_of_death_id')),
                'state':'submitted'
            }

            # Create or update
            if kwargs.get('application'):
                application = request.env['cemetery.application'].sudo().browse(int(kwargs['application']))
                application.sudo().write(vals)
            else:
                application = request.env['cemetery.application'].sudo().create(vals)
                kwargs['application'] = application.id

            # Update for second page
            kwargs.update({
                'types': application.interment_type,
                'page': 'second',
                'cemeteries': request.env['cemetery.cemetery'].sudo().search([]),
                'cemeteries_section': request.env['cemetery.section'].sudo().search([]),
                'graves': request.env['grave.grave'].sudo().search([]),
                'cemetery_id': application.cemetery_id.id if application.cemetery_id else "",
                'section_id': application.section_id.id if application.section_id else "",
                'grave_id': application.grave_id.id if application.grave_id else "",
            })
            return request.render('cemetery_management.cemetery_application_form', kwargs)

        elif kwargs.get('page') == 'second':
            error = None
            errors = []
            is_deceased_value = kwargs.get('is_deceased')
            is_deceased = is_deceased_value == 'yes'

            application = request.env['cemetery.application'].sudo().browse(int(kwargs['application']))

            data = {
                'cemetery': int(kwargs.get('cemetery_id')) if kwargs.get('cemetery_id') else "",
                'section': int(kwargs.get('section_id')) if kwargs.get('section_id') else "",
                'graves': int(kwargs.get('grave_id')) if kwargs.get('grave_id') else "",
            }

            if not is_deceased_value:
                errors.append("Please select the deceased details")

            if application.type == 'burial':
                if not kwargs.get('cemetery_id'):
                    errors.append("Please select a cemetery")
                if not kwargs.get('section_id'):
                    errors.append("Please select a cemetery section")
                if not kwargs.get('grave_id'):
                    errors.append("Please select a grave")

            if errors:
                kwargs.update({
                    'error': " | ".join(errors),
                    'cemeteries': request.env['cemetery.cemetery'].sudo().search([]),
                    'cemeteries_section': request.env['cemetery.section'].sudo().search([]),
                    'graves': request.env['grave.grave'].sudo().search([]),
                    'data': data
                })
                return request.render('cemetery_management.cemetery_application_form', kwargs)

            application.sudo().write({
                'interment_type': kwargs.get('interment_type'),
                'serial_number': kwargs.get('serial_number'),
                'barcode_number': kwargs.get('barcode_number'),
                'cemetery_id': int(kwargs.get('cemetery_id')) if kwargs.get('cemetery_id') else None,
                'section_id': int(kwargs.get('section_id')) if kwargs.get('section_id') else None,
                'grave_id': int(kwargs.get('grave_id')) if kwargs.get('grave_id') else None,
                'is_deceased': is_deceased
            })

            # Prepare for next page
            data.update({
                'death_province': int(application.death_province_id.id) if application.death_province_id else "",
                'burial_province': int(application.burial_province_id.id) if application.burial_province_id else "",
                'municipality': int(application.municipality_id.id) if application.municipality_id else "",
                'province': int(application.province_id.id) if application.province_id else "",
                'country': int(application.country_id.id) if application.country_id else "",
                'gender': application.gender,
            })

            kwargs.update({
                'page': 'fifth',
                'data': data,
                'death_provinces': request.env['province.province'].sudo().search([]),
                'burial_provinces': request.env['province.province'].sudo().search([]),
                'municipalities': request.env['municipality.municipality'].sudo().search([]),
                'provinces': request.env['province.province'].sudo().search([]),
                'countries': request.env['res.country'].search([]),
                'place_of_death': application.place_of_death,
                'place_of_burial': application.place_of_burial,
                'deceased_surname': application.deceased_surname,
                'deceased_firstname': application.deceased_firstname,
                'gender': application.gender,
                'deceased_preferred_name': application.deceased_preferred_name,
                'street': application.street,
                'street2': application.street2,
                'city': application.city,
                'zip_': application.zip,
                'religion': application.religion,
                'foreigner': "yes" if application.foreigner else "no",
                'passport_number': application.passport_number,
                'id_number': application.id_number,
                'date_of_birth': application.date_of_birth,
                'date_of_death': application.date_of_death
            })
            return request.render('cemetery_management.cemetery_application_form', kwargs)


        elif kwargs.get('page') == 'fifth':
            files = request.httprequest.files
            application_id = int(kwargs.get('application'))
            application = request.env['cemetery.application'].sudo().browse(application_id)

            def file_to_binary(field_name):
                file = files.get(field_name)
                return base64.b64encode(file.read()) if file else False

            application.write({
                'burial_order': file_to_binary('burial_order'),
                'deceased_id': file_to_binary('deceased_id'),
                'next_of_kin_id': file_to_binary('next_of_kin_id'),
                'death_certificate': file_to_binary('death_certificate'),
            })

            application_vals = {
                'name': application.name
            }
            return request.render('cemetery_management.cemetery_application_form_completed', application_vals)
