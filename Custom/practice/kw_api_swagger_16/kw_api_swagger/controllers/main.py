
import logging

import json
from odoo import http
from odoo.addons.kw_api.controllers.controller_base import KwApi
from odoo.addons.kw_api_custom_endpoint.controllers.custom_endpoint import (
    CustomEndpointController,
)
from odoo.http import request
from .base_endpoints import BASE_ENDPOINTS, ENDPOINT_ATTRS

_logger = logging.getLogger(__name__)

# pylint: disable=too-many-return-statements


class SwaggerController(CustomEndpointController):

    @http.route('/kw_api/swagger/', auth='user', website=True)
    def swagger_ui(self, **kwargs):
        return request.render('kw_api_swagger.swagger_template')

    @http.route('/kw_api/swagger/swagger.json', auth='user', methods=['GET'])
    def openapi(self, **kw):
        paths = BASE_ENDPOINTS.copy()
        base_url = request.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        endpoint_ids = request.env['kw.api.custom.endpoint'].sudo().search([])
        paths.update(self.get_custom_endpoint_paths(endpoint_ids))
        result = {
            "openapi": "3.0.0",
            "info": {
                "title": "Swagger API documentation",
                "description": "KW Api",
                "version": "1.0"
            },
            "servers": [{"url": f"{base_url}"}],
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "description": "Bearer token authentication. "
                        "Use any active <kw.api.key> or <kw.api.token>"
                    }
                }
            },
            "security": [{"BearerAuth": []}],
            "paths": paths
        }
        return http.request.make_response(
            json.dumps(result), headers={'Content-Type': 'application/json'}
        )

    def process_response(self, response, endpoint_id=False):
        data = json.loads(response.data.decode('utf-8'))
        code = int(data.get('code', 0))
        if 250 >= code >= 200 and 'content' in data and data['content']:
            first_record = data['content'][0]
            if first_record.get('id'):
                del first_record['id']
            if first_record.get('write_date'):
                del first_record['write_date']
            return {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties":
                            self.generate_swagger_schema_from_fields(
                                    first_record, endpoint_id=endpoint_id
                            )
                        }
                    }
                }
            }
        return {}

    @staticmethod
    def process_response_to_get():
        return {
            "content": {
                "application/json": {
                }
            }
        }

    @staticmethod
    def return_contact_to_administration(response_function):
        return {"content": {
            "application/json": {
                "schema": {
                    "type": "string",
                    "example":
                        "Please contact the administrator as this endpoint is "
                        "handled by a custom function. And the input data is "
                        f"defined in the function {response_function}"
                }
            }
        }}

    def generate_swagger_schema_from_fields(self, data, endpoint_id):
        """Generate input schema based on endpoint field configuration"""
        properties = {}

        for field_name in data.keys():
            field_id = request.env['ir.model.fields'].sudo().search([
                ('name', '=', field_name),
                ('model', '=', endpoint_id.model_id.model),
            ])
            field_schema = self.get_field_input_schema(field_id)
            properties[field_name] = field_schema

        return properties

    def get_field_input_schema(self, endpoint_field):
        """Get proper input schema based on Odoo field type"""
        ttype = endpoint_field.ttype

        schema_map = {
            'char': {'type': 'string', 'example': 'string'},
            'text': {'type': 'string', 'example': 'string'},
            'integer': {'type': 'integer', 'example': 123},
            'float': {'type': 'number', 'format': 'float', 'example': 123.45},
            'boolean': {'type': 'boolean', 'example': True},
            'date': {
                'type': 'string',
                'format': 'date',
                'example': '2024-12-31',
            },
            'datetime': {
                'type': 'string',
                'format': 'date-time',
                'example': '2024-12-31T23:59:59Z',
            },
            'many2one': {'type': 'integer', 'example': 123},
            'selection': {'type': 'string', 'example': 'selection_value'},
            'one2many': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Optional: Include for updates, '
                            'omit for new records'
                        }
                    },
                    'additionalProperties': True
                },
                'example': [
                    {'name': 'New Record', 'field': 'value'},
                    {'id': 5, 'name': 'Updated Record', 'int_field': 200.0}
                ]
            },
            'many2many': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Optional: Include for updates, '
                            'omit for new records'
                        }
                    },
                    'additionalProperties': True
                },
                'example': [
                    {'name': 'New Related Record'},
                    {'id': 3, 'name': 'Update Existing Record'}
                ]
            },
        }
        return schema_map.get(ttype, {'type': 'string', 'example': 'string'})

    def get_custom_endpoint_paths(self, endpoint_ids):
        paths = {}

        def process_endpoint(endpoint_id, endpoint_vals):
            for endpoint_attr in ENDPOINT_ATTRS:
                if getattr(endpoint_id, endpoint_attr.get('check_add')):
                    custom_url = endpoint_attr.get('endpoint_url').replace(
                        '{API_URL}', endpoint_id.api_name).replace(
                        '{API_ID_FIELD}', endpoint_id.model_id_field)

                    parameters = [
                        {
                            'name': endpoint_id.model_id_field,
                            'in': 'path',
                            "schema": {"type": "string"},
                            'required': 'true'
                        }
                        if endpoint_attr.get('is_need_api_field') else None
                    ]
                    parameters = [param for param in parameters if
                                  param is not None]
                    example_response_200 = {}
                    dc_403 = endpoint_attr.get('description_in_403')
                    if endpoint_id.kind == 'fields':
                        kw_api = KwApi(**endpoint_id.kwapi_params())
                        response = endpoint_id.response(kw_api=kw_api)
                        example_response_body = self.process_response(
                            response, endpoint_id=endpoint_id
                        ) if endpoint_attr.get('is_required_body') \
                            else (self.process_response_to_get())
                        example_response_200 = {} if not endpoint_attr.get(
                            'is_need_body_to_200') else example_response_body
                    else:
                        example_response_body = (
                            self.return_contact_to_administration(
                                endpoint_id.response_function))
                    vals = {
                        endpoint_attr.get('api_method'): {
                            'description': endpoint_id.description,
                            'parameters': parameters,
                            'security': [{'BearerAuth': []}],
                            "requestBody": {
                                "required": endpoint_attr.get(
                                    'is_required_body'),
                                **example_response_body
                            } if endpoint_id.is_json_required else {},
                            "responses": {
                                "200": {
                                    "description": endpoint_attr.get(
                                        'description_in_200',
                                        "OK (Successfully)"),
                                    **example_response_200
                                },
                                "400": {
                                    "description":
                                        "Bad Request (Invalid request)"},
                                "403": {
                                    "description": endpoint_attr.get(
                                        'description_in_403'),
                                    "content": {"application/json": {
                                        "schema":
                                            {"type": "object",
                                             "properties": {"error": {
                                                 "type": "object",
                                                 "properties": {"code": {
                                                     "type": "string",
                                                     "example": "403"},
                                                     "message": {
                                                         "type": "string",
                                                         "example":
                                                             f"403: {dc_403}"
                                                 }
                                                 }
                                             }
                                             }
                                             }
                                    }
                                    }
                                }
                            }
                        }
                    }
                    if custom_url in endpoint_vals:
                        endpoint_vals[custom_url].update(vals)
                    else:
                        endpoint_vals[custom_url] = vals
        for endpoint_id in endpoint_ids:
            endpoint_vals = {}
            process_endpoint(endpoint_id, endpoint_vals)
            paths.update(endpoint_vals)
        return dict(paths)
