# -*- coding: utf-8 -*-
{
    'name': "Divisa Secundaria",

    'summary': """
        Divisa secundaria en lineas de asiento""",

    'description': """
        Agrega Divisa secundaria en lineas de asiento. 
    """,

    'author': "Proyecta",
    'website': "https://odoo.proyectasoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '16.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'views/account_move_line_view.xml',
        'wizard/compute_secondary_amount_view.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
