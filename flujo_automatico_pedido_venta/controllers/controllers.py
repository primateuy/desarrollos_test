# -*- coding: utf-8 -*-
# from odoo import http


# class FlujoAutomaticoPedidoVenta(http.Controller):
#     @http.route('/flujo_automatico_pedido_venta/flujo_automatico_pedido_venta', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/flujo_automatico_pedido_venta/flujo_automatico_pedido_venta/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('flujo_automatico_pedido_venta.listing', {
#             'root': '/flujo_automatico_pedido_venta/flujo_automatico_pedido_venta',
#             'objects': http.request.env['flujo_automatico_pedido_venta.flujo_automatico_pedido_venta'].search([]),
#         })

#     @http.route('/flujo_automatico_pedido_venta/flujo_automatico_pedido_venta/objects/<model("flujo_automatico_pedido_venta.flujo_automatico_pedido_venta"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('flujo_automatico_pedido_venta.object', {
#             'object': obj
#         })

