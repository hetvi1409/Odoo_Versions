=======================
KW API Swagger
=======================

Provides interactive Swagger UI and auto-generated OpenAPI 3.0 documentation for KW API Custom Endpoints.

.. contents::
   :local:

Overview
========

This module adds Swagger/OpenAPI documentation capabilities to ``kw_api_custom_endpoint``.
It automatically generates interactive API documentation from your custom endpoint configurations,
making it easy to explore, test, and understand your API without manual documentation.

Features
========

* **Auto-generated OpenAPI 3.0 Specification** - No manual spec writing required
* **Interactive Swagger UI** - Test endpoints directly from the browser
* **Dynamic Schema Generation** - Automatically infers schemas from Odoo model fields
* **Field Type Mapping** - Supports all Odoo field types (char, integer, many2one, one2many, etc.)
* **Authentication Support** - Documents API key and bearer token authentication
* **CRUD Endpoint Documentation** - Covers list, get, create, update, delete operations
* **Real-time Updates** - Swagger spec updates when endpoints are modified

Dependencies
============

Required Modules
----------------

* ``kw_api_custom_endpoint`` - Provides the core custom endpoint functionality

External Dependencies
---------------------

* **Swagger UI** (loaded via CDN) - No local installation required

Installation
============

1. Ensure ``kw_api_custom_endpoint`` is installed and configured
2. Install ``kw_api_swagger`` module::

    odoo-bin -d your_database -i kw_api_swagger

3. No additional configuration required

Usage
=====

Accessing Swagger UI
--------------------

**Via Menu:**

Navigate to: ``KW API � Swagger``

**Via URL:**

Browse to: ``https://your-odoo-instance.com/kw_api/swagger/``

**OpenAPI Spec:**

JSON endpoint: ``https://your-odoo-instance.com/kw_api/swagger/swagger.json``

Available Endpoints
-------------------

The Swagger UI automatically documents:

* **Authentication Endpoints**

  - ``POST /kw_api/auth/token`` - Get access token
  - ``POST /kw_api/auth/is_token_alive`` - Validate token

* **Custom CRUD Endpoints**

  - ``GET /kw_api/custom/{api_name}`` - List records
  - ``GET /kw_api/custom/{api_name}/{id}`` - Get single record
  - ``POST /kw_api/custom/{api_name}`` - Create record
  - ``POST /kw_api/custom/{api_name}/{id}`` - Update record
  - ``DELETE /kw_api/custom/{api_name}/{id}`` - Delete record

Testing Endpoints
-----------------

1. Open Swagger UI from the menu
2. Click on an endpoint to expand details
3. Click "Try it out"
4. Fill in required parameters
5. Add authentication headers if required
6. Click "Execute" to test the endpoint
7. View response below

Technical Details
=================

Architecture
------------

* **Controller Inheritance**: ``SwaggerController`` extends ``CustomEndpointController``
* **No Data Layer**: Uses models from ``kw_api_custom_endpoint``
* **View Integration**: Template inherits from ``web.report_layout``

Routes
------

::

    GET  /kw_api/swagger/              - Swagger UI interface (auth='user')
    GET  /kw_api/swagger/swagger.json  - OpenAPI specification (auth='user')

How It Works
------------

1. Queries all configured ``kw.api.custom.endpoint`` records
2. Generates OpenAPI paths for enabled operations (list, get, create, update, delete)
3. Inspects ``ir.model.fields`` to build request/response schemas
4. Maps Odoo field types to OpenAPI data types
5. Serves JSON spec to Swagger UI for rendering

Field Type Mappings
-------------------

========== ============= ===================
Odoo Type  OpenAPI Type  Example
========== ============= ===================
char       string        "example text"
text       string        "long text"
integer    integer       123
float      number        123.45
boolean    boolean       true
date       string(date)  "2024-12-31"
datetime   string        "2024-12-31T23:59:59Z"
many2one   integer       123
selection  string        "value"
one2many   array         [{...}]
many2many  array         [{...}]
========== ============= ===================

Configuration
=============

This module requires no configuration. Swagger documentation is automatically
generated based on your custom endpoint configurations in ``kw_api_custom_endpoint``.

**Authentication**: Swagger UI requires Odoo user authentication (auth='user').
Ensure users have appropriate access rights to the KW API menu.

Known Limitations
=================

* Custom response functions show "contact administrator" message (cannot introspect)
* Requires active user session (not public access)
* Depends on endpoints being configured in ``kw_api_custom_endpoint``

Troubleshooting
===============

**Swagger UI not loading:**

* Check browser console for JavaScript errors
* Verify ``swagger-ui.js`` is accessible at ``/kw_api_swagger/static/js/swagger-ui.js``
* Clear browser cache

**Endpoints missing from Swagger:**

* Ensure endpoints are enabled in ``kw_api_custom_endpoint``
* Check that operations (list/get/create/update/delete) are activated
* Refresh the page to regenerate the spec

**Schema showing incorrect types:**

* Verify field definitions in the related Odoo model
* Check ``ir.model.fields`` for correct field type (ttype)
