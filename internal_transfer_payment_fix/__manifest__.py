# -*- coding: utf-8 -*-
{
    'name': "Internal Transfer FIX ",
    'summary': """
    """,
    'description': """
        Este módulo asegura que, una vez validada una transferencia interna en Odoo tantos los pagos como los asientos 
        queden asociados y no puedan ser modificados aquellos que son de referencia.Tambien corrige el funcionamiento de 
        transferencias internas entre distiontas monedas.
    """,
    'author': "Primate",
    'website': "primate.uy",
    'category': 'Contabilidad',
    'version': '17.0.1.1.0',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'views/account_move.xml',
        'views/account_payment_view.xml',
    ],
}

