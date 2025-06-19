{
    "name": "Reporte de Stock por Almacén",
    "version": "1.0.0",
    "depends": ["stock"],
    "author": "Andrés Iglesias / Primate Uy",
    "category": "Inventory",
    "data": [
        "security/ir.model.access.csv",
        "security/stock_report_security.xml",
        "views/res_users_view.xml",
        "views/stock_report_view.xml",
        "views/stock_warehouse_views.xml"
    ],
    "installable": True,
    "application": False,
}