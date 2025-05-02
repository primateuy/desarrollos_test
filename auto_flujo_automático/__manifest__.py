{
    'name': 'Flujo Automático en Ventas',
    'version': '17.0.1.0.0',
    'summary': 'Modifica el botón Confirmar en órdenes de venta para ejecutar trabajos automáticos (ir.cron).',
    'category': 'Ventas',
    'author': 'PrimateUY',
    'website': 'https://primate.uy',

    'depends': ['sale', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/orden_venta_vista.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
