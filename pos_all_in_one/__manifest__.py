# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS All in one -Advance Point of Sale All in one Features for retail",
    "version" : "17.0.0.6",
    "category" : "Point of Sale",
    'summary': 'All in one pos Reprint pos Return POS Stock pos gift import sale from pos pos multi currency payment pos pay later pos internal transfer pos disable payment pos product template pos product operation pos loyalty rewards all pos reports pos stock pos retail',
    "description": """
    
  POS all in one -  advance app features pos Reorder pos Reprint pos Coupon Discount pos Order Return POS Stock pos gift pos order all pos all features pos discount pos order list print pos receipt pos item count pos bag charges import sale from pos create quote from pos pos multi currency payment  pos pay later pos internal transfer pos discable payment pos product template pos product create/update pos loyalty rewards pos reports
    
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com/demo-request?app=pos_all_in_one&version=17&edition=Community",
    "price": 65,
    "currency": 'EUR',
    "depends" : ['base','sale_management','pos_orders_all','pos_hr'],
    "data": [
        'security/ir.model.access.csv',
        'views/pos_reports_assets.xml',
        'views/pos_loyalty.xml',
        'views/pos_custom_view.xml',
        'views/POS_config_internal_transfer.xml',
        'views/custom_pos_disable_view.xml',
        'views/custom_pos_product_op_view.xml',
        'views/pos_config_inherit.xml',
        'views/custom_pos_paymentview.xml',
        'wizard/sales_summary_report.xml',
        'wizard/pos_sale_summary.xml',
        'wizard/x_report_view.xml',
        'wizard/z_report_view.xml',
        'wizard/top_selling.xml',
        'wizard/top_selling_report.xml',
        'wizard/profit_loss_report.xml',
        'wizard/pos_payment_report.xml',
        'wizard/profit_loss.xml',
        'wizard/pos_payment.xml',
    ],

    "auto_install": False,
    'license': 'OPL-1',
    "installable": True,
    'assets': {
        'point_of_sale._assets_pos': [

            # css
            "pos_all_in_one/static/src/css/pos.css",
            "pos_all_in_one/static/src/css/new_base_update.css",
            "pos_all_in_one/static/src/css/pos_payment.css",

            # store
            'pos_all_in_one/static/src/app/store/models.js',
            'pos_all_in_one/static/src/app/store/db.js',

            # # pos_product_operations

            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/see_all_products_button/see_all_products_button.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/see_all_products_button/see_all_products_button.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/pos_product_screen/pos_product_screen.js',
            'pos_all_in_one/static/src/app/screens/product_screen/pos_product_screen/pos_product_screen.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/pos_product_screen/pos_product.js',
            'pos_all_in_one/static/src/app/screens/product_screen/pos_product_screen/pos_product.xml',

            'pos_all_in_one/static/src/app/popup/product_details_create_popup.js',
            'pos_all_in_one/static/src/app/popup/product_details_create_popup.xml',

            'pos_all_in_one/static/src/app/popup/product_details_edit_popup.js',
            'pos_all_in_one/static/src/app/popup/product_details_edit_popup.xml',

            'pos_all_in_one/static/src/app/popup/pos_product_detail_popup.js',
            'pos_all_in_one/static/src/app/popup/pos_product_detail_popup.xml',

            # # bi_pos_product_template without alternative product flow.

            'pos_all_in_one/static/src/app/generic_components/product_card/product_card.xml',

            'pos_all_in_one/static/src/app/popup/product_template_popup.js',
            'pos_all_in_one/static/src/app/popup/product_template_popup.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/product_product/product_product.js',
            'pos_all_in_one/static/src/app/screens/product_screen/product_product/product_product.xml',

            # # bi_pos_internal_transfer

            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/pos_internal_transfer_button/pos_internal_transfer_button.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/pos_internal_transfer_button/pos_internal_transfer_button.xml',

            'pos_all_in_one/static/src/app/popup/pos_internal_stock_popup.js',
            'pos_all_in_one/static/src/app/popup/pos_internal_stock_popup.xml',

            'pos_all_in_one/static/src/app/popup/pos_confirmation_popup.js',
            'pos_all_in_one/static/src/app/popup/pos_confirmation_popup.xml',

            # bi_pos_payline_ref

            'pos_all_in_one/static/src/app/screens/payment_screen/payment_lines/payment_lines.js',
            'pos_all_in_one/static/src/app/screens/payment_screen/payment_lines/payment_lines.xml',

            # bi_pos_multi_currency

            'pos_all_in_one/static/src/app/screens/payment_screen/payment_screen.js',
            'pos_all_in_one/static/src/app/screens/payment_screen/payment_screen.xml',

            # pos_disable_payments

            'pos_all_in_one/static/src/app/screens/product_screen/product_screen.js',
            'pos_all_in_one/static/src/app/screens/product_screen/product_screen.xml',
            'pos_all_in_one/static/src/app/screens/product_screen/action_pad/action_pad.xml',

            # # bi_pos_reports
            
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/audit_report_button/audit_report_button.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/audit_report_button/audit_report_button.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/category_summary_button/category_summary_button.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/category_summary_button/category_summary_button.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/order_summary_button/order_summary_button.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/order_summary_button/order_summary_button.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/payment_summary_button/payment_summary_button.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/payment_summary_button/payment_summary_button.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/product_summary_button/product_summary_button.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/product_summary_button/product_summary_button.xml',

            'pos_all_in_one/static/src/app/popup/audit_report_popup.js',
            'pos_all_in_one/static/src/app/popup/audit_report_popup.xml',

            'pos_all_in_one/static/src/app/popup/category_summary_popup.js',
            'pos_all_in_one/static/src/app/popup/category_summary_popup.xml',

            'pos_all_in_one/static/src/app/popup/order_summary_popup.js',
            'pos_all_in_one/static/src/app/popup/order_summary_popup.xml',

            'pos_all_in_one/static/src/app/popup/payment_summary_popup.js',
            'pos_all_in_one/static/src/app/popup/payment_summary_popup.xml',

            'pos_all_in_one/static/src/app/popup/product_summary_popup.js',
            'pos_all_in_one/static/src/app/popup/product_summary_popup.xml',

            'pos_all_in_one/static/src/app/screens/receipt_screen/audit_location_receipt/location_receipt.js',
            'pos_all_in_one/static/src/app/screens/receipt_screen/audit_location_receipt/location_receipt.xml',

            'pos_all_in_one/static/src/app/screens/receipt_screen/audit_location_receipt/location_receipt_screen.js',
            'pos_all_in_one/static/src/app/screens/receipt_screen/audit_location_receipt/location_receipt_screen.xml',

            'pos_all_in_one/static/src/app/screens/receipt_screen/category_summary_receipt/category_receipt_widget.js',
            'pos_all_in_one/static/src/app/screens/receipt_screen/category_summary_receipt/category_receipt_widget.xml',

            'pos_all_in_one/static/src/app/screens/receipt_screen/category_summary_receipt/xml_pos_category_summary_receipt.js',
            'pos_all_in_one/static/src/app/screens/receipt_screen/category_summary_receipt/xml_pos_category_summary_receipt.xml',

            'pos_all_in_one/static/src/app/screens/receipt_screen/order_summary_receipt/order_receipt_widget.js',
            'pos_all_in_one/static/src/app/screens/receipt_screen/order_summary_receipt/order_receipt_widget.xml',

            'pos_all_in_one/static/src/app/screens/receipt_screen/order_summary_receipt/xml_pos_order_summary_receipt.js',
            'pos_all_in_one/static/src/app/screens/receipt_screen/order_summary_receipt/xml_pos_order_summary_receipt.xml',

            'pos_all_in_one/static/src/app/screens/receipt_screen/payment_summary_receipt/payment_receipt_widget.js',
            'pos_all_in_one/static/src/app/screens/receipt_screen/payment_summary_receipt/payment_receipt_widget.xml',

            'pos_all_in_one/static/src/app/screens/receipt_screen/payment_summary_receipt/xml_pos_payment_summary_receipt.js',
            'pos_all_in_one/static/src/app/screens/receipt_screen/payment_summary_receipt/xml_pos_payment_summary_receipt.xml',

            'pos_all_in_one/static/src/app/screens/receipt_screen/product_summary_receipt/product_receipt_widget.js',
            'pos_all_in_one/static/src/app/screens/receipt_screen/product_summary_receipt/product_receipt_widget.xml',

            'pos_all_in_one/static/src/app/screens/receipt_screen/product_summary_receipt/xml_pos_product_summary_receipt.js',
            'pos_all_in_one/static/src/app/screens/receipt_screen/product_summary_receipt/xml_pos_product_summary_receipt.xml',

            # # pos_loyalty_odoo

            'pos_all_in_one/static/src/app/generic_components/order_widget/order_widget.js',
            'pos_all_in_one/static/src/app/generic_components/order_widget/order_widget.xml',

            'pos_all_in_one/static/src/app/screens/partner_list/partner_list.xml',
            'pos_all_in_one/static/src/app/screens/partner_list/partner_line/partner_line.xml', 
            'pos_all_in_one/static/src/app/screens/partner_list/partner_editor/partner_editor.xml', 

            'pos_all_in_one/static/src/app/screens/receipt_screen/receipt/order_receipt.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/loyalty_button/loyalty_button_widget.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/loyalty_button/loyalty_button_widget.xml',

            'pos_all_in_one/static/src/app/popup/loyalty_popup_widget.js',
            'pos_all_in_one/static/src/app/popup/loyalty_popup_widget.xml',


            # # bi_pos_payment

            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/payment_button/create_payment_button_widget.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/payment_button/create_payment_button_widget.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/invoice_button/see_all_invoices_button_widget.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/invoice_button/see_all_invoices_button_widget.xml',

            'pos_all_in_one/static/src/app/screens/partner_list/partner_list.js',

            'pos_all_in_one/static/src/app/popup/register_payment_popup.js',
            'pos_all_in_one/static/src/app/popup/register_payment_popup.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/pos_invoice_screen/pos_invoice_screen.js',
            'pos_all_in_one/static/src/app/screens/product_screen/pos_invoice_screen/pos_invoice_screen.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/pos_invoice_screen/pos_invoice/pos_invoice.js',
            'pos_all_in_one/static/src/app/screens/product_screen/pos_invoice_screen/pos_invoice/pos_invoice.xml',

            'pos_all_in_one/static/src/app/popup/pos_invoice_detail_popup.js',
            'pos_all_in_one/static/src/app/popup/pos_invoice_detail_popup.xml',

            'pos_all_in_one/static/src/app/popup/register_invoice_payment_popup.js',
            'pos_all_in_one/static/src/app/popup/register_invoice_payment_popup.xml',

            # # pos_pay_later

            'pos_all_in_one/static/src/app/screens/product_screen/pos_orders_screen/pos_orders_screen.js',
            'pos_all_in_one/static/src/app/screens/product_screen/pos_orders_screen/pos_orders_screen.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/pos_orders_screen/pos_orders_line.xml',

            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/create_draft_button/create_draft_button.js',
            'pos_all_in_one/static/src/app/screens/product_screen/control_buttons/create_draft_button/create_draft_button.xml',

        ],
    },
    "live_test_url":"https://www.browseinfo.com/demo-request?app=pos_all_in_one&version=17&edition=Community",
    "images":["static/description/Banner.gif"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
