# -*- coding: utf-8 -*-
{
    'name': "Marketing mail",
    'description': """
        sending mail to customer for informing about alternative products,brand
    """,

    'author': "sigb",
    'depends': ['mail','base','sale','fetchmail'],
    'data': [
        'views/product_mail_notification.xml',
        'wizard/marketing_notification.xml'

    ],

}
