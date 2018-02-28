
{
    'name': 'Pos Partner customization',
    'summary': 'Customization in POS Partner',
    'version': '11.0.1.0',
    'category': 'POS',
    'author': "Sigb",
    'license': 'AGPL-3',
    'depends': ['base','point_of_sale'],
    'data': [
        'views/pos_partner_view.xml',
        'views/template.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'application': True,
}
