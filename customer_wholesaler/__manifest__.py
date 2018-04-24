
{
    'name': 'wholesale customer',
    'category': 'sale',
    'version': '1.0',
    'author':'sigb',
    'description': "Set a customer as wholesaler",
    'depends': ['base','web','website','website_sale'],
    'installable': True,
    'data': [
        'views/wholesaler.xml',
        'views/wholesale_page.xml',
        'views/templates.xml',

    ],
}
