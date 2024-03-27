# -*- coding: utf-8 -*-
{
    'name': "pos_multi_currency",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'documents', 'project', 'account', 'sale_project', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_invoice.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_multi_currency/static/src/xml/custom_pricelist.xml',
            'pos_multi_currency/static/src/js/SetPricelistButton.js',
        ],

        'web.assets_backend': [
            'pos_multi_currency/static/src/js/tax_totals.js',
        ],

    }
}
