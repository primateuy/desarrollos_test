# -*- coding: utf-8 -*-
{
    'name': 'Dirección por Defecto',
    'version': '17.0.1.0.0',

    'summary': 'Evita el AttributeError y asigna "Dirección no definida" por defecto',

    'category': 'Localización/Uruguay',
    'author': 'PrimateUY',
    'website': 'https://primate.uy',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'l10n_uy_vat_query',
    ],
    'data': [
        'views/res_company_cfe_view.xml',
    ],
    'installable': True,
    'application': False,
}
