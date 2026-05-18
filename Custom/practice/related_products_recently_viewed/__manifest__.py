{ 
    'name': 'Website Related Products & Recently Viewed Products',
    'version': '2.4',
    'category': 'Website',
    'author': 'Real Tech',
    'license': 'LGPL-3',
    'summary': 'Display related products and recently viewed items on product details page',
    'depends': ['website'],
    'data': [
        'views/recent_products_carousel.xml',
    ],
    'images': [
        'static/description/main_screenshot.gif',
        'images/main_1.png',
        'images/main_2.png',
        'images/main_3.png'
    ],
    'assets': {
        'web.assets_frontend': [
            'product_carousel/static/src/scss/recent_products_carousel.scss',
            'product_carousel/static/src/js/recent_products_carousel.js',
        ],
    },
    'installable': True,
    'application': False,
}
