# -*- coding: utf-8 -*-
import xmltodict
import requests

from odoo import models, fields
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo para almacenar el XML crudo de la respuesta de la DGI
    xml_result = fields.Text(readonly=True)

    def _consultar_partner_ruc(self):
        """Realiza la consulta al servicio DGI e imprime la URL y la respuesta cruda."""
        api_url = self.get_param('api_server_url')
        url = f"{api_url}/?vat={self.vat}"

        response = requests.post(url)
        if response.status_code != 200:
            raise ValidationError('Error al consultar el RUC')

        self.xml_result = response.text

        return self.load_dgi_data(response.text)

    def load_dgi_data(self, xml_result=None):
        """
        Procesa el XML de la DGI y actualiza los campos del partner.
        Para la dirección, si faltan datos, asigna valores por defecto.
        """
        for partner in self:
            datos = xmltodict.parse(xml_result or '')
            datos_persona = datos.get('WS_PersonaActEmpresarial') or {}

            # Datos básicos
            denominacion    = datos_persona.get('Denominacion')    or ''
            nombre_fantasia = datos_persona.get('NombreFantasia') or ''

            # Nodo de domicilio (puede no existir o no ser dict)
            nodo_dom = datos_persona.get('WS_DomFiscalLocPrincipal')
            if not isinstance(nodo_dom, dict):
                nodo_dom = {}
            datos_direccion = nodo_dom.get(
                'WS_PersonaActEmpresarial.WS_DomFiscalLocPrincipalItem'
            ) or {}

            # Ubicación geográfica
            city_id  = False
            state_id = False
            try:
                city_id = partner.find_city(name=datos_direccion.get('Dpto_Nom'))
            except Exception:
                pass
            try:
                state_id = partner.find_state(name=datos_direccion.get('Dpto_Nom'))
            except Exception:
                pass

            # Valores de dirección con default
            calle  = datos_direccion.get('Calle_Nom')   or 'Dirección no definida'
            numero = datos_direccion.get('Dom_Pta_Nro') or 'Dirección no definida'
            codigo = datos_direccion.get('Dom_Pst_Cod') or ''

            # Construir dict de actualización
            valores = {
                'name':          nombre_fantasia or denominacion or partner.name,
                'social_reason': denominacion or partner.social_reason,
                'is_company':    True,
                'vat':           partner.vat,
                'street':        calle,
                'street2':       numero,
                'city_id':       city_id.id    if city_id  else False,
                'state_id':      state_id.id   if state_id else False,
                'zip':           codigo,
                'country_id':    self.env.company.country_id.id,
            }

            # Procesar contactos de forma robusta
            contactos_node = datos_direccion.get('Contactos')
            contactos = []
            if isinstance(contactos_node, dict):
                raw = contactos_node.get('WS_Domicilio.WS_DomicilioItem.Contacto') or []
                if isinstance(raw, dict):
                    contactos = [raw]
                elif isinstance(raw, list):
                    contactos = raw

            for c in contactos:
                tipo  = c.get('TipoCtt_Id')
                valor = c.get('DomCtt_Val')
                if tipo == '6':
                    valores['mobile'] = valor
                elif tipo == '1':
                    valores['email'] = valor
                elif tipo == '5':
                    valores['phone'] = valor

            # Actualizar el partner
            partner.update(valores)

            # Post en chatter
            if partner._origin:
                partner._origin.message_post(
                    subject='Datos actualizados desde DGI',
                    body=str(valores),
                    message_type='comment'
                )
        return True
