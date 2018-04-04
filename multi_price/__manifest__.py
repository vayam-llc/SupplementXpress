
{
    'name': 'Product Multi Price',
    'summary': 'Set multiple price for product',
    'version': '10.0.1.0',
    'category': 'Product',
    'summary': """
Set multiple price for product
""",
    'author': "Sigb",
    'license': 'AGPL-3',
    'depends': ['product','sale','point_of_sale'],
    'data': [
        'views/view.xml',
        'views/template.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'application': True,
}
