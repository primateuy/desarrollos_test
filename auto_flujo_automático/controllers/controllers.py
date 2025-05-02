# -*- coding: utf-8 -*-
# from odoo import http


# class AutoFlujoAutomático(http.Controller):
#     @http.route('/auto_flujo_automático/auto_flujo_automático', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/auto_flujo_automático/auto_flujo_automático/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('auto_flujo_automático.listing', {
#             'root': '/auto_flujo_automático/auto_flujo_automático',
#             'objects': http.request.env['auto_flujo_automático.auto_flujo_automático'].search([]),
#         })

#     @http.route('/auto_flujo_automático/auto_flujo_automático/objects/<model("auto_flujo_automático.auto_flujo_automático"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('auto_flujo_automático.object', {
#             'object': obj
#         })

