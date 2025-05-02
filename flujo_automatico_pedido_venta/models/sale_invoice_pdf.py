from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_download_invoice_pdf(self):
        """ Método para la vista de cotización: Busca la factura publicada asociada
            y ejecuta la acción del informe para descargar el PDF.
        """
        self.ensure_one()

        # Se buscan las facturas asociadas publicadas (ajusta el criterio según tus datos)
        invoice = self.invoice_ids.filtered(lambda inv: inv.state == 'posted')

        if not invoice:
            raise UserError(_("No hay una factura publicada asociada a esta orden de venta."))
        # Invoca la acción del informe; en Odoo 17 suele ser 'account.account_invoices'

        report_action = self.env.ref('account.account_invoices')

        if not report_action:
            raise UserError(_("No se encontró la acción del informe de factura."))

        return report_action.report_action(invoice)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_download_pdf(self):
        """ Método para la vista de factura: Si la factura está publicada,
            ejecuta la acción del informe para descargar el PDF.
        """
        self.ensure_one()

        if self.state != 'posted':
            raise UserError(_("La factura no está publicada."))

        report_action = self.env.ref('account.account_invoices')

        if not report_action:
            raise UserError(_("No se encontró la acción del informe de factura."))

        return report_action.report_action(self)

