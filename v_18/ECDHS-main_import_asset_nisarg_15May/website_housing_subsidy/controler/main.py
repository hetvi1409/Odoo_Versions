from odoo import http
from odoo.http import request
import base64

class HousingSubsidy(http.Controller):
    @http.route('/housing-subsidy-application', type='http', auth='public', website=True)
    def HousingSubsidyApplication(self, **kwargs):
        races = request.env['res.race'].sudo().search([])
        country = request.env['res.country'].sudo().search([])
        district = request.env['res.region'].sudo().search([])
        return http.request.render(
            'website_housing_subsidy.housing_subsidy_application_form',{
        'races': races,
        'country': country,
        'district': district,
    })

    @http.route('/get/states', type='json', auth='public', csrf=False)
    def get_states(self, **kwargs):
        country_id = kwargs.get('country_id')

        if not country_id:
            return []

        states = request.env['res.country.state'].sudo().search([
            ('country_id', '=', int(country_id))
        ])
        return [{'id': state.id, 'name': state.name} for state in states]

    @http.route('/get/municipalities', type='json', auth='public', csrf=False)
    def get_municipalities(self, **kwargs):
        district_id = kwargs.get('district_id')

        if not district_id:
            return []

        municipalities = request.env['res.municipality'].sudo().search([
            ('region_id', '=', int(district_id))
        ])
        return [{'id': m.id, 'name': m.municipality} for m in municipalities]

    @http.route('/submit/beneficiary', type='http', auth="public",
                website=True, csrf=False)
    def submit_beneficiary_form(self, **post):
        uploaded_mrg_doc = False
        uploaded_identity_doc = False
        uploaded_identity_spouse_doc = False
        uploaded_divorce_doc = False
        uploaded_spouse_death_doc = False
        uploaded_disability_doc = False
        uploaded_proof_loan_doc = False
        uploaded_agreement_sale_doc = False
        uploaded_compact_agreement_doc = False
        uploaded_conveyencer_doc = False
        uploaded_building_contract_doc = False
        uploaded_proof_of_income_doc = False
        uploaded_residence_certificate_doc = False
        race_applicant = int(post.get('race_applicant')) if post.get(
            'race_applicant') else False
        race_spouse = int(post.get('race_spouse')) if post.get(
            'race_spouse') else False
        citizen_applicant = int(post.get('citizen_country_id')) if post.get(
            'citizen_country_id') else False
        country_id = int(post.get('country_id')) if post.get(
            'country_id') else False
        state_id = int(post.get('state_id')) if post.get(
            'state_id') else False
        district_id = int(post.get('district')) if post.get(
            'district') else False
        municipality_id = int(post.get('municipality_id')) if post.get(
            'municipality_id') else False
        is_disabled = post.get('disabled') == 'on'
        citizen = post.get('citizen') == 'on'
        uploaded_mrg_file = post.get('mrg_certificate')
        if uploaded_mrg_file:
            attachment_data = base64.b64encode(uploaded_mrg_file.read())
            uploaded_mrg_doc = request.env['ir.attachment'].sudo().create({
                'name': uploaded_mrg_file.filename,
                'datas': attachment_data,
                'res_model': 'housing.subsidy',
                'type': 'binary',
                'public': False,
            })
        uploaded_identity_file = post.get('identity_doc_self')
        if uploaded_identity_file:
            attachment_data = base64.b64encode(uploaded_identity_file.read())
            uploaded_identity_doc = request.env['ir.attachment'].sudo().create({
                'name': uploaded_identity_file.filename,
                'datas': attachment_data,
                'res_model': 'housing.subsidy',
                'type': 'binary',
                'public': False,
            })
        uploaded_identity_spouse_file = post.get('identity_doc_self')
        if uploaded_identity_spouse_file:
            attachment_data = base64.b64encode(uploaded_identity_spouse_file.read())
            uploaded_identity_spouse_doc = request.env['ir.attachment'].sudo().create(
                {
                    'name': uploaded_identity_spouse_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })
        uploaded_divorce_file = post.get('divorce_certificate')
        if uploaded_divorce_file:
            attachment_data = base64.b64encode(
                uploaded_divorce_file.read())
            uploaded_divorce_doc = request.env[
                'ir.attachment'].sudo().create(
                {
                    'name': uploaded_divorce_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })
        uploaded_spouse_death_file = post.get('spouse_death_certificate')
        if uploaded_spouse_death_file:
            attachment_data = base64.b64encode(
                uploaded_spouse_death_file.read())
            uploaded_spouse_death_doc = request.env[
                'ir.attachment'].sudo().create(
                {
                    'name': uploaded_spouse_death_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })
        uploaded_disability_file = post.get('proof_of_disability')
        if uploaded_disability_file:
            attachment_data = base64.b64encode(
                uploaded_disability_file.read())
            uploaded_disability_doc = request.env[
                'ir.attachment'].sudo().create(
                {
                    'name': uploaded_disability_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })

        uploaded_proof_loan_file = post.get('proof_of_loan')
        if uploaded_proof_loan_file:
            attachment_data = base64.b64encode(
                uploaded_proof_loan_file.read())
            uploaded_proof_loan_doc = request.env[
                'ir.attachment'].sudo().create(
                {
                    'name': uploaded_proof_loan_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })
        uploaded_agreement_sale_file = post.get('agreement_of_sale')
        if uploaded_agreement_sale_file:
            attachment_data = base64.b64encode(
                uploaded_agreement_sale_file.read())
            uploaded_agreement_sale_doc = request.env[
                'ir.attachment'].sudo().create(
                {
                    'name': uploaded_agreement_sale_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })

        uploaded_compact_agreement_file = post.get('compact_agreement')
        if uploaded_compact_agreement_file:
            attachment_data = base64.b64encode(
                uploaded_compact_agreement_file.read())
            uploaded_compact_agreement_doc = request.env[
                'ir.attachment'].sudo().create(
                {
                    'name': uploaded_compact_agreement_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })

        uploaded_conveyencer_file = post.get('agreement_with_conveyancer')
        if uploaded_conveyencer_file:
            attachment_data = base64.b64encode(
                uploaded_conveyencer_file.read())
            uploaded_conveyencer_doc = request.env[
                'ir.attachment'].sudo().create(
                {
                    'name': uploaded_conveyencer_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })

        uploaded_building_contract_file = post.get('building_contract_certificate')
        if uploaded_building_contract_file:
            attachment_data = base64.b64encode(
                uploaded_building_contract_file.read())
            uploaded_building_contract_doc = request.env[
                'ir.attachment'].sudo().create(
                {
                    'name': uploaded_building_contract_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })

        uploaded_proof_of_income_file = post.get(
            'proof_of_income_certificate')
        if uploaded_proof_of_income_file:
            attachment_data = base64.b64encode(
                uploaded_proof_of_income_file.read())
            uploaded_proof_of_income_doc = request.env[
                'ir.attachment'].sudo().create(
                {
                    'name': uploaded_proof_of_income_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })

        uploaded_residence_certificate_file = post.get(
            'residence_certificate')
        if uploaded_residence_certificate_file:
            attachment_data = base64.b64encode(
                uploaded_residence_certificate_file.read())
            uploaded_residence_certificate_doc = request.env[
                'ir.attachment'].sudo().create(
                {
                    'name': uploaded_residence_certificate_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'type': 'binary',
                    'public': False,
                })

        # Create main application
        subsidy = request.env['housing.subsidy'].sudo().create({
            'emergency_contact_name': post.get('emergency_contact_name'),
            'street': post.get('street'),
            'individual_reg_number': 'New',
            'street2': post.get('street2'),
            'zip': post.get('zip'),
            'city': post.get('city'),
            'telephone_number': post.get('telephone_number'),
            'married': post.get('married'),
            'hab_long_partner': post.get('hab_long_partner'),
            'widow_depend': post.get('widow_depend'),
            'divorced_with_dept': post.get('divorced_with_dept'),
            'single_depend': post.get('single_depend'),
            'applicant_surname': post.get('applicant_surname'),
            'spouse_surname': post.get('spouse_surname'),
            'applicant_maiden_surname': post.get('applicant_maiden_surname'),
            'spouse_maiden_surname': post.get('spouse_maiden_surname'),
            'applicant_full_name': post.get('applicant_full_name'),
            'spouse_full_name': post.get('spouse_full_name'),
            'identity_number': post.get('identity_number'),
            'identity_number_spouse': post.get('identity_number_spouse'),
            'applicant_gender': post.get('applicant_gender'),
            'spouse_gender': post.get('spouse_gender'),
            'race_applicant': race_applicant,
            'race_spouse': race_spouse,
            'country_id': country_id,
            'state_id': state_id,
            'disabled': is_disabled,
            'residential_address': post.get('residential_address'),
            'spouse_emp_details': post.get('applicant_emp_details'),
            'applicant_emp_details': post.get('spouse_emp_details'),
            'applicant_basic_income': post.get('applicant_basic_income'),
            'spouse_basic_income': post.get('spouse_basic_income'),
            'applicant_regular_period': post.get('applicant_allowances'),
            'spouse_regular_period': post.get('spouse_allowances'),
            'applicant_housing_allowance': post.get('applicant_housing_allowance'),
            'spouse_housing_allowance': post.get('spouse_housing_allowance'),
            'applicant_regular_financial': post.get('applicant_employer_obligation'),
            'spouse_regular_financial': post.get('spouse_employer_obligation'),
            'applicant_commission_received': post.get('applicant_commission'),
            'spouse_commission_received': post.get('spouse_commission'),
            'applicant_pension_disability': post.get('applicant_pension_grant'),
            'spouse_pension_disability': post.get('spouse_pension_grant'),
            'applicant_total': post.get('applicant_total'),
            'spouse_total': post.get('spouse_total'),
            'joint_total': post.get('joint_total'),
            'subsidy_amt': post.get('subsidy_amount'),
            'citizen': citizen,
            'citizen_country_id': citizen_applicant,
            'south_african_permit': post.get('residence_permit_number'),
            'date_permit': post.get('permit_issue_date') or False,
            'name_of_seller': post.get('seller_name'),
            'district_id': district_id,
            'municipality_id': municipality_id,
            'township': post.get('township'),
            'lot_number': post.get('lot_number'),
            'township_extension': post.get('township_extension'),
            'unit_number': post.get('unit_number'),
            'flat_name': post.get('flat_name'),
            'house': post.get('house'),
            'type_tenure': post.get('tenure'),
            'other_tenure': post.get('other_tenure'),
            'total_product_price': post.get('total_product_price'),
            'subsidy': post.get('subsidy'),
            'amt_home_loan': post.get('home_loan'),
            'emp_contribution': post.get('employer_contribution'),
            'own_contribution': post.get('own_cash_contribution'),
            'own_building': post.get('own_material_contribution'),
            'funding_total': post.get('funding_total'),
            'state': 'submitted',
            'mrg_certificate': uploaded_mrg_doc.id if uploaded_mrg_doc else False,
            'identity_doc_self': uploaded_identity_doc.id if uploaded_identity_doc else False,
            'identity_doc_spouse': uploaded_identity_spouse_doc.id if uploaded_identity_spouse_doc else False,
            'divorce_certificate': uploaded_divorce_doc.id if uploaded_divorce_doc else False,
            'spouse_death_certificate': uploaded_spouse_death_doc.id if uploaded_spouse_death_doc else False,
            'proof_of_disability': uploaded_disability_doc.id if uploaded_disability_doc else False,
            'proof_of_loan': uploaded_proof_loan_doc.id if uploaded_proof_loan_doc else False,
            'agreement_of_sale': uploaded_agreement_sale_doc.id if uploaded_agreement_sale_doc else False,
            'compact_agreement': uploaded_compact_agreement_doc.id if uploaded_compact_agreement_doc else False,
            'agreement_with_conveyancer': uploaded_conveyencer_doc.id if uploaded_conveyencer_doc else False,
            'building_contract_certificate': uploaded_building_contract_doc.id if uploaded_building_contract_doc else False,
            'proof_of_income_certificate': uploaded_proof_of_income_doc.id if uploaded_proof_of_income_doc else False,
            'residence_certificate': uploaded_residence_certificate_doc.id if uploaded_residence_certificate_doc else False,
        })

        # Save dependants
        for i in [1, 2]:
            if post.get(f'dependant_name_{i}'):
                request.env['dependant.details'].sudo().create({
                    'dependant_surname': post.get(f'dependant_name_{i}'),
                    'dependant_initials': post.get(f'dependant_initials_{i}'),
                    'dependant_relation': post.get(f'dependant_relation_{i}'),
                    'dependant_age': post.get(f'dependant_age_{i}'),
                    'dependant_gender': post.get(f'dependant_gender_{i}'),
                    'dependant_id': subsidy.id,
                })

        file_fields = [
            'mrg_certificate',
            'identity_doc_self',
            'identity_doc_spouse',
            'divorce_certificate',
            'spouse_death_certificate',
            'proof_of_disability',
            'proof_of_loan',
            'agreement_of_sale',
            'compact_agreement',
            'agreement_with_conveyancer',
            'building_contract_certificate',
            'proof_of_income_certificate',
            'residence_certificate',
        ]

        for field_name in file_fields:
            uploaded_file = request.httprequest.files.get(field_name)
            if uploaded_file:
                attachment_data = base64.b64encode(uploaded_file.read())
                request.env['ir.attachment'].sudo().create({
                    'name': uploaded_file.filename,
                    'datas': attachment_data,
                    'res_model': 'housing.subsidy',
                    'res_id': subsidy.id,
                    'type': 'binary',
                    'public': False,
                })

        return request.redirect('/thank-you/%s' % subsidy.id)

    @http.route('/thank-you/<int:app_id>', type='http', auth="public",
                website=True)
    def thank_you(self,app_id):
        application = request.env['housing.subsidy'].sudo().browse(app_id)
        return request.render('website_housing_subsidy.thank_you_page', {'application': application})