from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import json
import logging
_logger = logging.getLogger(__name__)

class PaymentAggregator(models.Model):

    _name = 'mps.payment.aggregator'
    _description = 'Model to save payment aggregator'

    name = fields.Char(required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='currency',
        required=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('published','Published')
    ],default="draft")

    # talonario
    receiptbook_id = fields.Many2one(
        "mps.receipt.books",
        required=True
    )

    # cliente o empresa
    customer_id = fields.Many2one(
        'res.partner',
        string='customer',
        required=True
    )

    adenda = fields.Char(string="Adenda")

    date = fields.Date(required=True)

    # importe
    amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_amount"
    )

    # pago a cuenta
    payment_account = fields.Monetary(
        currency_field="currency_id"
    )

    # asignacion de deuda
    debt_allocation = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_debt_allocation"
    )

    # Diferencia
    difference = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_difference"
    )

    # Metodos de pago
    mps_payment_methods_line_ids = fields.One2many(
        'mps.payment.methods.line', 
        'mps_payment_aggregator_id'
    )

    # apuntes contables
    mps_credits_line_ids = fields.Many2many(
        'account.move.line', 
        string='Cuentas por Pagar/Cobrar',
    )
    average_rate = fields.Float(compute='_compute_average_rate')

    # Se suma los montos de los metodos de pago
    @api.depends('average_rate')
    def _compute_average_rate(self):
        payment_lines = self.mps_payment_methods_line_ids
        if len(payment_lines) > 0:
            self.average_rate = sum(payment_lines.mapped("exchange_rate")) / len(payment_lines)
        else: 
            self.average_rate = 0


    # Se suma los montos de los metodos de pago
    @api.depends('amount')
    def _compute_amount(self):
        for record in self:
            record.amount = sum(self.mps_payment_methods_line_ids.mapped("amount"))

    # Si el adenda se cambia, se lo agregamos a los metodos de pago 
    @api.onchange('adenda')
    def onchange_adenda(self):
        if self.adenda:
            if len(self.mps_payment_methods_line_ids) > 0:
                for method in self.mps_payment_methods_line_ids:
                    method.adenda = self.adenda
    

    # Cambiar estatus del registro
    def button_change_state(self):
        if self.state == "draft":
            # Validamos creditos/debitos
            if len(self.mps_credits_line_ids) == 0:
                raise ValidationError(_("To make payments you must have credits or debits to operate."))

            # Validamos si tiene importes pagados
            for credit_line in self.mps_credits_line_ids:
                if credit_line["total_import"] <= 0:
                    raise ValidationError(_("To confirm payments you must upload the amounts to be paid."))
            
            # Validamos pagos
            if len(self.mps_payment_methods_line_ids) == 0:
                raise ValidationError(_("To make payments you must load the payments in the payment lines."))

            # Validamos el valor de diferencia
            if self.difference != 0:
                raise ValidationError(_("To confirm payments the difference must be 0"))

            for credit_line in self.mps_credits_line_ids:
                if not credit_line.move_id:
                    raise UserError(_("La línea contable %s no está asociada a una factura") % credit_line.display_name)
                
                # Verificar que la factura tenga exactamente una línea por cobrar/pagar
                receivable_payable_lines = credit_line.move_id.line_ids.filtered(
                    lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable')
                )
                if len(receivable_payable_lines) != 1:
                    raise UserError(_("La factura %s no tiene una estructura contable válida") % credit_line.move_id.name)

            try:
                # Recorrer los creditos y/o debitos
                self._create_invoices_payment()

                # Validamos si tiene pago acuento para realizar le pago
                self._create_payment_acount()

                # Crear los pagos de los metodos de pago
                self._create_lines_payment_payments()

            except Exception as e:
                raise UserError(e)
            self.state = "published"
        else:
            self.state = "draft"

    # Metodo para crear los pagos de las lineas de pago
    def _create_lines_payment_payments(self):
        # Lineas de pago
        for payment_method in self.mps_payment_methods_line_ids:
            # Tomamos el diario de la linea de pago
            journal = payment_method.account_journal_id
            
            # Validamos
            if not journal:
                raise UserError(_("La linea de pago debe contener un diario contable"))
            
            # Construimos el diccionario para el pago
            payment_details = self._get_standard_payment()
            payment_details['date'] = payment_method["date"]
            payment_details['amount'] = payment_method["amount"]
            payment_details['payment_type'] = self["receiptbook_id"]["type"] if not self["receiptbook_id"]["enable_reverse_payment"] else payment_method["payment_type"]
            payment_details['is_internal_transfer'] = True   # Marcamos
            payment_details['ref'] = _('Internal Transfer')   # Referencia
            payment_details['payment_method_id'] = payment_method["payment_method_id"]["id"]
            
            # Validar el sentido del talonario para registrar el pago, ya sea saliente o entrante
            if self.receiptbook_id.type == "outbound":
                payment_details['journal_id'] = journal.id # Diario origen
                payment_details['destination_journal_id'] = self.currency_id.account_journal_id.id # Diario destino
            else:
                payment_details['journal_id'] = self.currency_id.account_journal_id.id # Diario origen
                payment_details['destination_journal_id'] = journal.id, # Diario destino
            
            # Creamos el pago
            self.create_publish_payment(payment_details)

    # Metodo para crear el pago a cuenta
    def _create_payment_acount(self):
        if self.payment_account > 0:
            # Armamos los detalles del pago
            payment_details = self._get_standard_payment()

            # Modificamos el monto a pagar
            payment_details['amount'] = self.payment_account

            # Creamos el pago
            self.create_publish_payment(payment_details)

    # Metodo para recorrer los apuntes contables y marcar como pagados
    def _create_invoices_payment(self):
        # Recorrer los creditos y/o debitos
        for credit_line in self.mps_credits_line_ids:
            # Armamos los detalles del pago
            payment_details = self._get_standard_payment()

            # Modificamos los campos necesarios
            payment_details["amount"] = credit_line.total_import  # Monto a pagar
            payment_details["reconciled_invoice_ids"] = [(6,0,[credit_line.move_id.id])], # Se asigna la factura al pago
            payment_details["ref"] = credit_line.move_id.name, # Nombre de referencia

            # Creamos el pago
            self.create_publish_payment(payment_details)

            # Marcamos la factura como pagada
            credit_line.move_id.payment_state = 'paid' 

    # Metodo para obtener el diccionario estandar para registrar un pago
    def _get_standard_payment(self):
        return {
            'partner_id': self.customer_id.id,   # Cliente
            'date': self.date,                   # Fecha del pago    
            'amount': 0,                         # Monto a pagar
            'is_internal_transfer': False,       # Si es transferencia
            'payment_type': self.receiptbook_id.type,  # Tipo de pago segun el talonario
            'journal_id': self.currency_id.account_journal_id.id, # Diario intermedio
            'partner_type': self.receiptbook_id.partner_type, # Si es cliente o si es proveedor
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id, # Metodo de pago
        }
    
    # Metodo para crear un pago y publicarlo
    def create_publish_payment(self, payment_details):
        if not payment_details:
            raise ValidationError(_("Payments cannot be created with empty information."))
        # Creamos las transferencias internas
        payment_id = self.env['account.payment'].create(payment_details)
        # Confirmamos el pago
        payment_id.action_post()
        payment_id.set_transaction_type()
        # Retornamos el pago
        return payment_id

    # Se calcula la diferencia
    @api.depends('amount', 'payment_account', 'debt_allocation')
    def _compute_difference(self):
        for record in self:
            record.difference = record.amount - (record.payment_account + record.debt_allocation)
    # Calculamos debt_allocation automáticamente cuando cambian las líneas
    @api.depends('mps_credits_line_ids.total_import')
    def _compute_debt_allocation(self):
        for record in self:
            record.debt_allocation = sum(record.mps_credits_line_ids.mapped('total_import'))

    
    @api.onchange('customer_id', 'currency_id')
    def filter_credit_moves(self):
        self.mps_credits_line_ids = self.search_account_move_line()

    def assign_domain(self):
        return [
                    ('partner_id', '=', self.customer_id.id),
                    ('currency_id', '=', self.currency_id.id),
                    '|',  
                    ('account_id.account_type', '=', 'asset_receivable'),
                    ('account_id.account_type', '=', 'liability_payable'),
                    ('move_id.payment_state','=','not_paid'),
                    ('move_id.move_type', 'in', ['out_invoice','in_invoice'])
                ]
    
    def search_account_move_line(self):
        return self.env['account.move.line'].search(self.assign_domain())
    
    def button_open_accounting_notes(self):
        self.ensure_one()
        
        return {
            'name': 'Apuntes Contables', 
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',  
            'view_mode': 'tree,form',  
            'domain': self.assign_domain(),  
        }
    
    def button_open_grouped_payments(self):
        self.ensure_one()
        
        # Buscar la vista específica si existe
        view_id = self.env.ref('tu_modulo.view_account_payment_tree_grouped_simple', False)
        
        return {
            'name': 'Pagos Agrupados',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree',
            'views': [(view_id.id if view_id else False, 'tree')],
            'target': 'current',
            'context': {
                'group_by': ['transaction_type'],
                'search_default_partner_id': self.customer_id.id if self.customer_id else False,
            },
            'domain': [('partner_id', '=', self.customer_id.id)] if self.customer_id else [],
        }
    
    def button_update_accounting_notes(self):
        self.filter_credit_moves()
        return
    
    def button_delete_accounting_notes(self):
        # Filtrar solo los registros donde total_import es 0
        lines_to_remove = self.mps_credits_line_ids.filtered(lambda line: line.total_import == 0)
        # Eliminar solo esas líneas
        self.write({'mps_credits_line_ids': [(3, line.id) for line in lines_to_remove]})
        return
    

    def button_apply_fifo(self):
        if self.difference > 0 and self.mps_credits_line_ids:
            sorted_moves = self.mps_credits_line_ids.sorted(key=lambda r: r.date or fields.Date.today())
            
            for move in sorted_moves:
                if move.total_import == 0:
                    total_import = abs(move.credit) + abs(move.debit)
                    if total_import <= 0:
                        continue
                    if (self.difference - total_import) >= 0:
                        move.total_import = total_import
                    else:
                        break

    def button_assign_all(self):
        for record in self.mps_credits_line_ids:
            if record.total_import == 0:
                total_import = record.credit + record.debit
                if (self.difference - total_import) >= 0:
                        record.total_import = total_import

        return
 