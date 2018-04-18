# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase category',
    'category': 'Purchase',
    'sequence': 15,
    'summary': 'Purchase category',
    'version': '1.0',
    'description': "",
    'installable': True,
    'depends': [
        'crm','product','sale','purchase','stock'
    ],
    'data': ['security/ir.model.access.csv',
             'views/purchase_category.xml'],
    'application': True,
}
