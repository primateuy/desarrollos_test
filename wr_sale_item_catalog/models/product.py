# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict
from odoo.tools import float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sale_catalog_quantity = fields.Float('SOL Quantity', compute="_compute_sale_catalog_quantity",
                                         inverse="_inverse_sale_catalog_quantity",
                                         search="_search_sale_catalog_quantity")
    sale_catalog_partner_price = fields.Float('Partner Price', compute="_compute_sale_catalog_partner_price")
    sale_catalog_partner_price_currency_id = fields.Many2one('res.currency',
                                                             compute="_compute_sale_catalog_partner_price")

    @api.model
    def _get_contextual_sale_order(self):
        sale_id = self.env.context.get('sale_catalog_sale_id')
        if sale_id:
            return self.env['sale.order'].browse(sale_id)
        return self.env['sale.order']

    @api.depends('sale_catalog_quantity')
    def _compute_sale_catalog_partner_price(self):
        sale_order = self._get_contextual_sale_order()
        for product in self:
            product.sale_catalog_partner_price = sale_order.pricelist_id._get_products_price(product, product.sale_catalog_quantity).get(product.id, product.list_price) if sale_order.pricelist_id else product.list_price
            product.sale_catalog_partner_price_currency_id = sale_order.currency_id or product.currency_id

    def _compute_sale_catalog_quantity(self):
        order = self._get_contextual_sale_order()
        if order:
            SaleOrderLine = self.env['sale.order.line']
            if self.user_has_groups('project.group_project_user'):
                order = order.sudo()
                SaleOrderLine = SaleOrderLine.sudo()
            products_qties = SaleOrderLine._read_group(
                [('id', 'in', order.order_line.ids), ('order_id', '=', order.id)],
                ['product_id', 'product_uom_qty'], ['product_id'])
            qty_dict = dict([(x['product_id'][0], x['product_uom_qty']) for x in products_qties if x['product_id']])
            for product in self:
                product.sale_catalog_quantity = qty_dict.get(product.id, 0)
        else:
            self.sale_catalog_quantity = False

    def _inverse_sale_catalog_quantity(self):
        order = self._get_contextual_sale_order()
        if order:
            SaleOrderLine_sudo = self.env['sale.order.line'].sudo()
            sale_lines_read_group = SaleOrderLine_sudo._read_group([
                ('order_id', '=', order.id),
                ('product_id', 'in', self.ids)],
                ['product_id', 'sequence', 'ids:array_agg(id)'],
                ['product_id', 'sequence'],
                lazy=False)
            sale_lines_per_product = defaultdict(lambda: self.env['sale.order.line'])
            for sol in sale_lines_read_group:
                sale_lines_per_product[sol['product_id'][0]] |= SaleOrderLine_sudo.browse(sol['ids'])
            for product in self:
                sale_lines = sale_lines_per_product.get(product.id, self.env['sale.order.line'])
                all_editable_lines = sale_lines.filtered(
                    lambda l: l.qty_delivered == 0 or l.qty_delivered_method == 'manual' or l.state != 'done')
                diff_qty = product.sale_catalog_quantity - sum(sale_lines.mapped('product_uom_qty'))
                if all_editable_lines:  # existing line: change ordered qty (and delivered, if delivered method)
                    if diff_qty > 0:
                        vals = {
                            'product_uom_qty': all_editable_lines[0].product_uom_qty + diff_qty,
                        }
                        if all_editable_lines[0].qty_delivered_method == 'manual':
                            vals['qty_delivered'] = all_editable_lines[0].product_uom_qty + diff_qty
                        all_editable_lines[0].with_context(sale_catalog_no_message_post=True).write(vals)
                        continue
                    # diff_qty is negative, we remove the quantities from existing editable lines:
                    for line in all_editable_lines:
                        new_line_qty = max(0, line.product_uom_qty + diff_qty)
                        diff_qty += line.product_uom_qty - new_line_qty
                        vals = {
                            'product_uom_qty': new_line_qty
                        }
                        if line.qty_delivered_method == 'manual':
                            vals['qty_delivered'] = new_line_qty
                        line.with_context(sale_catalog_no_message_post=True).write(vals)
                        if diff_qty == 0:
                            break
                elif diff_qty > 0:  # create new SOL
                    vals = {
                        'order_id': order.id,
                        'product_id': product.id,
                        'product_uom_qty': diff_qty,
                        'product_uom': product.uom_id.id,
                    }
                    if product.service_type == 'manual':
                        vals['qty_delivered'] = diff_qty

                    sol = SaleOrderLine_sudo.create(vals)
                    if order.pricelist_id.discount_policy != 'without_discount':
                        sol.discount = 0.0
                    if not sol.qty_delivered_method == 'manual':
                        sol.qty_delivered = 0

    @api.model
    def _search_sale_catalog_quantity(self, operator, value):
        if not (isinstance(value, int) or (isinstance(value, bool) and value is False)):
            raise ValueError(_('Invalid value: %s', value))
        if operator not in ('=', '!=', '<=', '<', '>', '>=') or (operator == '!=' and value is False):
            raise ValueError(_('Invalid operator: %s', operator))

        order = self._get_contextual_sale_order()
        if not order:
            return []
        op = 'inselect'
        if value is False:
            value = 0
            operator = '>='
            op = 'not inselect'
        query = """
                SELECT sol.product_id
                    FROM sale_order_line sol
                LEFT JOIN sale_order so
                    ON sol.order_id = so.id
                WHERE so.id = %s
                    AND sol.product_uom_qty {} %s
            """.format(operator)
        return [('id', op, (query, (order.id, value)))]

    def set_sale_catalog_quantity(self, quantity):
        order = self._get_contextual_sale_order()
        if not order or quantity and quantity < 0:
            return
        self = self.sudo()

        if order.sudo().state == 'done':
            return False
        self.sale_catalog_quantity = float_round(quantity, precision_rounding=self.uom_id.rounding)
        return True

    def sale_catalog_add_quantity(self):
        return self.set_sale_catalog_quantity(self.sudo().sale_catalog_quantity + 1)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
