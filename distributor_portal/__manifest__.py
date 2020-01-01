# -*- coding: utf-8 -*-
{
    'name': "distributor_portal",

    'summary': """
        Manage Record of Distributors""",

    'description': """
         Manage Record of Distributors
    """,

    'author': "Dymaxel Systems (Private) Limited",
    'website': "http://www.https://telenoc.org/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '12.4',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','crm','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
