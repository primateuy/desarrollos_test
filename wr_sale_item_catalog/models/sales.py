# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def action_add_from_sale_catalog(self):
        order = self.env['sale.order'].browse(self.env.context.get('order_id'))
        domain = [('sale_ok', '=', True),
                  '|', ('company_id', '=', order.company_id.id), ('company_id', '=', False)]
        kanban_view = self.env.ref('wr_sale_item_catalog.view_product_product_kanban_sale_catalog')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Choose Products'),
            'res_model': 'product.product',
            'views': [(kanban_view.id, 'kanban'), (False, 'form')],
            'domain': domain,
            'context': {
                **self.env.context,
                'sale_catalog_mode': True,
                'create': self.env['product.template'].check_access_rights('create', raise_exception=False),
                'sale_catalog_sale_id': order.id,
                'pricelist': order.partner_id.property_product_pricelist.id,
                'hide_qty_buttons': order.sudo().state == 'done',
                'default_invoice_policy': 'delivery',
            },
            'help': _("""<p class="o_view_nocontent_smiling_face">
                No products found. Let's create one!
            </p>""")
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
