{
    'name': 'MCB Brand',
    'category': 'brands',
    'version': '1.0',
    'description': "Set a mcb in product",
    'depends': ['base','product_brand','product','purchase','account'],
    'installable': True,
    'data': [
        'views/mcb_brands.xml',
        # 'views/mcb_in_product.xml',
    ],
    'application': True,
}