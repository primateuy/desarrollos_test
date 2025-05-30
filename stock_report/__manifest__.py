{
    "name": "Reporte de Stock por Almacén",
    "version": "1.0.0",
    "depends": ["stock"],
    "author": "Andrés Iglesias / Primate Uy",
    "category": "Inventory",
    "data": [
        "views/stock_report_view.xml",
        "views/res_users_view.xml",
        "security/ir.model.access.csv",
        "security/stock_report_security.xml"
    ],
    "installable": True,
    "application": False,
}