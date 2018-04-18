{
    'name': 'Product Brand Pricelist',
    'version': '11.0.1.0.0',
    'category': 'Product',
    'summary': "Product Brand Pricelist",
    'author': 'Socius IGB',
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'product',
        'sale_management',
        'product_brand',
        'decimal_precision',
        ],
    'data': [
        'views/pricelist.xml',
    ],
    'installable': True,
    'auto_install': False
}