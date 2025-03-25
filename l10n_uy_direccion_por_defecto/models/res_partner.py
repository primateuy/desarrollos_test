from odoo import models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def load_dgi_data(self, response_text):
        # Inicializa el diccionario de datos de dirección vacío
        datos_direccion = {}

        # Si no se encuentran datos de dirección, se asigna el valor por defecto o "no definido"
        if not datos_direccion:
            direccion_defecto = self.env.company.direccion_por_defecto or "no definido"
            datos_direccion = {
                'Contactos': {
                    'WS_Domicilio.WS_DomicilioItem.Contacto': direccion_defecto
                }
            }

        # Extrae los datos de contacto de la estructura de datos
        contactos = datos_direccion.get('Contactos', {}).get('WS_Domicilio.WS_DomicilioItem.Contacto', [])
        return contactos