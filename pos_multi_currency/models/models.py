from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.constrains('pricelist_id', 'use_pricelist', 'available_pricelist_ids', 'journal_id', 'invoice_journal_id', 'payment_method_ids')
    def _check_currencies(self):
        journal = self.env['account.journal'].search([('name', '=', 'Point of Sale')])
        currency = journal.currency_id
        if self.pricelist_id.currency_id != currency:
            pricelist = self.env['product.pricelist'].search([('currency_id', '=', currency.id)])[0]
            self.pricelist_id = pricelist
        for config in self:
            if config.use_pricelist and config.pricelist_id not in config.available_pricelist_ids:
                raise ValidationError(_("The default pricelist must be included in the available pricelists."))
        if self.invoice_journal_id.currency_id and self.invoice_journal_id.currency_id != self.currency_id:
            raise ValidationError(_("The invoice journal must be in the same currency as the Sales Journal or the company currency if that is not set."))

    def set_pricelist(self, currency_id):
        res_config_settings = self.env['res.config.settings']
        default_pos_config = res_config_settings._default_pos_config()
        default_pos_config.journal_id.write({"currency_id": currency_id})



#
# class PosOrder(models.Model):
#     _inherit = "pos.order"
#
#     total_amount_compute = fields.Float(string="Total Amount", compute='_total_amount_compute', store=False)
#     currency_converted = fields.Boolean(store=True, default=False)
    # converted_orders = []

    # @api.onchange('payment_ids', 'lines')
    # def _onchange_amount_all(self):
    #     for order in self:
    #         if not order.pricelist_id.currency_id:
    #             raise UserError(
    #                 _("You can't: create a pos order from the backend interface, or unset the pricelist, or create a pos.order in a python test with Form tool, or edit the form view in studio if no PoS order exist"))
    #         currency = order.pricelist_id.currency_id
    #         order.amount_paid = sum(payment.amount for payment in order.payment_ids)
    #         order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.payment_ids)
    #         order.amount_tax = currency.round(
    #             sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
    #         amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
    #         order.amount_total = order.amount_tax + amount_untaxed

    # @api.onchange('payment_ids', 'lines')
    # def _total_amount_compute(self):
    #     for order in self:
    #         if not order.currency_converted:
    #             if order.pricelist_id.currency_id.id != 2:
    #                 print(order)
    #                 pricelist_rate = order.pricelist_id.currency_id.rate
    #                 for line in order.lines:
    #                     unit_price = line.price_unit / pricelist_rate
    #                     line.write({'price_unit': unit_price})
    #                     res = line._compute_amount_line_all()
    #                     line.update(res)
    #                 for payment in order.payment_ids:
    #                     payment_amount = payment.amount / pricelist_rate
    #                     payment.write({'amount': payment_amount})
    #                 # for move in order.session_move_id.line_ids:
    #                 #     if move.credit != 0:
    #                 #         move_amount = move.credit / pricelist_rate
    #                 #         move.with_context(check_move_validity=False).write({'credit': move_amount})
    #                 #     else:
    #                 #         move_amount = move.debit / pricelist_rate
    #                 #         move.with_context(check_move_validity=False).write({'debit': move_amount})
    #                 # order.session_move_id.line_ids._compute_debit_credit()
    #                 currency = order.pricelist_id.currency_id
    #                 order.amount_paid = sum(payment.amount for payment in order.payment_ids)
    #                 order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.payment_ids)
    #                 order.amount_tax = currency.round(
    #                     sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
    #                 amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
    #                 order.amount_total = order.amount_tax + amount_untaxed
    #                 order.currency_converted = True
    #                 order.total_amount_compute = order.amount_total
    #             else:
    #                 order.currency_converted = True
    #                 order.total_amount_compute = order.amount_total
    #         else:
    #             order.total_amount_compute = order.amount_total


        # for order in self:
        #     if not order.pricelist_id.currency_id:
        #         raise UserError(
        #             _("You can't: create a pos order from the backend interface, or unset the pricelist, or create a pos.order in a python test with Form tool, or edit the form view in studio if no PoS order exist"))
        #     currency = order.pricelist_id.currency_id
        #     order.amount_paid = sum(payment.amount for payment in order.payment_ids)
        #     order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.payment_ids)
        #     order.amount_tax = currency.round(
        #         sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
        #     amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
        #     order.amount_total = order.amount_tax + amount_untaxed
        #     order.total_amount_compute = order.amount_total

class PosSession(models.Model):
    _inherit = 'pos.session'

    def close_session_from_ui(self, bank_payment_method_diff_pairs=None):
        journal = self.env['account.journal'].search([('name', '=', 'Point of Sale')])
        currency = self.env['res.currency'].search([('name', '=', 'USD')])
        # journal.currency_id = currency
        journal.write({"currency_id": currency})

        res = super(PosSession, self).close_session_from_ui()
        return res

#
# class AccountMove(models.Model):
#     _inherit = "account.move"
#
#     currency_converted_move_custom = fields.Boolean(store=True, default=False)
#     total_amount_move_custom = fields.Float(string="Total Amount", compute='_compute_total_amount_move', store=False)
#     # currency_converted = fields.Boolean(store=True, default=False)
#
#     @api.depends('journal_id', 'amount_total_signed')
#     def _compute_total_amount_move(self):
#         # print(self)
#         # pos_moves = self.search([('ref', 'ilike', 'pos')])
#         # for move in pos_moves:
#         #     move.total_amount_move_custom = move.amount_total_signed
#         pos_orders = self.env['pos.order']
#         for move in self:
#             if 'POS' in move.display_name and pos_orders.search([('session_move_id', '=', move.name)]):
#                 move.total_amount_move_custom = move.amount_total_signed
#             else:
#                 move.total_amount_move_custom = move.amount_total_signed
