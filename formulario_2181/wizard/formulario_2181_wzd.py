# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from dateutil.relativedelta import relativedelta
from io import StringIO
import base64

TIPO_DOC_RUT = 2


class account_line_beta_wzd(models.TransientModel):
    _name = 'account.line.beta.wzd'
    _rec_name = 'month'

    _group_results = []

    def add_to_file(self, result_item, file_output):
        data = []
        line_amount = "{:.2f}".format(result_item['amount'])
        data.append(result_item['vat'].zfill(12))  # Company VAT
        data.append(result_item['form'].zfill(5))  # Form hardcode
        data.append(result_item['year_month'])  # Wizard yearmonth
        data.append(result_item['rut'].zfill(12))
        data.append(result_item['date_invoice'])  # Invoice yearmonth
        data.append(result_item['line_beta'])  # Line beta
        data.append(line_amount)  # Tax Line Amount
        record = ""
        for line in data:
            record += line + " "
        # file_output.write(record[:-1]+"\n")
        file_output.write(record + "\n")

    def action_next(self):
        row = self.browse(self.id)
        delta = relativedelta(months=-1, day=1)
        _date = datetime.strptime("01-%s-%s" % (row['month'], row['year']), "%d-%m-%Y").date()
        file_to_save = StringIO()
        not_result = True
        self._group_results = []
        fecha_fin = datetime.strftime(_date - delta, DATE_FORMAT)

        ac_move_line_obj = self.env["account.move.line"]
        ac_move_line_ids = ac_move_line_obj.search(
            [('move_id.state', '=', 'posted'), ('move_id.date', '>=', datetime.strftime(_date, DATE_FORMAT)),
             ('move_id.date', '<', fecha_fin)])
        user = self.env["res.users"].browse(self._uid)
        company_id = user.company_id.id
        if ac_move_line_ids:

            def _do_action(self, ac_move_line, line_beta):
                _found = False
                rut = ac_move_line.partner_id.vat[2:] if ac_move_line.partner_id.vat else ""
                if rut:
                    if len(ac_move_line.partner_id.vat) > 11:
                        rut = ac_move_line.partner_id.vat[2:]
                    else:
                        rut = ac_move_line.partner_id.vat if ac_move_line.partner_id.vat else ""
                for _r in self._group_results:
                    # if _r.get('partner_id', False) == ac_tax_line.invoice_id.partner_id.id \
                    if _r.get('vat', False) == ac_move_line.company_id.vat[2:] \
                            and _r.get('rut', False) == rut \
                            and _r.get('line_beta', False) == line_beta:
                        if ac_move_line.debit != 0.0:
                            debit = ac_move_line.debit
                            if 'check_rate' in ac_move_line._fields and 'rate_exchange' in ac_move_line._fields:
                                rate = ac_move_line.rate_exchange
                            else:
                                tipo_cambio = self.env['res.currency.rate'].search(
                                    [('name', '<=', ac_move_line.move_id.date), ('currency_id', '=', 2)], limit=1)
                                rate = tipo_cambio.inverserate
                            if ac_move_line.currency_id and ac_move_line.currency_id.name == 'USD' and ac_move_line.amount_currency != 0:
                                if rate:
                                    debit = ac_move_line.amount_currency * rate
                                else:
                                    debit = ac_move_line.amount_currency
                            # if ac_move_line.invoice_id:
                            if ac_move_line.move_id.is_invoice():
                                if ac_move_line.move_id.type in ('in_refund', 'out_refund'):
                                    _r['amount'] -= debit
                                else:
                                    _r['amount'] += debit
                            else:
                                _r['amount'] += debit
                        elif ac_move_line.credit != 0.0:
                            credit = ac_move_line.credit
                            if 'check_rate' in ac_move_line._fields and 'ac_move_line' in ac_move_line._fields:
                                rate = ac_move_line.rate_exchange
                            else:
                                tipo_cambio = self.env['res.currency.rate'].search(
                                    [('name', '<=', ac_move_line.move_id.date), ('currency_id', '=', 2)], limit=1)
                                rate = tipo_cambio.inverserate
                            if ac_move_line.currency_id and ac_move_line.currency_id.name == 'USD' and ac_move_line.amount_currency != 0:
                                if rate:
                                    credit = -ac_move_line.amount_currency * rate

                                else:
                                    credit = -ac_move_line.amount_currency

                            if ac_move_line.move_id.is_invoice():
                                if ac_move_line.move_id.type in ('in_refund', 'out_refund'):
                                    _r['amount'] -= credit
                                else:
                                    _r['amount'] += credit
                            else:
                                _r['amount'] -= credit
                        _r['amount'] = _r['amount']
                        _found = True
                        break
                if not _found:
                    am = 0
                    if ac_move_line.debit != 0.0:
                        debit = ac_move_line.debit
                        if 'check_rate' in ac_move_line._fields and 'ac_move_line' in ac_move_line._fields:
                            rate = ac_move_line.rate_exchange
                        else:
                            tipo_cambio = self.env['res.currency.rate'].search(
                                [('name', '<=', ac_move_line.move_id.date), ('currency_id', '=', 2)], limit=1)
                            rate = tipo_cambio.inverserate
                        if ac_move_line.currency_id and ac_move_line.currency_id.name == 'USD' and ac_move_line.amount_currency != 0:
                            if rate:
                                debit = ac_move_line.amount_currency * rate
                            else:
                                debit = ac_move_line.amount_currency
                        if ac_move_line.move_id.is_invoice():
                            if ac_move_line.move_id.type in ('in_refund', 'out_refund'):
                                am = -debit
                            else:
                                am = debit
                        else:
                            am = debit
                    elif ac_move_line.credit != 0.0:
                        credit = ac_move_line.credit
                        if 'check_rate' in ac_move_line._fields and 'ac_move_line' in ac_move_line._fields:
                            rate = ac_move_line.rate_exchange
                        else:
                            tipo_cambio = self.env['res.currency.rate'].search(
                                [('name', '<=', ac_move_line.move_id.date), ('currency_id', '=', 2)], limit=1)
                            rate = tipo_cambio.inverserate
                        if ac_move_line.currency_id and ac_move_line.currency_id.name == 'USD' and ac_move_line.amount_currency != 0:
                            if rate:
                                credit = -ac_move_line.amount_currency * rate
                            else:
                                credit = -ac_move_line.amount_currency
                        if ac_move_line.move_id.is_invoice():
                            if ac_move_line.move_id.type in ('in_refund', 'out_refund'):
                                am = -credit
                            else:
                                am = credit
                        else:
                            am = -credit
                    if am != 0:
                        self._group_results.append({
                            'amount': round(am, 2),
                            'line_beta': line_beta,
                            'vat': str(ac_move_line.company_id.vat) if ac_move_line.company_id.vat else "",
                            'rut': str(ac_move_line.partner_id.vat) if ac_move_line.partner_id.vat else "",
                            'year_month': row['year'] + row['month'],
                            'date_invoice': row['year'] + row['month'],  # inv.date_invoice...???
                            'form': '2181'  # It's a hardcode always?
                        })

            for row_tax in row.tax_ids:
                for ac_move_line in ac_move_line_ids:
                    is_company = False
                    if ac_move_line.partner_id:
                        # if ac_move_line.partner_id.vat_type == TIPO_DOC_RUT:
                        if ac_move_line.partner_id.tipodocumento_ids.codigo == TIPO_DOC_RUT:
                            is_company = True
                    row_tax_line = row_tax.invoice_repartition_line_ids.filtered(lambda x: x.account_id)
                    row_tax_account = row_tax_line.account_id
                    if is_company and ac_move_line.account_id.id == row_tax_account.id:
                        _do_action(self, ac_move_line, row_tax.line_beta)

            if self._group_results:
                # _columns = [u'RUT compañía',u'Form', u'Año', u'RUT cliente',u'Fecha', u'Código', u'Monto']
                # _columns_row = ''
                # for r in _columns:
                #     _columns_row += r+ " "
                # file_to_save.write(_columns_row+"\n")
                for _r in self._group_results:
                    self.add_to_file(_r, file_to_save)
        _value = file_to_save.getvalue()
        index = _value.rfind(" ")
        # _value = _value[0:index:]
        _value = _value[0:index:] + _value[index + 1::]
        if _value:
            not_result = False
        self.state = 'exported' if not not_result else 'init'
        self.file_name = 'formulario_2181' + "." + row['file_format'] if not not_result else False
        self.file = base64.encodestring(_value.encode('utf-8')) if not not_result else False
        self.not_result = not_result
        file_to_save.close()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Formulario 2181',
            'res_model': 'account.line.beta.wzd',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id
        }

    def action_back(self):
        self.state = 'init'
        self.file_name = False
        self.file = False
        self.not_result = False

        return {
            'type': 'ir.actions.act_window',
            'name': 'Formulario 2181',
            'res_model': 'account.line.beta.wzd',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id
        }

    def _get_years(self):
        current_year = date.today().year
        return [(str(year), str(year)) for year in range(current_year - 10, current_year + 1)]

    month = fields.Selection([('01', 'Enero'),
                              ('02', 'Febrero'),
                              ('03', 'Marzo'),
                              ('04', 'Abril'),
                              ('05', 'Mayo'),
                              ('06', 'Junio'),
                              ('07', 'Julio'),
                              ('08', 'Agosto'),
                              ('09', 'Setiembre'),
                              ('10', 'Octubre'),
                              ('11', 'Noviembre'),
                              ('12', 'Diciembre')], string='Mes', required=True, readonly=True,
                             states={'init': [('readonly', False)]},
                             default=str(date.today().month) if date.today().month >= 10 else '0' + str(
                                 date.today().month))
    year = fields.Selection(_get_years, string=u'Año', required=True, readonly=True,
                            states={'init': [('readonly', False)]}, default=str(date.today().year))
    file_format = fields.Selection([('txt', 'Archivo (.txt)'), ('csv', 'Archivo (.csv)')], 'Formato del archivo',
                                   required=True, readonly=True, states={'init': [('readonly', False)]}, default='csv')
    tax_ids = fields.Many2many('account.tax', 'account_line_beta_tax_code_wzd_rel', 'wzd_id', 'tax_code_id',
                               string='Impuestos', domain=[('line_beta', '!=', False)], required=True, readonly=True,
                               states={'init': [('readonly', False)]},
                               default=lambda self: self.env['account.tax'].search([('line_beta', '!=', False)]).ids)
    file_name = fields.Char('Nombre del archivo', size=128)
    file = fields.Binary('Archivo')
    state = fields.Selection([('init', 'Init'), ('exported', 'Exported')], 'Estado', default='init')
    not_result = fields.Boolean('Sin resultados')
    show_all = fields.Boolean('Mostrar todo')
