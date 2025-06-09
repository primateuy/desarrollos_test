from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_id", "company_id")
    @api.depends_context("partner_id", "company_id", "company")
    def _compute_sale_type_id(self):
        for record in self:
            sale_type = False

            # Si hay tipo por usuario
            user_sale_type = self.env["sale.order.type"].search([
                ("assignment_method", "=", "user"),
                ("user_ids", "in", record.env.user.id),
                ("company_id", "in", [record.company_id.id, False]),
            ], limit=1)

            if user_sale_type:
                sale_type = user_sale_type
            else:
                # Si hay tipo por cliente
                partner_sale_type = (
                    record.partner_id.with_company(record.company_id).sale_type
                    or record.partner_id.commercial_partner_id.with_company(record.company_id).sale_type
                )
                if partner_sale_type and partner_sale_type.assignment_method == "partner":
                    sale_type = partner_sale_type

            # Si no hay ninguno, usar el predeterminado
            if not sale_type:
                sale_type = record._default_type_id()

            record.type_id = sale_type