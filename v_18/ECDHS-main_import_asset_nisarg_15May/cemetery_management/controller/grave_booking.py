from odoo.http import request, Controller, route


class GraveBooking(Controller):

    @route('/grave-booking', auth='public', website=True)
    def grave_booking(self, **kwargs):
        data = {
            'interment_type': "",
            'attended_by': "",
            'municipality': request.env['municipality.municipality'].sudo().search([('company_id', '=', request.env.company.id)], limit=1).id,
            'cemetery': "",
            'section': "",
        }
        if request.env.user.sudo().id in request.env.ref(
                'cemetery_management.group_undertaken').sudo().users.ids:
            type = 'undertaker'
        else:
            type = 'general'

        return request.render(
            'cemetery_management.grave_booking_application_form', {
                'page': 'first',
                'municipalities': request.env[
                    'municipality.municipality'].sudo().search([]),
                'cemeteries': request.env['cemetery.cemetery'].sudo().search(
                    []),
                'sections': request.env['cemetery.section'].sudo().search([]),
                'user_type': type,
                'data': data
            })

    @route(['/grave-first/<int:booking>'],
           type='http', auth="public", website=True)
    def grave_previous_first_page(self, booking):
        """Previous page for the booking: first page"""
        booking = request.env[('grave.booking')].sudo().browse(int(booking))
        data = {
            'page': 'first',
            'data': {
                'interment_type': booking.interment_type,
                'attended_by': booking.attended_by,
                'municipality': int(booking.municipality_id.id),
                'cemetery': int(booking.cemetery_id.id),
                'section': int(booking.section_id.id),
            },
            'interment_type': booking.interment_type,
            'attended_by': booking.attended_by,
            'grave_number': booking.grave_number,
            'no_attendees': booking.no_attendees,
            'time_of_use': booking.time_of_use,
            'municipalities': request.env[
                'municipality.municipality'].sudo().search([]),
            'cemeteries': request.env['cemetery.cemetery'].sudo().search([]),
            'sections': request.env['cemetery.section'].sudo().search([]),
            'booking': booking.id,
            'field': booking.field,
            'row': booking.row,
            'category': booking.category,
            'user_type': booking.user_type,
            'other_specification': booking.other_specification,
        }
        return request.render(
            'cemetery_management.grave_booking_application_form', data)

    @route(['/grave-second/<int:booking>'],
           type='http', auth="public", website=True)
    def grave_previous_second_page(self, booking):
        """Previous page for the booking: second page"""
        booking = request.env[('grave.booking')].sudo().browse(int(booking))
        kwargs = {
            'page': 'second',
            'data': {
                'applicant_municipality': int(
                    booking.applicant_municipality_id.id),
                'province': int(booking.province_id.id),
                # 'state': int(booking.state_id.id),
                'country': int(booking.country_id.id),
            },
            'user_type': booking.user_type,
            'booking': booking.id,
            'applicant_name': booking.applicant_name,
            'applicant_email': booking.applicant_email,
            'applicant_phone': booking.applicant_phone,
            'street': booking.street,
            'street2': booking.street2,
            'city': booking.city,
            'zip_': booking.zip,
            'applicant_municipality_id': int(
                booking.applicant_municipality_id.id) if booking.applicant_municipality_id else None,
            'province_id': int(booking.province_id.id) if booking.province_id else None,
            # 'state_id': int(booking.state_id.id) if booking.state_id else None,
            'country_id': int(booking.country_id.id) if booking.country_id else None,
        }

        kwargs['lease_purchase_type'] = booking.type
        kwargs['applicant_municipalities'] = request.env[
            'municipality.municipality'].sudo().search([])
        kwargs['provinces'] = request.env[
            'province.province'].sudo().search([])
        # kwargs['states'] = request.env['res.country.state'].sudo().search(
        #     [])
        kwargs['countries'] = request.env['res.country'].sudo().search([])
        return request.render(
            'cemetery_management.grave_booking_application_form', kwargs)

    @route(['/grave-third/<int:booking>'],
           type='http', auth="public", website=True)
    def grave_previous_third_page(self, booking):
        """Previous page for the booking: third page"""

        booking = request.env[('grave.booking')].sudo().browse(int(booking))
        kwargs = {
            'page': 'third',
            'data': {
                'authorisation_municipality': int(
                    booking.authorisation_municipality_id.id) if booking.authorisation_municipality_id else None,
                'authorisation_province': int(
                    booking.authorisation_province_id.id) if booking.authorisation_province_id else None,
                # 'authorisation_state': int(
                    # booking.authorisation_state_id.id) if booking.authorisation_state_id else None,
                'authorisation_country': int(
                    booking.authorisation_country_id.id) if booking.authorisation_country_id else None,
            },
            'user_type': booking.user_type,
            'booking': booking.id,
            'authorisation_name': booking.applicant_name,
            'authorisation_email': booking.applicant_email,
            'authorisation_phone': booking.applicant_phone,
            'authorisation_street': booking.authorisation_street,
            'authorisation_street2': booking.authorisation_street2,
            'authorisation_city': booking.authorisation_city,
            'authorisation_zip': booking.authorisation_zip,
            'authorisation_municipality_id': int(
                booking.authorisation_municipality_id.id),
            'authorisation_province_id': int(booking.province_id.id),
            # 'authorisation_state_id': int(booking.authorisation_state_id.id),
            'authorisation_country_id': int(
                booking.authorisation_country_id.id),
        }

        kwargs['lease_purchase_type'] = booking.type
        kwargs['authorisation_municipalities'] = request.env[
            'municipality.municipality'].sudo().search([])
        kwargs['authorisation_provinces'] = request.env[
            'province.province'].sudo().search([])
        # kwargs['authorisation_states'] = request.env[
        #     'res.country.state'].sudo().search([])
        kwargs['authorisation_countries'] = request.env[
            'res.country'].sudo().search([])
        return request.render(
            'cemetery_management.grave_booking_application_form', kwargs)

    @route('/grave-submit', auth='public', website=True)
    def grave_submit(self, **kwargs):
        """For submit the forms,"""
        if kwargs['page'] == 'first':
            error = ""
            data = {
                'interment_type': "",
                'attended_by': "",
                'municipality': "",
                'cemetery': "",
                'section': "",
            }
            kwargs['municipalities'] = request.env[
                'municipality.municipality'].sudo().search([])
            kwargs['cemeteries'] = request.env[
                'cemetery.cemetery'].sudo().search([])
            kwargs['sections'] = request.env['cemetery.section'].sudo().search(
                [])
            if kwargs.get('interment_type'):
                data['interment_type'] = kwargs.get('interment_type')
                if kwargs.get('interment_type') == 'cremation':
                    if not kwargs.get('attended_by'):
                        error = "Please add the Attended by options"
                    else:
                        data['attended_by'] = kwargs.get('attended_by')
                    if kwargs.get('attended_by') == 'family':
                        if not kwargs.get('no_attendees'):
                            error = "Please add the no of attendees details"
                        else:
                            if not kwargs.get('no_attendees').isdigit():
                                error = "Number of attendees must be a number"
            if not kwargs.get('row'):
                error = "Please add the row"
            else:
                if not kwargs.get('row').isdigit():
                    error = "Please add the integer value for row"
            if not kwargs.get('category'):
                error = "Please add the category"
            if not kwargs.get('field'):
                error = "Please add the field"
            else:
                if not kwargs.get('field').isdigit():
                    error = "Please add the integer value for field"
            if not kwargs.get('section_id'):
                error = "Please add the cemetery section"
            if not kwargs.get('cemetery_id'):
                error = "Please add the cemetery"
            if not kwargs.get('municipality_id'):
                error = "Please add the municipality"
            if not kwargs.get('time_of_use'):
                error = "Please add the time of use"
            data['municipality'] = int(
                kwargs.get('municipality_id')) if kwargs.get(
                'municipality_id') else None
            data['cemetery'] = int(kwargs.get('cemetery_id')) if kwargs.get(
                'cemetery_id') else None
            data['section'] = int(kwargs.get('section_id')) if kwargs.get(
                'section_id') else None
            kwargs['data'] = data
            kwargs['error'] = error
            if error:
                return request.render(
                    'cemetery_management.grave_booking_application_form',
                    kwargs)
            else:
                if not kwargs.get('booking'):
                    booking = request.env['grave.booking'].sudo().create({
                        'interment_type': kwargs.get('interment_type'),
                        'company_id': request.env['municipality.municipality'].sudo().browse(int(kwargs.get('municipality_id'))).company_id.id,
                        'grave_number': kwargs.get('grave_number'),
                        'attended_by': kwargs.get('attended_by'),
                        'no_attendees': kwargs.get('no_attendees'),
                        'time_of_use': kwargs.get('time_of_use'),
                        'municipality_id': int(kwargs.get('municipality_id')),
                        'applicant_municipality_id': int(kwargs.get('municipality_id')),
                        'cemetery_id': int(kwargs.get('cemetery_id')),
                        'section_id': int(kwargs.get('section_id')),
                        'field': int(kwargs.get('field')),
                        'row': int(kwargs.get('row')),
                        'category': kwargs.get('category'),
                        'user_type': kwargs.get('user_type'),
                            'type': kwargs.get('lease_purchase_type'),
                        'other_specification': kwargs.get(
                            'other_specification'),
                    })
                else:
                    booking = (request.env['grave.booking'].sudo().browse(
                        int(kwargs.get('booking'))))
                    booking.write({
                        'type': kwargs.get('lease_purchase_type'),
                        'interment_type': kwargs.get('interment_type'),
                        'grave_number': kwargs.get('grave_number'),
                        'attended_by': kwargs.get('attended_by'),
                        'no_attendees': kwargs.get('no_attendees'),
                        'time_of_use': kwargs.get('time_of_use'),
                        'municipality_id': int(kwargs.get('municipality_id')),
                        'cemetery_id': int(kwargs.get('cemetery_id')),
                        'section_id': int(kwargs.get('section_id')),
                        'field': int(kwargs.get('field')),
                        'row': int(kwargs.get('row')),
                        'category': kwargs.get('category'),
                        'user_type': kwargs.get('user_type'),
                        'other_specification': kwargs.get(
                            'other_specification'),
                    })
                kwargs['page'] = "second"
                kwargs['booking'] = booking.id

                kwargs['applicant_municipalities'] = request.env[
                    'municipality.municipality'].sudo().search([])
                kwargs['provinces'] = request.env[
                    'province.province'].sudo().search([])
                # kwargs['states'] = request.env[
                #     'res.country.state'].sudo().search([])
                kwargs['countries'] = request.env['res.country'].sudo().search(
                    [])
                kwargs['applicant_name'] = booking.applicant_name
                kwargs['applicant_email'] = booking.applicant_email
                kwargs['applicant_phone'] = booking.applicant_phone
                kwargs['street'] = booking.street
                kwargs['street2'] = booking.street2
                kwargs['city'] = booking.city
                kwargs['zip_'] = booking.zip
                kwargs['lease_purchase_type'] = booking.type
                data = {
                    'applicant_municipality': int(
                        booking.applicant_municipality_id.id) if booking.applicant_municipality_id else None,
                    'province': int(
                        booking.province_id.id) if booking.province_id else None,
                    # 'state': int(
                    #     booking.state_id.id) if booking.state_id else None,
                    'country': int(
                        booking.country_id.id) if booking.country_id else None,
                }
                kwargs['data'] = data
                return request.render(
                    'cemetery_management.grave_booking_application_form',
                    kwargs)
        if kwargs.get('page') == 'second':
            error = ""
            kwargs['page'] = 'second'
            kwargs['applicant_municipalities'] = request.env[
                'municipality.municipality'].sudo().search([])
            kwargs['provinces'] = request.env[
                'province.province'].sudo().search([])
            # kwargs['states'] = request.env['res.country.state'].sudo().search(
            #     [])
            kwargs['countries'] = request.env['res.country'].sudo().search([])
            data = {
                'applicant_municipality': int(
                    kwargs.get('applicant_municipality_id')) if kwargs.get(
                    'applicant_municipality_id') else None,
                'province': int(kwargs.get('province_id')) if kwargs.get(
                    'province_id') else None,
                # 'state': int(kwargs.get('state_id')) if kwargs.get(
                #     'state_id') else None,
                'country': int(kwargs.get('country_id')) if kwargs.get(
                    'country_id') else None,
            }
            kwargs['data'] = data

            booking = request.env['grave.booking'].sudo().browse(
                int(kwargs.get('booking')))
            if not kwargs.get('city'):
                error = "Please add the city"
            if kwargs.get('zip_') and len(kwargs.get('zip_')) != 4:
                error = "Zip must be in 4 digits"
            if not kwargs.get('street'):
                error = "Please add the street"
            if not kwargs.get('applicant_phone'):
                error = "Please add the phone"
            if not kwargs.get('applicant_phone'):
                error = "Please add the phone"
            if not kwargs.get('applicant_email'):
                error = "Please add the email"
            if not kwargs.get('country_id'):
                error = "Please add the country"

            if not kwargs.get('country_id'):
                error = "Please add the country"
            if not kwargs.get('applicant_municipality_id'):
                error = "Please add the muncipality"
            if error:
                kwargs['error'] = error
                kwargs['lease_purchase_type'] = booking.type
                return request.render(
                    'cemetery_management.grave_booking_application_form',
                    kwargs)
            else:
                booking.sudo().write({
                    'applicant_name': kwargs.get('applicant_name'),
                    'applicant_email': kwargs.get('applicant_email'),
                    'applicant_phone': kwargs.get('applicant_phone'),
                    'street': kwargs.get('street'),
                    'street2': kwargs.get('street2'),
                    'city': kwargs.get('city'),
                    'zip': kwargs.get('zip_'),
                    'applicant_municipality_id': int(
                        kwargs.get('applicant_municipality_id')) if kwargs.get('applicant_municipality_id') else None,
                    'province_id': int(kwargs.get('province_id')) if kwargs.get('province_id') else None,
                    # 'state_id': int(kwargs.get('state_id')) if kwargs.get('state_id') else None,
                    'country_id': int(kwargs.get('country_id')) if kwargs.get('country_id') else None,
                })
                kwargs['page'] = 'third'
                kwargs['authorisation_name'] = booking.authorisation_name
                kwargs['authorisation_email'] = booking.authorisation_email
                kwargs['authorisation_phone'] = booking.authorisation_phone
                kwargs['authorisation_street'] = booking.authorisation_street
                kwargs['authorisation_street2'] = booking.authorisation_street2
                kwargs['authorisation_city'] = booking.authorisation_city
                kwargs['authorisation_zip'] = booking.authorisation_zip
                kwargs['authorisation_municipalities'] = request.env[
                    'municipality.municipality'].sudo().search([])
                kwargs['authorisation_provinces'] = request.env[
                    'province.province'].sudo().search([])
                # kwargs['authorisation_states'] = request.env[
                #     'res.country.state'].sudo().search([])
                kwargs['authorisation_countries'] = request.env[
                    'res.country'].sudo().search([])
                kwargs['lease_purchase_type'] = booking.type
                data = {
                    'authorisation_municipality': int(
                        booking.authorisation_municipality_id.id) if booking.authorisation_municipality_id else None,
                    'authorisation_province': int(
                        booking.authorisation_province_id.id) if booking.authorisation_province_id else None,
                    # 'authorisation_state': int(
                    #     booking.authorisation_state_id.id) if booking.authorisation_state_id else None,
                    'authorisation_country': int(
                        booking.authorisation_country_id.id) if booking.authorisation_country_id else None,
                }
                kwargs['data'] = data
                return request.render(
                    'cemetery_management.grave_booking_application_form',
                    kwargs)
        if kwargs.get('page') == 'third':
            error = ""
            data = {
                'authorisation_municipality': int(
                    kwargs['authorisation_municipality_id']) if kwargs[
                    'authorisation_municipality_id'] else None,
                'authorisation_province': int(
                    kwargs['authorisation_province_id']) if kwargs[
                    'authorisation_province_id'] else None,
                # 'authorisation_state': int(kwargs['authorisation_state_id']) if
                # kwargs['authorisation_state_id'] else None,
                'authorisation_country': int(
                    kwargs['authorisation_country_id']) if kwargs[
                    'authorisation_country_id'] else None,
            }
            kwargs['authorisation_municipalities'] = request.env[
                'municipality.municipality'].sudo().search([])
            kwargs['authorisation_provinces'] = request.env[
                'province.province'].sudo().search([])
            # kwargs['authorisation_states'] = request.env[
            #     'res.country.state'].sudo().search(
            #     [])
            kwargs['authorisation_countries'] = request.env[
                'res.country'].sudo().search([])

            kwargs['data'] = data
            if not kwargs.get('authorisation_city'):
                error = "Please add the city"
            if kwargs.get('authorisation_zip') and len(kwargs.get('authorisation_zip')) != 4:
                error = "Zip must be in 4 digits"
            if not kwargs.get('authorisation_street'):
                error = "Please add the street"
            if not kwargs.get('authorisation_phone'):
                error = "Please add the phone"
            if not kwargs.get('authorisation_email'):
                error = "Please add the email"
            if error:
                kwargs['error'] = error

                booking = request.env['grave.booking'].sudo().browse(
                    int(kwargs.get('booking')))

                kwargs['lease_purchase_type'] = booking.type
                return request.render(
                    'cemetery_management.grave_booking_application_form',
                    kwargs)
            else:
                booking = request.env['grave.booking'].sudo().browse(
                    int(kwargs.get('booking')))

                kwargs['lease_purchase_type'] = booking.type
                booking.sudo().write({
                    'authorisation_name': kwargs.get('authorisation_name'),
                    'authorisation_email': kwargs.get('authorisation_email'),
                    'authorisation_phone': kwargs.get('authorisation_phone'),
                    'authorisation_street': kwargs.get('authorisation_street'),
                    'authorisation_street2': kwargs.get(
                        'authorisation_street2'),
                    'authorisation_zip': kwargs.get('authorisation_zip'),
                    'authorisation_city': kwargs.get('authorisation_city'),
                    # 'authorisation_state_id': int(
                    #     kwargs.get('authorisation_state_id')) if kwargs.get(
                    #     'authorisation_state_id') else None,
                    'authorisation_country_id': int(
                        kwargs.get('authorisation_country_id')) if kwargs.get(
                        'authorisation_country_id') else None,
                    'authorisation_province_id': int(
                        kwargs.get('authorisation_province_id')) if kwargs.get(
                        'authorisation_province_id') else None,
                    'authorisation_municipality_id': int(kwargs.get(
                        'authorisation_municipality_id')) if kwargs.get(
                        'authorisation_municipality_id') else None,
                })

                kwargs['lease_purchase_type'] = booking.type
                kwargs['page'] = 'fourth'
                kwargs['municipalities_1'] = request.env[
                    'municipality.municipality'].sudo().search([])
                kwargs['provinces_1'] = request.env[
                    'province.province'].sudo().search([])
                # kwargs['states_1'] = request.env[
                #     'res.country.state'].sudo().search([])
                kwargs['countries_1'] = request.env[
                    'res.country'].sudo().search([])
                data = {
                    'municipality_1': "",
                    'province_1': "",
                    # 'state_1': "",
                    'country_1': "",
                }
                kwargs['data'] = data
                return request.render(
                    'cemetery_management.grave_booking_application_form',
                    kwargs)
        if kwargs.get('page') == 'fourth':
            booking = request.env['grave.booking'].sudo().browse(int(kwargs['booking']))
            booking.action_submit()
            return request.render(
                'cemetery_management.grave_application_form_completed',
                kwargs)

