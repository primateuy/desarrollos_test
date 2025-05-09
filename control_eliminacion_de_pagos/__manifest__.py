{
    "name": "Control de Eliminación de Pagos",
    "version": "17.0.1.0.0",
    "category": "Accounting",
    "summary": "Permite eliminar pagos solo a ciertos grupos de usuarios",
    "author": "Andrés Iglesias / PrimateUy",
    "website": "https://www.primate.uy",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/delete_payment_groups.xml",
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}