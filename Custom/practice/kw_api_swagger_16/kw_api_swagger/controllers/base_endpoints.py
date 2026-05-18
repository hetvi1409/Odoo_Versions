# Authentication endpoints removed from Swagger documentation for security
# reasons. The actual API routes still function, but are not advertised in
# public docs. Token/API key management should be done by
# administrators/managers.
BASE_ENDPOINTS = {}


ENDPOINT_ATTRS = [
    {
        'endpoint_url': '/kw_api/custom/{API_URL}',
        'check_add': 'is_list_enabled',
        'is_need_body_to_200': True,
        'description_in_403': 'List forbidden',
        'api_method': 'get',
    },
    {
        'endpoint_url': '/kw_api/custom/{API_URL}/{{API_ID_FIELD}}',
        'check_add': 'is_get_enabled',
        'is_need_body_to_200': True,
        'is_need_api_field': True,
        'description_in_403': 'Get forbidden',
        'api_method': 'get',
    },
    {
        'endpoint_url': '/kw_api/custom/{API_URL}',
        'is_required_body': True,
        'check_add': 'is_create_enabled',
        'is_need_body_to_200': True,
        'description_in_403': 'Create forbidden',
        'api_method': 'post',
    },
    {
        'endpoint_url': '/kw_api/custom/{API_URL}/{{API_ID_FIELD}}',
        'check_add': 'is_update_enabled',
        'is_need_body_to_200': True,
        'is_need_api_field': True,
        'is_required_body': True,
        'description_in_403': 'Update forbidden',
        'api_method': 'post',
    },
    {
        'endpoint_url': '/kw_api/custom/{API_URL}/{{API_ID_FIELD}}',
        'check_add': 'is_delete_enabled',
        'is_need_body_to_200': False,
        'description_in_403': 'Delete forbidden',
        'api_method': 'delete',
        'is_need_api_field': True,
        'description_in_200': 'Object {Attribute} was deleted',
    },
]
