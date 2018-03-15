{
    'name': ' Invoice Report',
    'version': '10.1',
    'category': 'Report',
	'summary': 'Montdor Invoice Report ',
	'author': 'Sigb',
    'website': 'http://www.sociusigb.com',
    'description': """Customized Invoice Report for Montdor""",
    'depends': ['account', 'sale'],
    'data': [  
        'views/invoice_template.xml',
        'views/montdor_report.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}