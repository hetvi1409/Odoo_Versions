{
    'name': 'Sale Order Form Custom Renderer',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Custom JS Form Renderer for sale.order with widgets and OWL components',
    'author': 'Your Company',
    'depends': ['sale'],   # only depends on 'sale' — no extra Python libs needed

    # ── XML views loaded server-side ─────────────────────────────────────
    'data': [
        'views/sale_order_form_views.xml',
    ],

    # ── JS / CSS / XML templates loaded in the browser backend bundle ────
    'assets': {
        'web.assets_backend': [
            # 1. SCSS first — so styles are available when components mount
            'sale_form_custom/static/src/scss/sale_form_custom.scss',

            # 2. OWL XML templates — must be loaded before JS that references them
            'sale_form_custom/static/src/xml/sale_form_renderer.xml',
            'sale_form_custom/static/src/xml/amount_summary_widget.xml',
            'sale_form_custom/static/src/xml/status_bar_widget.xml',

            # 3. JS components
            'sale_form_custom/static/src/js/amount_summary_widget.js',
            'sale_form_custom/static/src/js/status_bar_widget.js',
            'sale_form_custom/static/src/js/sale_form_renderer.js',
        ],
    },

    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
