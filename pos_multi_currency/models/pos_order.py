from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)
from odoo.tools import formatLang
from odoo.tools import float_is_zero



class PosOrder(models.Model):
    _inherit = "pos.order"

    custom_currency_id = fields.Many2one('res.currency', string="Original Currency")
    custom_amount_tax = fields.Float(string='Taxes', digits=0, readonly=True, required=True)
    custom_amount_total = fields.Float(string='Total', digits=0, readonly=True, required=True)
    custom_amount_paid = fields.Float(string='Paid', states={'draft': [('readonly', False)]},
                               readonly=True, digits=0, required=True)
    custom_amount_return = fields.Float(string='Returned', digits=0, required=True, readonly=True)
    custom_tip_amount = fields.Float(string='Tip Amount', digits=0, readonly=True)
    custom_conversion_rate = fields.Float(string="Conversion Rate")

    custom_margin = fields.Monetary(string="Margin", compute='_compute_custom_margin')
    custom_margin_percent = fields.Float(string="Margin (%)", compute='_compute_custom_margin', digits=(12, 4))



    def action_pos_order_invoice(self):
        custom_context = self.env.context.copy()
        if 'custom_currency_id' in custom_context.keys():
            res = super(PosOrder, self).action_pos_order_invoice()
        else:
            custom_context.update({'custom_currency_id': self.custom_currency_id.id})
            res = super(PosOrder, self.with_context(custom_context)).action_pos_order_invoice()
        return res


    def add_payment(self, data):
        if self.refunded_order_ids:
            data['custom_currency_id'] = self.refunded_order_ids.custom_currency_id.id
            data['custom_amount'] = data['amount'] * self.refunded_order_ids.custom_conversion_rate
        res = super(PosOrder, self).add_payment(data)
        return res

    @api.depends('lines.margin', 'is_total_cost_computed')
    def _compute_custom_margin(self):
        for order in self:
            if order.is_total_cost_computed:
                order.custom_margin = sum(order.lines.mapped('custom_margin'))
                amount_untaxed = order.custom_currency_id.round(sum(line.custom_price_subtotal for line in order.lines))
                order.custom_margin_percent = not float_is_zero(amount_untaxed,
                                                         precision_rounding=order.custom_currency_id.rounding) and order.custom_margin / amount_untaxed or 0
            else:
                order.custom_margin = 0
                order.custom_margin_percent = 0

    @api.model
    def create_from_ui(self, orders, draft=False):

        # All the base currency(USD) values have prefix "converted"
        # All the custom currency(currently active on POS UI) values have prefix "custom"

        order_data = orders[0]['data']
        current_user_id = orders[0]['data']['user_id']
        default_currency_id = self.env['res.users'].search([("id", "=", current_user_id)]).company_id.currency_id.id

        custom_amount_total = order_data['amount_total']
        custom_amount_paid = order_data['amount_paid']
        custom_amount_tax = order_data['amount_tax']
        custom_amount_return = int(order_data['amount_return'])
        custom_tip_amount = int(order_data['tip_amount'])

        pos_selected_currency = self.env['res.config.settings']._default_pos_config().journal_id.currency_id
        conversion_rate = pos_selected_currency.rate

        if conversion_rate != 0:
            converted_amount_total = order_data['amount_total'] / conversion_rate
            converted_amount_paid = order_data['amount_paid'] / conversion_rate
            converted_amount_tax = order_data['amount_tax'] / conversion_rate
            converted_amount_return = int(order_data['amount_return'] / conversion_rate)
            converted_tip_amount = int(order_data['tip_amount'] / conversion_rate)

            custom_order_lines = []
            converted_order_lines = []

            custom_statements = []
            converted_statements = []

            for order_line in order_data['lines']:
                custom_order_lines.append(order_line)

                order_line[2]['custom_price_unit'] = order_line[2].get('price_unit')
                order_line[2]['custom_price_subtotal'] = order_line[2].get('price_subtotal')
                order_line[2]['custom_price_subtotal_incl'] = order_line[2].get('price_subtotal_incl')
                order_line[2]['custom_discount'] = order_line[2].get('discount')
                order_line[2]['custom_price_extra'] = order_line[2].get('price_extra')
                order_line[2]['custom_currency_id'] = pos_selected_currency

                order_line[2]['price_unit'] = order_line[2].get('price_unit') / conversion_rate
                order_line[2]['price_subtotal'] = order_line[2].get('price_subtotal')/ conversion_rate
                order_line[2]['price_subtotal_incl'] = order_line[2].get('price_subtotal_incl') / conversion_rate
                order_line[2]['discount'] = order_line[2].get('discount') / conversion_rate
                order_line[2]['price_extra'] = order_line[2].get('price_extra') / conversion_rate

                converted_order_lines.append(order_line)

            for statement in order_data['statement_ids']:
                custom_statements.append(statement)
                statement[2]['custom_amount'] = statement[2].get('amount')
                statement[2]['amount'] = statement[2].get('amount') / conversion_rate
                converted_statements.append(statement)

        data = {
            'name': order_data['name'],
            'amount_paid': converted_amount_paid,
            'amount_total': converted_amount_total,
            'amount_tax': converted_amount_tax,
            'amount_return': converted_amount_return,
            'lines': converted_order_lines,
            'statement_ids': converted_statements,
            'pos_session_id': order_data['pos_session_id'],
            'pricelist_id': default_currency_id,
            'partner_id': order_data['partner_id'],
            'user_id': order_data['user_id'],
            'uid': order_data['uid'],
            'sequence_number': order_data['sequence_number'],
            'creation_date': order_data['creation_date'],
            'fiscal_position_id': order_data['fiscal_position_id'],
            'server_id': order_data['server_id'],
            'to_invoice': order_data['to_invoice'],
            'to_ship': order_data['to_ship'],
            'is_tipped': order_data['is_tipped'],
            'tip_amount': converted_tip_amount,
            'access_token': order_data['access_token']
        }

        orders[0]['data'] = data

        res_config_settings = self.env['res.config.settings']
        default_pos_config = res_config_settings._default_pos_config()
        default_pos_config.journal_id.write({"currency_id": default_currency_id})

        custom_context = self.env.context.copy()
        custom_context.update({'custom_currency_id': pos_selected_currency.id})
        order_ids = super(PosOrder, self.with_context(custom_context)).create_from_ui(orders, draft)
        # self.env["account.move"].browse(order_ids[0]['account_move']).journal_id.write({"currency_id": 2})
        print("order_ids", order_ids)
        order_id = order_ids[0].get("id")
        pos_order = self.env["pos.order"].browse(order_id)
        if pos_order.exists:
            pos_order.write({
                'custom_amount_paid': custom_amount_paid,
                'custom_amount_return': custom_amount_return,
                'custom_amount_tax': custom_amount_tax,
                'custom_amount_total': custom_amount_total,
                'custom_tip_amount': custom_tip_amount,
                'custom_conversion_rate': conversion_rate,
                'custom_currency_id': pos_selected_currency
            })

            for index, payment_id in enumerate(pos_order.payment_ids):
                payment_id.write({"custom_amount": converted_statements[index][2].get('custom_amount')})

        return order_ids
        # default_pos_config.journal_id.write({"currency_id": pos_selected_currency.id})

    def _apply_invoice_payments(self):
        custom_currency_id = self.env.context.get('custom_currency_id')
        custom_context = self.env.context.copy()
        if self.refunded_order_ids:
            custom_context.update({'custom_conversion_rate': self.refunded_order_ids.custom_conversion_rate})
        else:
            custom_currency_id = self.env['res.currency'].browse(custom_currency_id)
            custom_context.update({'custom_conversion_rate': custom_currency_id.rate})
        move = super(PosOrder, self.with_context(custom_context))._apply_invoice_payments()
        move.write({'custom_currency_id': custom_currency_id})
        for line in move.invoice_line_ids:
            line.write({'custom_currency_id': custom_currency_id})
        return move




    def _prepare_invoice_line(self, order_line):
        res = super(PosOrder, self)._prepare_invoice_line(order_line)
        res['custom_price_unit'] = order_line.custom_price_unit
        res['custom_price_subtotal'] = order_line.custom_price_subtotal
        if order_line.custom_currency_id:
            res['custom_currency_id'] = order_line.custom_currency_id.id
        else:
            res['custom_currency_id'] = self.env.context.get('custom_currency_id')
        # res['custom_price_total'] = order_line.price_total * order_line.currency_id.rate
        return res

    def _create_invoice(self, move_vals):
        custom_currency_id = move_vals['invoice_line_ids'][0][2]['custom_currency_id']
        move_vals.update({'custom_currency_id': custom_currency_id})
        custom_context = self.env.context.copy()
        custom_currency_id = self.env['res.currency'].browse(custom_currency_id)

        if self.refunded_order_ids:
            custom_context.update({'custom_conversion_rate': self.refunded_order_ids.custom_conversion_rate})
        else:
            custom_context.update({'custom_conversion_rate': custom_currency_id.rate})
        move = super(PosOrder, self.with_context(custom_context))._create_invoice(move_vals)
        for journal_item in move.line_ids - move.invoice_line_ids:
            journal_item.write({'custom_currency_id': move.custom_currency_id.id})
        return move



class AccountMove(models.Model):
    _inherit = "account.move"

    custom_tax_totals = fields.Binary(
        string="Invoice Totals",
        compute='_custom_compute_tax_totals',
        store=False,
        help='Edit Tax amounts if you encounter rounding issues.',
        exportable=False,
    )

    custom_currency_id = fields.Many2one('res.currency', string='Currency')

    custom_invoice_payments_widget = fields.Binary(
        groups="account.group_account_invoice,account.group_account_readonly",
        compute='_custom_compute_payments_widget_reconciled_info',
        exportable=False,
    )

    custom_amount_residual = fields.Monetary(
        string='Amount Due',
        compute='_custom_compute_amount', store=True,
    )

    custom_conversion_rate = fields.Float(string="Conversion Rate", compute='_custom_compute_conversion_rate', store=True)

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state')
    def _custom_compute_amount(self):
        for move in self:
            # move._compute_amount()
            move.custom_amount_residual = move.custom_conversion_rate * move.amount_residual


    @api.depends_context('lang')
    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id',
    )
    def _custom_compute_tax_totals(self):
        for rec in self:
            #rec._compute_tax_totals()
            if rec.custom_currency_id and rec.tax_totals:
                rec.custom_tax_totals = rec.tax_totals
                rec.custom_tax_totals['amount_total'] = rec.tax_totals['amount_total'] * rec.custom_conversion_rate
                rec.custom_tax_totals['amount_untaxed'] = rec.tax_totals['amount_untaxed'] * rec.custom_conversion_rate
                custom_formatted_amount_total = formatLang(rec.env, rec.custom_tax_totals['amount_total'],
                                                           currency_obj=rec.custom_currency_id)
                custom_formatted_amount_untaxed = formatLang(rec.env, rec.custom_tax_totals['amount_untaxed'],
                                                             currency_obj=rec.custom_currency_id)

                rec.custom_tax_totals['formatted_amount_total'] = custom_formatted_amount_total
                rec.custom_tax_totals['formatted_amount_untaxed'] = custom_formatted_amount_untaxed

            else:
                rec.custom_tax_totals = rec.tax_totals

    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id',
    )
    def _custom_compute_conversion_rate(self):
        for record in self:
            if 'custom_conversion_rate' in self.env.context.keys():
                record.custom_conversion_rate = self.env.context.get('custom_conversion_rate')
            else:
                record.custom_conversion_rate = record.custom_currency_id.rate


    def _custom_get_all_reconciled_invoice_partials(self):
        self.ensure_one()
        reconciled_lines = self.line_ids.filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
        if not reconciled_lines:
            return {}

        self.env['account.partial.reconcile'].flush_model([
            'credit_amount_currency', 'credit_move_id', 'debit_amount_currency',
            'debit_move_id', 'exchange_move_id',
        ])
        query = '''
            SELECT
                part.id,
                part.exchange_move_id,
                part.debit_amount_currency AS amount,
                part.credit_move_id AS counterpart_line_id
            FROM account_partial_reconcile part
            WHERE part.debit_move_id IN %s

            UNION ALL

            SELECT
                part.id,
                part.exchange_move_id,
                part.credit_amount_currency AS amount,
                part.debit_move_id AS counterpart_line_id
            FROM account_partial_reconcile part
            WHERE part.credit_move_id IN %s
        '''
        self._cr.execute(query, [tuple(reconciled_lines.ids)] * 2)

        partial_values_list = []
        counterpart_line_ids = set()
        exchange_move_ids = set()
        for values in self._cr.dictfetchall():
            partial_values_list.append({
                'aml_id': values['counterpart_line_id'],
                'partial_id': values['id'],
                'amount': values['amount'],
                'currency': self.custom_currency_id,
            })
            counterpart_line_ids.add(values['counterpart_line_id'])
            if values['exchange_move_id']:
                exchange_move_ids.add(values['exchange_move_id'])

        if exchange_move_ids:
            self.env['account.move.line'].flush_model(['move_id'])
            query = '''
                SELECT
                    part.id,
                    part.credit_move_id AS counterpart_line_id
                FROM account_partial_reconcile part
                JOIN account_move_line credit_line ON credit_line.id = part.credit_move_id
                WHERE credit_line.move_id IN %s AND part.debit_move_id IN %s

                UNION ALL

                SELECT
                    part.id,
                    part.debit_move_id AS counterpart_line_id
                FROM account_partial_reconcile part
                JOIN account_move_line debit_line ON debit_line.id = part.debit_move_id
                WHERE debit_line.move_id IN %s AND part.credit_move_id IN %s
            '''
            self._cr.execute(query, [tuple(exchange_move_ids), tuple(counterpart_line_ids)] * 2)

            for values in self._cr.dictfetchall():
                counterpart_line_ids.add(values['counterpart_line_id'])
                partial_values_list.append({
                    'aml_id': values['counterpart_line_id'],
                    'partial_id': values['id'],
                    'currency': self.custom_currency_id,
                })

        counterpart_lines = {x.id: x for x in self.env['account.move.line'].browse(counterpart_line_ids)}
        for partial_values in partial_values_list:
            partial_values['aml'] = counterpart_lines[partial_values['aml_id']]
            partial_values['is_exchange'] = partial_values['aml'].move_id.id in exchange_move_ids
            if partial_values['is_exchange']:
                partial_values['amount'] = abs(partial_values['aml'].balance)

        return partial_values_list





    @api.depends('move_type', 'line_ids.amount_residual')
    def _custom_compute_payments_widget_reconciled_info(self):
        for move in self:
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}

            if move.state == 'posted' and move.is_invoice(include_receipts=True):
                reconciled_vals = []
                reconciled_partials = move._custom_get_all_reconciled_invoice_partials()
                for reconciled_partial in reconciled_partials:
                    counterpart_line = reconciled_partial['aml']
                    if counterpart_line.move_id.ref:
                        reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
                    else:
                        reconciliation_ref = counterpart_line.move_id.name
                    if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
                        foreign_currency = counterpart_line.currency_id
                    else:
                        foreign_currency = False

                    reconciled_vals.append({
                        'name': counterpart_line.name,
                        'journal_name': counterpart_line.journal_id.name,
                        'amount': reconciled_partial['amount'] * move.custom_conversion_rate,
                        'currency_id': move.custom_currency_id.id if reconciled_partial['is_exchange'] else
                        reconciled_partial['currency'].id,
                        'date': counterpart_line.date,
                        'partial_id': reconciled_partial['partial_id'],
                        'account_payment_id': counterpart_line.payment_id.id,
                        'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
                        'move_id': counterpart_line.move_id.id,
                        'ref': reconciliation_ref,
                        # these are necessary for the views to change depending on the values
                        'is_exchange': reconciled_partial['is_exchange'],
                        'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance * counterpart_line.custom_conversion_rate),
                                                              currency_obj=counterpart_line.custom_currency_id),
                        'amount_foreign_currency': foreign_currency and formatLang(self.env,
                                                                                   abs(counterpart_line.amount_currency) * counterpart_line.custom_conversion_rate,
                                                                                   currency_obj=foreign_currency)
                    })
                payments_widget_vals['content'] = reconciled_vals

            if payments_widget_vals['content']:
                move.custom_invoice_payments_widget = payments_widget_vals
            else:
                move.custom_invoice_payments_widget = False



    @api.model_create_multi
    def create(self, vals_list):
        if vals_list:
            if vals_list[0].get('invoice_user_id'):
                invoice_user_id = vals_list[0]['invoice_user_id']
                default_currency_id = self.env['res.users'].search([("id", "=", invoice_user_id)]).company_id.currency_id.id
                vals_list[0]['currency_id'] = default_currency_id
        res = super(AccountMove, self).create(vals_list)
        return res


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    custom_price_subtotal = fields.Float(string='Subtotal w/o Tax', digits=0, readonly=True, required=True)
    custom_price_subtotal_incl = fields.Float(string='Subtotal', digits=0, readonly=True, required=True)
    custom_price_unit = fields.Float(string='Unit Price', digits=0)
    custom_price_extra = fields.Float(string="Price extra")
    custom_discount = fields.Float(string='Discount (%)', digits=0, default=0.0)
    custom_currency_id = fields.Many2one(related='order_id.custom_currency_id', string="Selected Currency")
    custom_margin = fields.Monetary(string="Margin", compute='_compute_custom_margin')
    custom_total_cost = fields.Float(string='Total cost', compute='_compute_custom_total_cost', digits='Product Price', readonly=True)
    custom_margin_percent = fields.Float(string="Margin (%)", compute='_compute_custom_margin', digits=(12, 4))
    custom_conversion_rate = fields.Float(string="Conversion Rate", related='custom_currency_id.rate', store=True)

    @api.depends('price_subtotal', 'total_cost')
    def _compute_custom_total_cost(self):
        for line in self:
            line.custom_total_cost = line.total_cost * line.custom_conversion_rate

    @api.depends('price_subtotal', 'total_cost')
    def _compute_custom_margin(self):
        for line in self:
            line.custom_margin = line.custom_price_subtotal - line.custom_total_cost
            line.custom_margin_percent = not float_is_zero(line.custom_price_subtotal,
                                                    precision_rounding=line.custom_currency_id.rounding) and line.custom_margin / line.custom_price_subtotal or 0


class PosPayment(models.Model):
    _inherit = "pos.payment"

    custom_amount = fields.Monetary(string='Amount', required=True, currency_field='custom_currency_id', readonly=True,
                                    help="Total amount of the payment.")
    custom_currency_id = fields.Many2one('res.currency', string='Currency', related='pos_order_id.custom_currency_id')
    custom_conversion_rate = fields.Float(string="Conversion Rate", related='custom_currency_id.rate', store=True)



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    custom_currency_id = fields.Many2one('res.currency', string='Currency')

    custom_price_unit = fields.Float(
        string='Unit Price',
        readonly=False,
        digits='Product Price',
    )
    custom_price_subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='custom_currency_id',
    )

    custom_price_total = fields.Monetary(
        string='Total',
        currency_field='custom_currency_id',
    )

    custom_debit = fields.Monetary(
        string='Debit',
        compute='_compute_custom_debit_credit', inverse='_inverse_custom_debit', store=True, precompute=True,
        currency_field='custom_currency_id',
    )
    custom_credit = fields.Monetary(
        string='Credit',
        compute='_compute_custom_debit_credit', inverse='_inverse_custom_credit', store=True, precompute=True,
        currency_field='custom_currency_id',
    )

    custom_amount_currency = fields.Monetary(
        string='Amount in Currency',
        group_operator=None,
        compute='_compute_custom_amount_currency', inverse='_inverse_amount_currency', store=True, readonly=False,
        precompute=True,
        help="The amount expressed in an optional other currency if it is a multi-currency entry.")

    custom_conversion_rate = fields.Float(string="Conversion Rate", compute='_custom_compute_conversion_rate', store=True)

    @api.depends('currency_rate', 'balance')
    def _custom_compute_conversion_rate(self):
        for record in self:
            if 'custom_conversion_rate' in self.env.context.keys():
                record.custom_conversion_rate = self.env.context.get('custom_conversion_rate')
            else:
                record.custom_conversion_rate = record.custom_currency_id.rate

    @api.depends('currency_rate', 'balance')
    def _compute_custom_amount_currency(self):
        custom_currency_id = self.env.context.get('custom_currency_id')
        custom_currency_id = custom_currency_id = self.env['res.currency'].sudo().browse(custom_currency_id)
        custom_conversion_rate = custom_currency_id.rate
        for line in self:
            if line.custom_conversion_rate:
                custom_conversion_rate = line.custom_conversion_rate
            if line.custom_amount_currency is False:
                line.custom_amount_currency = custom_conversion_rate * (line.currency_id.round(line.balance * line.currency_rate))
            if line.currency_id == line.company_id.currency_id:
                line.custom_amount_currency = custom_conversion_rate * line.balance

        # for line in self:
        #     line._compute_amount_currency()
        #     line.custom_amount_currency = line.amount_currency * line.custom_currency_id.rate

    @api.onchange('debit')
    def _inverse_custom_debit(self):
        for line in self:
            if line.debit:
                line.custom_credit = 0
            line.balance = line.debit - line.credit

    @api.onchange('credit')
    def _inverse_custom_credit(self):
        for line in self:
            if line.credit:
                line.custom_debit = 0
            line.balance = line.debit - line.credit

    @api.depends('balance', 'move_id.is_storno')
    def _compute_custom_debit_credit(self):
        for line in self:
            if line.custom_conversion_rate:
                custom_conversion_rate = line.custom_conversion_rate
            else:
                custom_currency_id = line.custom_currency_id.id or line.move_id.custom_currency_id.id or self.env.context.get('custom_currency_id')
                custom_currency_id = self.env['res.currency'].sudo().browse(custom_currency_id)
                custom_conversion_rate = custom_currency_id.rate

            #line._compute_debit_credit()
            # custom_currency_id = line.custom_currency_id.id or line.move_id.custom_currency_id.id or self.env.context.get('custom_currency_id')
            # custom_currency_id = self.env['res.currency'].sudo().browse(custom_currency_id)
            if not line.is_storno:
                line.custom_debit = line.debit * custom_conversion_rate
                line.custom_credit = line.credit * custom_conversion_rate
            else:
                line.custom_debit = line.debit * custom_conversion_rate
                line.custom_credit = line.credit * custom_conversion_rate




class pos_make_payment(models.TransientModel):
    _inherit = 'pos.make.payment'


    def _custom_default_amount(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            order = self.env['pos.order'].browse(active_id)
            return (order.amount_total - order.amount_paid) * order.custom_conversion_rate
        return False

    custom_amount = fields.Float(digits=0, required=True, default=_custom_default_amount)

