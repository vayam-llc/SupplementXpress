# -*- coding: utf-8 -*-
{
    'name': "Mail notifcation",
    'description': """
        Mail notifications to the customer
    """,

    'author': "sigb",
    'depends': [
        'mail','base','sale','fetchmail'
    ],
    'data': [
        'views/welcome_mail.xml',

    ],

}
