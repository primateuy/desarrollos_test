# -*- coding: utf-8 -*-
{
    'name': "Dirección por Defecto para Consulta RUT",
    'version': '17.0.1.0.0',

    'summary': "Utiliza un valor por defecto en la consulta RUT en caso de error en la Conexión CFE",
    'category': 'Localización/Uruguay',

    'author': 'PrimateUY',
    'website': 'https://primate.uy',

    'depends': ['l10n_uy_vat_query'],

    'data': [
        'security/ir.model.access.csv',
        'views/vista_res_company.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,

}

