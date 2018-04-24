# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    'name': 'Theme Crafito',
    'summary': 'Advanced Responsive Theme with A Range of Custom Snippets',
    'description': '''Theme Crafito
Business theme
Hardware theme
Hardware and tools theme
Single Page theme
Digital security theme
Event theme
Medical equipments theme
multipurpose template for industry
multipurpose template for all industries
odoo custom theme
customizable odoo theme
multi industry odoo theme
multi purpose responsive odoo theme
multipurpose website template for odoo
odoo multipurpose theme for industry
multipurpose templates for odoo
odoo ecommerce templates
odoo ecommerce theme
odoo ecommerce themes
odoo responsive themes
odoo website themes
odoo ecommerce website theme
odoo theme for ecommerce store
odoo bootstrap themes
customize odoo theme
odoo ecommerce store theme for business
odoo theme for business
odoo responsive website theme
	''',
    'category': 'Theme/Ecommerce',
    'version': '11.0.1.0.0',
    'depends': [
        'website_hr',
        'mass_mailing',
        'website_sale',
        'website_blog',
        'website_event_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/views.xml',
        'views/website_view.xml',
        'views/slider_views.xml',
        'views/snippets.xml',
        'views/theme_customize.xml',
        'views/theme1.xml',
    ],
    'demo': [
        # 'demo/demo_homepage.xml',
    ],
    'images': ['static/description/splash-screen.png'],
    'application': True,
}
