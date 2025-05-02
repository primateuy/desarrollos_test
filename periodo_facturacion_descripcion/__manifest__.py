# -*- coding: utf-8 -*-
{
    'name': 'Periodo Facturación - Descripción simplificada',

    'summary': 'Si se activa el campo (Usar descripción de cotización) dentro de Planes recurrentes, la factura usará únicamente la descripción original de la cotización sin concatenar datos de la recurrencia.',

    'description': """
    Si se activa el campo (Usar descripción de cotización) dentro de Planes recurrentes,
    la factura usará únicamente la descripción original de la cotización
    sin concatenar datos de la recurrencia.
    """,

    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'author': 'PrimateUY',
    'website': 'https://primate.uy',
    'license': 'LGPL-3',


    'depends': ['sale', 'account', 'sale_subscription'],

    'data': [
        'views/sale_subscription_plan_view.xml',
    ],

    'installable': True,
    'application': False,
}

