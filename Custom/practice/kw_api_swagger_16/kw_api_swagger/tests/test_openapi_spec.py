import json
from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestOpenAPISpec(HttpCase):
    """Test OpenAPI specification generation and structure"""

    def setUp(self):
        super().setUp()
        self.base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url'
        )

        # Create a test custom endpoint for testing
        self.test_model = self.env['ir.model'].search([
            ('model', '=', 'res.partner')
        ], limit=1)

        self.test_endpoint = self.env['kw.api.custom.endpoint'].create({
            'name': 'Test Endpoint',
            'api_name': 'test_api',
            'model_id': self.test_model.id,
            'model_id_field': 'id',
            'kind': 'fields',
            'is_list_enabled': True,
            'is_get_enabled': True,
            'is_create_enabled': True,
            'is_update_enabled': True,
            'is_delete_enabled': True,
            'is_api_key_required': False,
            'is_token_required': True,
        })

        # Authenticate for HTTP tests
        self.authenticate('admin', 'admin')

    def _get_openapi_spec(self):
        """Helper method to fetch and parse OpenAPI spec"""
        url = f'{self.base_url}/kw_api/swagger/swagger.json'
        response = self.url_open(url)
        return json.loads(response.content.decode('utf-8'))

    def test_openapi_version(self):
        """Test that OpenAPI version is 3.0.0"""
        spec = self._get_openapi_spec()
        self.assertIn('openapi', spec, 'Spec should contain openapi version')
        self.assertEqual(
            spec['openapi'], '3.0.0',
            'OpenAPI version should be 3.0.0'
        )

    def test_info_section_exists(self):
        """Test that info section exists with required fields"""
        spec = self._get_openapi_spec()
        self.assertIn('info', spec, 'Spec should contain info section')

        info = spec['info']
        self.assertIn('title', info, 'Info should contain title')
        self.assertIn('description', info, 'Info should contain description')
        self.assertIn('version', info, 'Info should contain version')

    def test_info_section_content(self):
        """Test that info section has correct content"""
        spec = self._get_openapi_spec()
        info = spec['info']

        self.assertEqual(
            info['title'], 'Swagger API documentation',
            'Title should be correct'
        )
        self.assertEqual(
            info['description'], 'KW Api',
            'Description should be correct'
        )

    def test_servers_section_exists(self):
        """Test that servers section exists and contains base URL"""
        spec = self._get_openapi_spec()
        self.assertIn('servers', spec, 'Spec should contain servers section')
        self.assertIsInstance(
            spec['servers'], list,
            'Servers should be a list'
        )
        self.assertGreater(
            len(spec['servers']), 0,
            'Servers list should not be empty'
        )

        server = spec['servers'][0]
        self.assertIn('url', server, 'Server should contain URL')
        self.assertEqual(
            server['url'], self.base_url,
            'Server URL should match base URL'
        )

    def test_security_schemes_exist(self):
        """Test that security schemes are defined"""
        spec = self._get_openapi_spec()
        self.assertIn('components', spec, 'Spec should contain components')
        self.assertIn(
            'securitySchemes', spec['components'],
            'Components should contain securitySchemes'
        )

        security_schemes = spec['components']['securitySchemes']
        self.assertIn(
            'BearerAuth', security_schemes,
            'Should contain BearerAuth scheme'
        )

        bearer_auth = security_schemes['BearerAuth']
        self.assertEqual(
            bearer_auth['type'], 'http',
            'BearerAuth type should be http'
        )
        self.assertEqual(
            bearer_auth['scheme'], 'bearer',
            'BearerAuth scheme should be bearer'
        )

    def test_global_security_applied(self):
        """Test that global security is applied"""
        spec = self._get_openapi_spec()
        self.assertIn('security', spec, 'Spec should contain security')
        self.assertIsInstance(
            spec['security'], list,
            'Security should be a list'
        )
        self.assertIn(
            {'BearerAuth': []}, spec['security'],
            'Security should include BearerAuth'
        )

    def test_paths_section_exists(self):
        """Test that paths section exists"""
        spec = self._get_openapi_spec()
        self.assertIn('paths', spec, 'Spec should contain paths section')
        self.assertIsInstance(
            spec['paths'], dict,
            'Paths should be a dictionary'
        )

    def test_custom_endpoint_paths_generated(self):
        """Test that custom endpoint paths are generated"""
        spec = self._get_openapi_spec()
        paths = spec['paths']

        # Check for test endpoint paths
        expected_paths = [
            '/kw_api/custom/test_api',  # List/Create
            '/kw_api/custom/test_api/{id}',  # Get/Update/Delete
        ]

        for path in expected_paths:
            self.assertIn(
                path, paths,
                f'Custom endpoint path {path} should be in paths'
            )

    def test_crud_operations_present(self):
        """Test that CRUD operations are present for enabled endpoints"""
        spec = self._get_openapi_spec()
        paths = spec['paths']

        list_create_path = '/kw_api/custom/test_api'
        detail_path = '/kw_api/custom/test_api/{id}'

        # Check list/create path has GET and POST
        if list_create_path in paths:
            self.assertIn(
                'get', paths[list_create_path],
                'List endpoint should have GET method'
            )
            self.assertIn(
                'post', paths[list_create_path],
                'Create endpoint should have POST method'
            )

        # Check detail path has GET, POST, and DELETE
        if detail_path in paths:
            self.assertIn(
                'get', paths[detail_path],
                'Get endpoint should have GET method'
            )
            self.assertIn(
                'post', paths[detail_path],
                'Update endpoint should have POST method'
            )
            self.assertIn(
                'delete', paths[detail_path],
                'Delete endpoint should have DELETE method'
            )

    def test_endpoint_has_required_structure(self):
        """Test that endpoint operations have required structure"""
        spec = self._get_openapi_spec()
        paths = spec['paths']

        list_path = '/kw_api/custom/test_api'
        if list_path in paths and 'get' in paths[list_path]:
            operation = paths[list_path]['get']

            # Check required operation fields
            self.assertIn(
                'description', operation,
                'Operation should have description'
            )
            self.assertIn(
                'parameters', operation,
                'Operation should have parameters'
            )
            self.assertIn(
                'responses', operation,
                'Operation should have responses'
            )

    def test_response_codes_defined(self):
        """Test that standard response codes are defined"""
        spec = self._get_openapi_spec()
        paths = spec['paths']

        list_path = '/kw_api/custom/test_api'
        if list_path in paths and 'get' in paths[list_path]:
            responses = paths[list_path]['get']['responses']

            # Check for standard response codes
            self.assertIn('200', responses, 'Should define 200 response')
            self.assertIn('400', responses, 'Should define 400 response')
            self.assertIn('403', responses, 'Should define 403 response')

    def test_path_parameters_for_detail_endpoint(self):
        """Test that detail endpoints have path parameters"""
        spec = self._get_openapi_spec()
        paths = spec['paths']

        detail_path = '/kw_api/custom/test_api/{id}'
        if detail_path in paths and 'get' in paths[detail_path]:
            parameters = paths[detail_path]['get']['parameters']

            # Find the id parameter
            id_param = None
            for param in parameters:
                if param.get('name') == 'id':
                    id_param = param
                    break

            self.assertIsNotNone(
                id_param,
                'Detail endpoint should have id parameter'
            )
            self.assertEqual(
                id_param.get('in'), 'path',
                'ID parameter should be in path'
            )
            self.assertEqual(
                id_param.get('required'), 'true',
                'ID parameter should be required'
            )
