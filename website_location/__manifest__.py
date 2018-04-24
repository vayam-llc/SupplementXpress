{
    'name': 'Web Location',
    'category': 'Website',
    'sequence': 50,
    'summary': 'Build Location page',
    'website': 'https://www.odoo.com/page/website-builder',
    'version': '1.0',
    'description': "",
    'depends': ['web', 'web_editor', 'web_planner', 'http_routing', 'portal'],
    'installable': True,
    'data': [
        'data/location.xml',
    ],
    # 'qweb': ['static/src/xml/website.backend.xml'],
    'application': True,
}
