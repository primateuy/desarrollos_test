{
    'name': 'Flujo Automático Pedido Venta',
    'version': '1.0',
    'category': 'Sales',
    'author': 'PrimateUY',
    'website': 'https://primate.uy',
    'license': 'LGPL-3',

    'depends': ['sale_automatic_workflow', 'sale_automatic_workflow_stock'],

    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_type_view.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml'
    ],

    'installable': True,
    'application': True,
}
