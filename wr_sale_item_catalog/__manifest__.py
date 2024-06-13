# -*- coding: utf-8 -*-

{
    "name": "Sale Line Catalog",
    "version": "16.0.3",
    "category": "Sales/Sales",
    'summary': 'Sale Line Catalog',
    "description": """
        This module enables users to add products in sale order line using catalog action.
    """,
    "author": "WebRulers Infotech",
    "website": "https://www.webrulersinfotech.com",
    "live_test_url": "https://www.youtube.com/watch?v=RluuN0hQmYc",
    "price": "30",
    "currency": "USD",
    "images": ["static/description/main_thumbnail.gif"],
    "depends": ['base', 'sale', 'sale_management'],
    "data": [
        'views/sale_view.xml',
        'views/product_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'wr_sale_item_catalog/static/src/components/**/*',
            'wr_sale_item_catalog/static/src/views/**/*',
        ],
    },
    "auto_install": False,
    "installable": True,
    "license": "LGPL-3",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
