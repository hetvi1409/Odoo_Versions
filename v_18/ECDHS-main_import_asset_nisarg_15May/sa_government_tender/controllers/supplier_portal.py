# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
import logging
import re
from markupsafe import escape

_logger = logging.getLogger(__name__)


class SupplierRegistrationController(http.Controller):
    """Controller for supplier self-registration"""

    def _validate_email(self, email):
        """Validate email format"""
        if not email:
            return False
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _sanitize_input(self, value, max_length=200):
        """Sanitize string input"""
        if not value:
            return ''
        value = str(value).strip()
        if len(value) > max_length:
            value = value[:max_length]
        return value

    def _validate_phone(self, phone):
        """Basic phone validation"""
        if not phone:
            return True  # Phone is optional in some contexts
        # Remove common separators
        phone = re.sub(r'[\s\-\(\)\+]', '', phone)
        # Check if remaining chars are digits and reasonable length
        return phone.isdigit() and 7 <= len(phone) <= 15

    @http.route(['/supplier/register'], type='http', auth='public', website=True)
    def supplier_registration_form(self, **kwargs):
        """Display supplier registration form"""
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        # Check if user is logged in and already a supplier
        is_existing_supplier = False
        if request.env.user and not request.env.user._is_public():
            partner = request.env.user.partner_id
            if partner and partner.supplier_rank > 0:
                is_existing_supplier = True
                return request.render('sa_government_tender.supplier_already_registered', {
                    'partner': partner,
                    'page_name': 'supplier_registration',
                })

        return request.render('sa_government_tender.supplier_registration_form', {
            'countries': countries,
            'states': states,
            'page_name': 'supplier_registration',
        })

    @http.route(['/supplier/register/submit'], type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def supplier_registration_submit(self, **post):
        """Process supplier registration"""
        # Validate required fields
        required_fields = [
            'company_name', 'email', 'phone', 'street', 'city',
            'zip', 'country_id'
        ]

        errors = []
        for field in required_fields:
            if not post.get(field):
                errors.append(f"The field '{field.replace('_', ' ').title()}' is required.")

        if errors:
            return request.render('sa_government_tender.supplier_registration_error', {
                'errors': errors,
            })

        # Extract and validate registration data
        email = self._sanitize_input(post.get('email', ''), 100).lower()
        if not self._validate_email(email):
            errors.append("Please provide a valid email address.")

        company_name = self._sanitize_input(post.get('company_name', ''), 200)
        if len(company_name) < 2:
            errors.append("Company name must be at least 2 characters long.")

        phone = self._sanitize_input(post.get('phone', ''), 20)
        if not self._validate_phone(phone):
            errors.append("Please provide a valid phone number.")

        csd_number = self._sanitize_input(post.get('csd_number', ''), 50)
        company_reg_number = self._sanitize_input(post.get('company_registration_number', ''), 50)

        # Validate numeric/special fields
        try:
            country_id = int(post.get('country_id'))
            if country_id < 1:
                raise ValueError()
        except (ValueError, TypeError):
            errors.append("Please select a valid country.")
            country_id = None

        if errors:
            return request.render('sa_government_tender.supplier_registration_error', {
                'errors': errors,
            })

        # Comprehensive duplicate checks
        Partner = request.env['res.partner'].sudo()
        User = request.env['res.users'].sudo()

        # Check for duplicate email in suppliers
        if email:
            existing_email = Partner.search([
                ('email', '=', email),
                ('supplier_rank', '>', 0)
            ], limit=1)
            if existing_email:
                errors.append(
                    f"A supplier with email '{email}' is already registered: {existing_email.name} (ID: {existing_email.id}). "
                    "If you already have an account, please log in instead."
                )

        # Check for duplicate email in user accounts
        if email:
            existing_user = User.search([
                ('login', '=', email)
            ], limit=1)
            if existing_user and existing_user.partner_id:
                # Check if the user's partner is a supplier
                if existing_user.partner_id.supplier_rank > 0:
                    errors.append(
                        f"A user account with email '{email}' already exists and is linked to supplier: {existing_user.partner_id.name}. "
                        "Please log in or use password recovery."
                    )

        # Check for duplicate CSD number
        if csd_number:
            existing_csd = Partner.search([
                ('csd_number', '=', csd_number)
            ], limit=1)
            if existing_csd:
                errors.append(
                    f"A supplier with CSD Number '{csd_number}' is already registered: {existing_csd.name} (ID: {existing_csd.id})"
                )

        # Check for duplicate Company Registration number
        if company_reg_number:
            existing_reg = Partner.search([
                ('company_registration_number', '=', company_reg_number)
            ], limit=1)
            if existing_reg:
                errors.append(
                    f"A supplier with Company Registration Number '{company_reg_number}' is already registered: {existing_reg.name} (ID: {existing_reg.id})"
                )

        # If any duplicates found, show error page
        if errors:
            return request.render('sa_government_tender.supplier_registration_error', {
                'errors': errors,
                'show_login_link': True,
            })

        # Prepare partner values with sanitized inputs
        partner_vals = {
            'name': company_name,
            'is_company': True,
            'company_type': 'company',
            'email': email,
            'phone': phone,
            'mobile': self._sanitize_input(post.get('mobile', ''), 20),
            'website': self._sanitize_input(post.get('website', ''), 200),
            'street': self._sanitize_input(post.get('street', ''), 200),
            'street2': self._sanitize_input(post.get('street2', ''), 200),
            'city': self._sanitize_input(post.get('city', ''), 100),
            'state_id': int(post.get('state_id')) if post.get('state_id') and str(post.get('state_id')).isdigit() else False,
            'zip': self._sanitize_input(post.get('zip', ''), 20),
            'country_id': country_id,
            'vat': self._sanitize_input(post.get('vat', ''), 50),
            'supplier_rank': 1,  # Mark as supplier

            # SA Gov specific fields
            'company_registration_number': company_reg_number if company_reg_number else False,
            'csd_number': csd_number if csd_number else False,
            'csd_registered': bool(csd_number),
            'tax_clearance_number': self._sanitize_input(post.get('tax_clearance_number', ''), 50),
            'coid_number': self._sanitize_input(post.get('coid_number', ''), 50),
            'bbbee_level': post.get('bbbee_level', False),
            'bbbee_certificate_number': self._sanitize_input(post.get('bbbee_certificate_number', ''), 50),
            'comment': self._sanitize_input(post.get('additional_info', ''), 1000),
        }

        # Parse dates
        if post.get('csd_registration_date'):
            try:
                partner_vals['csd_registration_date'] = fields.Date.from_string(post.get('csd_registration_date'))
            except:
                pass

        if post.get('tax_clearance_expiry'):
            try:
                partner_vals['tax_clearance_expiry'] = fields.Date.from_string(post.get('tax_clearance_expiry'))
            except:
                pass

        if post.get('bbbee_certificate_date'):
            try:
                partner_vals['bbbee_certificate_date'] = fields.Date.from_string(post.get('bbbee_certificate_date'))
            except:
                pass

        if post.get('bbbee_expiry_date'):
            try:
                partner_vals['bbbee_expiry_date'] = fields.Date.from_string(post.get('bbbee_expiry_date'))
            except:
                pass

        try:
            # Rate limiting - check for recent registrations from same IP
            ip_address = request.httprequest.remote_addr
            recent_registrations = Partner.search_count([
                ('create_date', '>=', fields.Datetime.now() - timedelta(hours=1)),
                # Note: Odoo doesn't store IP by default, this is for future enhancement
            ])

            # Create partner with duplicate checking
            partner = Partner.create(partner_vals)
            _logger.info(f"Created supplier partner: {partner.name} (ID: {partner.id}, Email: {email}) from IP: {ip_address}")

            # Create portal user
            password_sent = False
            user = None
            if email:
                # Double-check user doesn't exist (race condition protection)
                existing_user = User.search([
                    ('login', '=', email)
                ], limit=1)

                if not existing_user:
                    # Create user with portal access
                    portal_group = request.env.ref('base.group_portal')
                    user_vals = {
                        'name': partner.name,
                        'login': email,
                        'email': email,
                        'partner_id': partner.id,
                        'groups_id': [(6, 0, [portal_group.id])],
                        'active': True,
                        'password': email,  # Set initial password to email address
                    }

                    try:
                        # Create the user with password set to their email
                        user = User.create(user_vals)
                        _logger.info(f"Created portal user for supplier: {user.name} (ID: {user.id}, Email: {email}) with initial password set to email")

                        # Generate password reset URL
                        reset_url = None
                        try:
                            # Use signup mechanism to generate reset token
                            user.sudo().signup_prepare()
                            signup_token = user.sudo().signup_token
                            if signup_token:
                                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                reset_url = f"{base_url}/web/reset_password?token={signup_token}&login={email}"
                                _logger.info(f"Generated password reset URL for user {email}")
                        except Exception as token_error:
                            _logger.warning(f"Could not generate signup token for user {email}: {token_error}")

                        # Send custom registration confirmation email with password reset link
                        try:
                            # Get the custom email template
                            template = request.env.ref('sa_government_tender.email_template_supplier_registration')
                            if template:
                                # Add reset URL to partner's context for the email template
                                if reset_url:
                                    partner = partner.with_context(password_reset_url=reset_url)
                                # Send the custom confirmation email
                                template.sudo().send_mail(partner.id, force_send=True)
                                password_sent = True
                                _logger.info(f"Registration confirmation email sent to {email} for user ID: {user.id}")
                        except Exception as email_error:
                            password_sent = False
                            _logger.exception(f"Could not send registration confirmation email to {email}")
                    except Exception as user_error:
                        _logger.exception(f"Error creating portal user for email {email}")
                        password_sent = False
                        user = None
                else:
                    # This shouldn't happen due to earlier checks, but handle gracefully
                    password_sent = False
                    _logger.warning(f"User with email {email} already exists, skipping user creation")

            return request.render('sa_government_tender.supplier_registration_success', {
                'partner': partner,
                'password_sent': password_sent,
                'user': user,
            })

        except ValidationError as e:
            # This will catch the model-level constraint violations
            error_message = str(e)
            return request.render('sa_government_tender.supplier_registration_error', {
                'errors': [error_message],
                'show_login_link': 'already exists' in error_message.lower(),
            })
        except Exception as e:
            _logger.exception("Error during supplier registration")
            return request.render('sa_government_tender.supplier_registration_error', {
                'errors': [f"An error occurred during registration: {str(e)}"],
                'show_login_link': False,
            })

    @http.route(['/supplier/profile'], type='http', auth='user', website=True)
    def supplier_profile(self, **kwargs):
        """View/edit supplier profile"""
        partner = request.env.user.partner_id
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        return request.render('sa_government_tender.supplier_profile_page', {
            'partner': partner,
            'countries': countries,
            'states': states,
            'page_name': 'supplier_profile',
        })

    @http.route(['/supplier/profile/update'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def supplier_profile_update(self, **post):
        """Update supplier profile"""
        partner = request.env.user.partner_id

        # Security check: ensure user can only update their own profile
        if not partner:
            _logger.warning(f"Profile update attempt by user {request.env.user.id} without partner")
            return request.redirect('/supplier/profile?error=Access denied')

        # Prepare update values with validation (only allow certain fields to be updated)
        errors = []

        phone = self._sanitize_input(post.get('phone'), 20)
        if phone and not self._validate_phone(phone):
            errors.append("Please provide a valid phone number.")

        if errors:
            error_msg = ' '.join(errors)
            return request.redirect(f'/supplier/profile?error={error_msg}')

        update_vals = {
            'phone': phone,
            'mobile': self._sanitize_input(post.get('mobile', ''), 20),
            'website': self._sanitize_input(post.get('website', ''), 200),
            'street': self._sanitize_input(post.get('street'), 200),
            'street2': self._sanitize_input(post.get('street2', ''), 200),
            'city': self._sanitize_input(post.get('city'), 100),
            'zip': self._sanitize_input(post.get('zip'), 20),
            'vat': self._sanitize_input(post.get('vat', ''), 50),
            'tax_clearance_number': self._sanitize_input(post.get('tax_clearance_number', ''), 50),
            'coid_number': self._sanitize_input(post.get('coid_number', ''), 50),
            'bbbee_level': post.get('bbbee_level', False),
            'bbbee_certificate_number': self._sanitize_input(post.get('bbbee_certificate_number', ''), 50),
            'comment': self._sanitize_input(post.get('additional_info', ''), 1000),
        }

        if post.get('state_id') and str(post.get('state_id')).isdigit():
            update_vals['state_id'] = int(post.get('state_id'))

        if post.get('country_id') and str(post.get('country_id')).isdigit():
            update_vals['country_id'] = int(post.get('country_id'))

        # Parse dates
        if post.get('tax_clearance_expiry'):
            try:
                update_vals['tax_clearance_expiry'] = fields.Date.from_string(post.get('tax_clearance_expiry'))
            except:
                pass

        if post.get('bbbee_certificate_date'):
            try:
                update_vals['bbbee_certificate_date'] = fields.Date.from_string(post.get('bbbee_certificate_date'))
            except:
                pass

        if post.get('bbbee_expiry_date'):
            try:
                update_vals['bbbee_expiry_date'] = fields.Date.from_string(post.get('bbbee_expiry_date'))
            except:
                pass

        try:
            partner.sudo().write(update_vals)

            return request.redirect('/supplier/profile?success=1')
        except Exception as e:
            _logger.exception("Error updating supplier profile")
            return request.redirect('/supplier/profile?error=' + str(e))
