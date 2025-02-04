from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    always_internal_transfer = fields.Boolean()
    counter_part_internal_transfer = fields.Boolean()
    show_destino = fields.Boolean(compute='_compute_show_currency_amount')
    currency_destino_id = fields.Many2one(comodel_name='res.currency', string='Moneda Destino')
    amount_destino = fields.Monetary(string='Importe Moneda Destino', currency_field='currency_destino_id')

    @api.depends('destination_journal_id', 'journal_id')
    def _compute_show_currency_amount(self):
        for rec in self:
            if rec.destination_journal_id and rec.journal_id and rec.destination_journal_id.currency_id.id != rec.journal_id.currency_id.id:
                rec.show_destino = True
            else:
                rec.show_destino = False

    @api.onchange('is_internal_transfer')
    def change_payment_type(self):
        for rec in self:
            if rec.is_internal_transfer:
                rec.payment_type = 'outbound'

    def _create_paired_internal_transfer_payment(self):
        ''' When an internal transfer is posted, a paired payment is created
        with opposite payment_type and swapped journal_id & destination_journal_id.
        Both payments liquidity transfer lines are then reconciled.
        '''
        for payment in self:
            payment_destination_currency_id = payment.destination_journal_id.currency_id or payment.destination_journal_id.company_id.currency_id
            paired_payment = payment.paired_internal_transfer_payment_id
            if not payment.paired_internal_transfer_payment_id:
                paired_payment = payment.copy({
                    'journal_id': payment.destination_journal_id.id,
                    'destination_journal_id': payment.journal_id.id,
                    'currency_id': payment_destination_currency_id.id,
                    'amount': payment.amount if not payment.amount_destino else payment.amount_destino,
                    'amount_destino': payment.amount if payment.amount_destino else 0,
                    'currency_destino_id': payment.currency_id.id if payment.amount_destino and payment.currency_destino_id else None,
                    'payment_type': 'inbound',
                    'move_id': False,
                    'ref': payment.ref,
                    'paired_internal_transfer_payment_id': payment.id,
                    'counter_part_internal_transfer': True,
                    'date': payment.date,
                })
            paired_payment.move_create_custom(payment)
            paired_payment.move_id._post(soft=False)
            payment.paired_internal_transfer_payment_id = paired_payment
            body = _("This payment has been created from:") + payment._get_html_link()
            paired_payment.message_post(body=body)
            body = _("A second payment has been created:") + paired_payment._get_html_link()
            payment.message_post(body=body)

            lines = (payment.move_id.line_ids + paired_payment.move_id.line_ids).filtered(
                lambda l: l.account_id == payment.destination_account_id and not l.reconciled)
            lines.reconcile()

    @api.depends('journal_id')
    def change_journal_is_internal_transfer(self):
        for payment in self:
            if payment.always_internal_transfer:
                raise ValidationError(
                    _("No puede editar el diario de un movimiento de cuenta si se ha publicado una vez"))

    def action_draft(self):
        for rec in self:
            rec = rec.with_context(force_delete=True)
            if rec.is_internal_transfer and not rec.counter_part_internal_transfer:
                rec.paired_internal_transfer_payment_id.action_draft()
            rec.always_internal_transfer = True
        res = super(AccountPayment, self).action_draft()
        return res

    def action_cancel(self):
        for rec in self:
            if rec.is_internal_transfer and not rec.counter_part_internal_transfer:
                rec.paired_internal_transfer_payment_id.action_cancel()
        res = super(AccountPayment, self).action_cancel()
        return res

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.is_internal_transfer and not rec.counter_part_internal_transfer:
                rec.paired_internal_transfer_payment_id.with_context(edit_main=True).write(vals)
        return res

    def action_post(self):
        move_ids = []
        for rec in self:
            if rec.is_internal_transfer:
                rec.create_modif_account_lines(rec, move_ids)
            if rec.is_internal_transfer and not rec.counter_part_internal_transfer and rec.paired_internal_transfer_payment_id:
                payment_destination_currency_id = rec.destination_journal_id.currency_id or rec.destination_journal_id.company_id.currency_id
                paired_payment = {
                    'currency_id': payment_destination_currency_id.id,
                    'amount': rec.amount if not rec.amount_destino else rec.amount_destino,
                    'amount_destino': rec.amount if rec.amount_destino else 0,
                    'currency_destino_id': rec.currency_id.id if rec.amount_destino and rec.currency_destino_id else None,
                    'ref': rec.ref,
                    'paired_internal_transfer_payment_id': rec.id,
                    'counter_part_internal_transfer': True,
                    'date': rec.date,
                }
                rec.paired_internal_transfer_payment_id.write(paired_payment)
                rec.paired_internal_transfer_payment_id.action_post()
        res = super(AccountPayment, self).action_post()
        for rec in self:
            if rec.is_internal_transfer:
                if rec.paired_internal_transfer_payment_id:
                    move_ids += rec.paired_internal_transfer_payment_id.move_id
        return res

    def create_modif_account_lines(self, rec, move_ids):
        move_values = {'line_ids': []}
        partner_type = rec.partner_type
        normal_payment = (partner_type == 'customer' and rec.payment_type == 'inbound') or (
                    partner_type == 'supplier' and rec.payment_type == 'outbound')
        currency_id = rec.journal_id.currency_id or rec.journal_id.company_id.currency_id
        company_currency_id = rec.company_currency_id
        foreign_amount = rec.amount
        foreign_currency = currency_id
        if rec.currency_id != company_currency_id:
            local_currency = rec.amount * rec.currency_id.rate
            foreign_amount = rec.amount
        else:
            local_currency = rec.amount
            if company_currency_id != currency_id:
                foreign_currency = currency_id
            elif rec.destination_journal_id.currency_id != currency_id:
                foreign_currency = rec.destination_journal_id.currency_id
            else:
                foreign_currency = rec.currency_id
                foreign_amount = company_currency_id._convert(rec.amount, foreign_currency,
                                                              rec.company_id, rec.date)
        if company_currency_id != currency_id:
            amount_company_currency = local_currency
            amount = foreign_amount
        else:
            amount_company_currency = local_currency
            amount = local_currency

        for line in rec.move_id.line_ids:
            value = {}
            if line == rec.move_id.line_ids[0]:
                if currency_id != rec.company_currency_id:
                    value['amount_currency'] = -amount
                    value['currency_id'] = currency_id.id
                else:
                    value['amount_currency'] = -amount_company_currency
                    value['currency_id'] = rec.company_currency_id.id
                value['account_id'] = rec.journal_id.default_account_id.id
                if normal_payment:
                    value['debit'] = 0
                    value['credit'] = amount_company_currency
                else:
                    value['debit'] = amount_company_currency
                    value['credit'] = 0
                    value['amount_currency'] = -value['amount_currency']
            else:
                transfer_account_id = rec.journal_id.company_id.transfer_account_id
                if not transfer_account_id:
                    raise ValidationError(_('No se encontró cuenta de transferencia interna en la compañía.'))
                if currency_id != rec.company_currency_id:
                    value['amount_currency'] = amount
                    value['currency_id'] = currency_id.id
                else:
                    value['amount_currency'] = amount_company_currency
                    value['currency_id'] = rec.company_currency_id.id
                value['account_id'] = transfer_account_id.id
                if normal_payment:
                    value['debit'] = amount_company_currency
                    value['credit'] = 0
                else:
                    value['debit'] = 0
                    value['credit'] = amount_company_currency
                    value['amount_currency'] = -value['amount_currency']

            move_values['line_ids'].append((1, line.id, value))
        rec.move_id.write(move_values)
        move_ids = rec.move_id

    def move_create_custom(self, payment):
        for paired_payment in self:
            move_values = {'line_ids': []}
            currency_id = paired_payment.journal_id.currency_id or paired_payment.journal_id.company_id.currency_id
            company_currency_id = paired_payment.company_currency_id
            local_currency = abs(payment.move_id.line_ids[0].balance)
            if paired_payment.currency_id != company_currency_id:
                foreign_amount = paired_payment.amount
            else:
                foreign_amount = company_currency_id._convert(paired_payment.amount,
                                                              paired_payment.destination_journal_id.currency_id,
                                                              paired_payment.company_id,
                                                              paired_payment.date)
            if company_currency_id != currency_id and (paired_payment.currency_destino_id == paired_payment.company_currency_id or paired_payment.currency_id == paired_payment.company_currency_id):
                amount_company_currency = local_currency
                amount = foreign_amount
            elif company_currency_id != currency_id and paired_payment.currency_destino_id != paired_payment.company_currency_id and paired_payment.currency_id != paired_payment.company_currency_id:
                amount = paired_payment.amount_destino * (paired_payment.currency_destino_id.rate / paired_payment.currency_id.rate)
                amount_company_currency = amount * paired_payment.currency_id.rate
            else:
                amount_company_currency = local_currency
                amount = local_currency
            for line in paired_payment.move_id.line_ids:
                value = {}
                if line == paired_payment.move_id.line_ids[0]:
                    if paired_payment.journal_id.currency_id != paired_payment.destination_journal_id.currency_id:
                        if currency_id != paired_payment.company_currency_id:
                            value['amount_currency'] = amount
                            value['currency_id'] = currency_id.id
                        else:
                            value['amount_currency'] = amount_company_currency
                            value['currency_id'] = paired_payment.company_currency_id.id
                    else:
                        value['amount_currency'] = paired_payment.amount
                        value['currency_id'] = paired_payment.currency_id.id
                        if paired_payment.currency_id != paired_payment.company_currency_id:
                            amount_company_currency = paired_payment.currency_id._convert(paired_payment.amount,
                                                                                          company_currency_id,
                                                                                          paired_payment.company_id,
                                                                                          paired_payment.date)
                    payment_account = paired_payment.move_id.line_ids[0].account_id
                    value['debit'] = amount_company_currency
                    value['credit'] = 0
                    value['account_id'] = payment_account.id
                else:
                    transfer_account_id = paired_payment.journal_id.company_id.transfer_account_id
                    if not transfer_account_id:
                        raise ValidationError(_('No se encontró cuenta de transferencia interna en la compañía.'))
                    if paired_payment.journal_id.currency_id != paired_payment.destination_journal_id.currency_id:
                        if currency_id != paired_payment.company_currency_id:
                            value['amount_currency'] = -amount
                            value['currency_id'] = currency_id.id
                        else:
                            value['amount_currency'] = -amount_company_currency
                            value['currency_id'] = paired_payment.company_currency_id.id
                    else:
                        value['amount_currency'] = -paired_payment.amount
                        value['currency_id'] = paired_payment.currency_id.id
                        if paired_payment.currency_id != paired_payment.company_currency_id:
                            amount_company_currency = paired_payment.currency_id._convert(paired_payment.amount,
                                                                                          company_currency_id,
                                                                                          paired_payment.company_id,
                                                                                          paired_payment.date)
                    value['account_id'] = transfer_account_id.id
                    value['debit'] = 0
                    value['credit'] = amount_company_currency
                move_values['line_ids'].append((1, line.id, value))
            paired_payment.move_id.write(move_values)
