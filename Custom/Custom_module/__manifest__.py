# -*- coding: utf-8 -*-
{
    'name': 'Custom Module',
    'version': '1.3',
    'summary': 'Custom Module',
    'sequence': 10,
    'description': """Custom""",
    'depends': ['base','sale_management','website','website_sale','stock'],
    'data': [
        'security/ir.model.access.csv',
        "views/custom.xml",
        "views/menu.xml",
        "views/product_template.xml",
    ]
}


# 1. In Product backend form add one boolean field called is_one_per_line
# 2. When we add more than one quantity into the cart then it will add separate lines into the
# cart and in sale order as well if for that product is_one_per_line is true.
# For example : we are trying to add 3 quantities into cart then in cart and in sale order
# three separate lines should be created.

# Custom_module