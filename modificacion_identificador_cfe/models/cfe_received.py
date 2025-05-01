# -*- coding: utf-8 -*-
import logging
import xmltodict
from odoo import models

class CFEReceived(models.Model):
    _inherit = 'cfe.received'

    def prepare_cfe_received_values(self, values=None):

        invoice_obj = self.env['account.move']
        cfe_received_values_obj = self.env['cfe.received.invoice.values']
        xml_resultado = values.get('XMLResultado', {})
        recibidos_values = xml_resultado.get('Recibidos', {}) \
            if not isinstance(xml_resultado.get('Recibidos', {}), type(None)) else {}
        recibidos = recibidos_values.get('Recibido', [])
        if not recibidos:
            return self.write({'state': 'fail'})

        for recibido in recibidos:
            if not isinstance(recibido, dict):
                continue

            # ─────────── LÍNEA A MODIFICAR ───────────
            # Actualmente usa FechaCFE; aquí reemplazaremos por el RUT cuando tengamos la clave
            uuid =    recibido ['Empresa'] \
                    + recibido ['TipoDocumentoCFE'] \
                    + recibido ['SerieDocumentoCFE'] \
                    + recibido ['ComprobanteCFE'] \
                    + recibido ['RUT']
            # ──────────────────────────────────────────

            invoice_id = invoice_obj.search([('uuid', '=', uuid)], limit=1)
            if invoice_id:
                values = {
                    'cfe_received_id': self.id,
                    'invoice_value': xmlcfefirmado,
                    'uuid': uuid,
                }
                new_cfe_received_values = cfe_received_values_obj.create(values)
                new_cfe_received_values.state = 'done'
                new_cfe_received_values.invoice_id = invoice_id
                self.action_marcar_cfe_procesado(documents=[invoice_id])
                continue

            cfe = recibido['XMLCFE']
            xmlcfefirmado = self.normalize_keys(xmltodict.parse(cfe))
            xmlcfefirmado['uuid'] = uuid
            values = {
                'cfe_received_id': self.id,
                'invoice_value': xmlcfefirmado,
                'uuid': uuid,
            }
            if not cfe_received_values_obj.search(
                [('uuid', '=', uuid), ('cfe_received_id', '=', self.id)], limit=1
            ):
                new_cfe_received_values = cfe_received_values_obj.create(values)

        return True
