from odoo import http
from odoo.http import request
import base64

class HousingApplication(http.Controller):


    @http.route('/housing-grant', type='http', auth='public', website=True)
    def housing_application(self, **kwargs):
        municipalities = request.env['res.municipality'].sudo().search([])
        provinces = request.env['res.province'].sudo().search([])
        departments = request.env['hr.department'].sudo().search([])
        cities = request.env['res.country.city'].sudo().search([])
        postal_cities = request.env['res.country.city'].sudo().search([])
        settlements = request.env['house.settlement'].sudo().search([])
        before_settlements = request.env['house.settlement'].sudo().search([])
        property_natures = request.env['property.nature'].sudo().search([])
        land_cities = request.env['res.country.city'].sudo().search([])
        land_ownerships = request.env['res.partner'].sudo().search([])
        return http.request.render('emergency_housing.housing_grant_application_form',{
            'provinces': provinces,
            'departments': departments,
            'municipalities': municipalities,
            'cities': cities,
            'postal_cities': postal_cities,
            'settlements': settlements,
            'before_settlements': before_settlements,
            'property_natures': property_natures,
            'land_ownerships': land_ownerships,
            'land_cities': land_cities,
                'data': {
                    'province': "",
                    'department': "",
                    'municipality': "",
                    'city': "",
                    'postal_city': "",
                    'mec_agreed': "",
                    'settlement': "",
                    'before_settlement': "",
                    'property_nature': "",
                    'consulted': "",
                    'consent_obtained': "",
                    'land_city': "",
                    'land_ownership': "",
                }
    })

    @http.route('/submit/housing', type='http', auth='public', website=True)
    def housing_submit_application(self, **kwargs):
        print(kwargs, 'aaaaa')

        vals = {
            'province_id': int(kwargs['province_id']) if kwargs['province_id'] else "",
            'department_id': int(kwargs['department_id']) if kwargs['department_id'] else "",
            'municipality_id': int(kwargs['municipality_id']) if kwargs['municipality_id'] else "",
            'date': kwargs['date'],
            'surname': kwargs['surname'],
            'designation': kwargs['designation'],
            'telephone': kwargs['telephone'],
            'fax_number': kwargs['fax_number'],
            'email': kwargs['email'],
            'street': kwargs['street'],
            'street2': kwargs['street2'],
            'postal_code': kwargs['postal_code'],
            # 'city_id': int(kwargs['city_id']) if kwargs['city_id'] else "",
            'physical_street': kwargs['physical_street'],
            'physical_street2': kwargs['physical_street2'],
            'physical_postal_code': kwargs['physical_postal_code'],
            'physical_city_id': int(kwargs['physical_city_id']) if kwargs['physical_city_id'] else "",
            'emergency_housing_situation': kwargs['emergency_housing_situation'],
            'location_and_cause': kwargs['location_and_cause'],
            'level_destitution': kwargs['level_destitution'],
            'nature_scope': kwargs['nature_scope'],
            'mec_agreed': kwargs['mec_agreed'] if kwargs['mec_agreed'] else "",
            # 'informed_disaster': kwargs['informed_disaster'] if kwargs['informed_disaster'] else "",
            'number_affected_person': kwargs['number_affected_person'],
            'income_profile': kwargs['income_profile'],
            'number_person_unemployed': kwargs['number_person_unemployed'],
            'reason_relocation': kwargs['reason_relocation'],
            'settlement_id': int(kwargs['settlement_id']) if kwargs['settlement_id'] else "",
            'before_settlement_id': int(kwargs['before_settlement_id']) if kwargs['before_settlement_id'] else "",
            'property_nature_id': int(kwargs['property_nature_id']) if kwargs['property_nature_id'] else "",
            'consulted': kwargs['consulted'] if kwargs['consulted'] else "",
            'consent_obtained': kwargs['consent_obtained'] if kwargs['consent_obtained'] else "",
            # 'land_city_id': int(kwargs['land_city_id']) if kwargs['land_city_id'] else "",
            'land_ownership_id': int(kwargs['land_ownership_id']) if kwargs['land_ownership_id'] else "",
            'land_availability_basis': kwargs['land_availability_basis'] if kwargs['land_availability_basis'] else "",
        }
        housing = request.env['housing.emergency'].sudo().create(vals)
        print(housing)
        # housing = ""
        if not housing:
            municipalities = request.env['res.municipality'].sudo().search([])
            provinces = request.env['res.province'].sudo().search([])
            departments = request.env['hr.department'].sudo().search([])
            cities = request.env['res.country.city'].sudo().search([])
            postal_cities = request.env['res.country.city'].sudo().search([])
            settlements = request.env['house.settlement'].sudo().search([])
            before_settlements = request.env['house.settlement'].sudo().search([])
            property_natures = request.env['property.nature'].sudo().search([])
            land_cities = request.env['res.country.city'].sudo().search([])
            land_ownerships = request.env['res.partner'].sudo().search([])
            kwargs['provinces'] = provinces
            kwargs['departments'] = departments
            kwargs['municipalities'] = municipalities
            kwargs['cities'] = cities
            kwargs['postal_cities'] = postal_cities
            kwargs['settlements'] = settlements
            kwargs['before_settlements'] = before_settlements
            kwargs['property_natures'] = property_natures
            kwargs['land_cities'] = land_cities
            kwargs['land_ownerships'] = land_ownerships
            kwargs['data'] = {
                'province': int(kwargs['province_id']) if kwargs['province_id'] else "",
                'department': int(kwargs['department_id']) if kwargs['department_id'] else "",
                'municipality': int(kwargs['municipality_id']) if kwargs['municipality_id'] else "",
                'city': int(kwargs['city_id']) if kwargs['city_id'] else "",
                'postal_city': int(kwargs['physical_city_id']) if kwargs['physical_city_id'] else "",
                'settlement': int(kwargs['settlement_id']) if kwargs['settlement_id'] else "",
                'before_settlement': int(kwargs['before_settlement_id']) if kwargs['before_settlement_id'] else "",
                'mec_agreed': kwargs['mec_agreed'] if kwargs['mec_agreed'] else "",
                # 'informed_disaster': kwargs['informed_disaster'] if kwargs['informed_disaster'] else "",
                'consulted': kwargs['consulted'] if kwargs['consulted'] else "",
                'property_nature': int(kwargs['property_nature_id']) if kwargs['property_nature_id'] else "",
                'consent_obtained': kwargs['consent_obtained'] if kwargs['consent_obtained'] else "",
                # 'land_city': int(kwargs['land_city_id']) if kwargs['land_city_id'] else "",
                'land_ownership': int(kwargs['land_ownership_id']) if kwargs['land_ownership_id'] else "",
                'land_availability_basis': kwargs['land_availability_basis'] if kwargs['land_availability_basis'] else "",

            }
            return http.request.render('emergency_housing.housing_grant_application_form', kwargs)
        else:
            application = housing
            application.sudo().portal_mark_submitted()
            return request.render('emergency_housing.thank_you_page',
                                  {'application': application})
            return {}