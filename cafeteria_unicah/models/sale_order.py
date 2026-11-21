from odoo import api, fields, models
from odoo.exceptions import UserError


LIMITE_LINEAS_BECADO = 5


class SaleOrder(models.Model):
    _inherit = "sale.order"

    categoria_cliente = fields.Selection(
        related="partner_id.categoria_cliente",
        string="Categoría",
    )
    beneficio_id = fields.Many2one(
        "cafeteria.beneficio",
        string="Beneficio",
        compute="_compute_beneficio_id",
        store=True,
        readonly=False,
        domain="[('categoria_cliente', '=', categoria_cliente)]",
    )
    beneficio_aplicado = fields.Boolean(
        string="Beneficio aplicado",
        readonly=True,
        copy=False,
    )
    total_sin_beneficio = fields.Monetary(
        string="Total sin beneficio",
        compute="_compute_total_sin_beneficio",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("partner_id", "partner_id.categoria_cliente", "date_order")
    def _compute_beneficio_id(self):
        for order in self:
            if not order.partner_id:
                order.beneficio_id = False
                continue

            fecha = (order.date_order or fields.Datetime.now()).date()
            order.beneficio_id = self.env["cafeteria.beneficio"].search(
                [
                    ("categoria_cliente", "=", order.partner_id.categoria_cliente),
                    ("active", "=", True),
                    ("fecha_inicio", "<=", fecha),
                    "|",
                    ("fecha_fin", "=", False),
                    ("fecha_fin", ">=", fecha),
                ],
                order="porcentaje desc",
                limit=1,
            )

    @api.depends(
        "order_line.price_unit",
        "order_line.product_uom_qty",
        "order_line.display_type",
        "order_line.product_id",
    )
    def _compute_total_sin_beneficio(self):
        for order in self:
            lineas = order.order_line.filtered(
                lambda line: not line.display_type and line.product_id
            )
            order.total_sin_beneficio = sum(
                line.price_unit * line.product_uom_qty for line in lineas
            )

    def action_aplicar_beneficio(self):
        for order in self:
            if order.state not in ("draft", "sent"):
                raise UserError("Solo se puede aplicar un beneficio a una cotización.")
            if order.beneficio_aplicado:
                raise UserError("El beneficio ya fue aplicado a esta cotización.")
            if not order.beneficio_id:
                raise UserError("El pedido no tiene un beneficio asignado.")

            lineas = order.order_line.filtered(
                lambda line: not line.display_type and line.product_id
            )
            if not lineas:
                raise UserError("Agregue al menos un producto antes de aplicar el beneficio.")

            beneficio = order.beneficio_id
            lineas.write({"discount": beneficio.porcentaje})
            order.beneficio_aplicado = True
            order.message_post(
                body=(
                    f"Se aplicó el {beneficio.name} "
                    f"con {beneficio.porcentaje:g} % de descuento."
                )
            )

    def action_confirm(self):
        for order in self:
            if order.categoria_cliente != "becado":
                continue

            lineas_producto = order.order_line.filtered(
                lambda line: not line.display_type and line.product_id
            )
            cantidad_lineas = len(lineas_producto)

            if cantidad_lineas > LIMITE_LINEAS_BECADO:
                raise UserError(
                    f"Un pedido de estudiante becado admite como máximo "
                    f"{LIMITE_LINEAS_BECADO} líneas de producto. "
                    f"Este pedido tiene {cantidad_lineas}."
                )

        return super().action_confirm()