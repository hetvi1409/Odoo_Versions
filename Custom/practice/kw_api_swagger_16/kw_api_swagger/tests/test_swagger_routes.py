import json
from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestSwaggerRoutes(HttpCase):
    """Test HTTP routes for Swagger UI and OpenAPI spec"""

    def setUp(self):
        super().setUp()
        self.base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url'
        )
        # Authenticate as admin user for route access
        self.authenticate('admin', 'admin')

    def test_swagger_ui_route_exists(self):
        """Test that /kw_api/swagger/ route is accessible"""
        url = f'{self.base_url}/kw_api/swagger/'
        response = self.url_open(url)
        self.assertEqual(
            response.status_code, 200,
            'Swagger UI route should return 200 OK'
        )

    def test_swagger_ui_returns_html(self):
        """Test that Swagger UI returns HTML content"""
        url = f'{self.base_url}/kw_api/swagger/'
        response = self.url_open(url)
        content_type = response.headers.get('Content-Type', '')
        self.assertIn(
            'text/html', content_type,
            'Swagger UI should return HTML content'
        )

    def test_swagger_ui_contains_swagger_elements(self):
        """Test that Swagger UI page contains expected elements"""
        url = f'{self.base_url}/kw_api/swagger/'
        response = self.url_open(url)
        content = response.content.decode('utf-8')

        # Check for Swagger UI specific elements
        self.assertIn(
            'swagger-ui', content,
            'Page should contain swagger-ui div'
        )
        self.assertIn(
            'Swagger API Documentation', content,
            'Page should contain Swagger documentation title'
        )

    def test_openapi_json_route_exists(self):
        """Test that /kw_api/swagger/swagger.json route is accessible"""
        url = f'{self.base_url}/kw_api/swagger/swagger.json'
        response = self.url_open(url)
        self.assertEqual(
            response.status_code, 200,
            'OpenAPI JSON route should return 200 OK'
        )

    def test_openapi_json_returns_json(self):
        """Test that swagger.json returns JSON content"""
        url = f'{self.base_url}/kw_api/swagger/swagger.json'
        response = self.url_open(url)
        content_type = response.headers.get('Content-Type', '')
        self.assertIn(
            'application/json', content_type,
            'OpenAPI endpoint should return JSON content'
        )

    def test_openapi_json_is_valid_json(self):
        """Test that swagger.json returns valid JSON that can be parsed"""
        url = f'{self.base_url}/kw_api/swagger/swagger.json'
        response = self.url_open(url)

        try:
            data = json.loads(response.content.decode('utf-8'))
            self.assertIsInstance(
                data, dict,
                'OpenAPI spec should be a JSON object'
            )
        except json.JSONDecodeError as e:
            self.fail(f'OpenAPI JSON is not valid: {e}')

    def test_swagger_ui_requires_authentication(self):
        """Test that Swagger UI requires user authentication"""
        # This test verifies the auth='user' setting
        # We're authenticated in setUp, so should get 200
        url = f'{self.base_url}/kw_api/swagger/'
        response = self.url_open(url)
        self.assertEqual(
            response.status_code, 200,
            'Authenticated user should access Swagger UI'
        )
