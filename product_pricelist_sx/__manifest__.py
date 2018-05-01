# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Product Pricelist SX',
    'version': '1.1',
    'author': 'Sarga Babu',
    'summary': 'Product Pricing Based on Customers',
    'sequence': 30,
    'description': """
    Module helps the user to add both whole sale, retail price for all products and helps in taking appropriate price and pricelist
    for a product based on the customer.
    """,
    'depends': ['base_sx', 'sale', 'pos_partner', 'product'],
    'data': [
        # 'views/pricelist_view.xml',
        'views/products_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
