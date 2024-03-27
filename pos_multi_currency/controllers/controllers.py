# -*- coding: utf-8 -*-
# from odoo import http


# class PosMultiCurrency(http.Controller):
#     @http.route('/pos_multi_currency/pos_multi_currency', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_multi_currency/pos_multi_currency/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_multi_currency.listing', {
#             'root': '/pos_multi_currency/pos_multi_currency',
#             'objects': http.request.env['pos_multi_currency.pos_multi_currency'].search([]),
#         })

#     @http.route('/pos_multi_currency/pos_multi_currency/objects/<model("pos_multi_currency.pos_multi_currency"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_multi_currency.object', {
#             'object': obj
#         })
