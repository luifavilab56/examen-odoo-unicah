from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .res_partner import CATEGORIAS_CLIENTE


class CafeteriaBeneficio(models.Model):
    _name = "cafeteria.beneficio"
    _description = "Beneficio de descuento"

    name = fields.Char(string="Nombre", required=True)
    categoria_cliente = fields.Selection(
        CATEGORIAS_CLIENTE, string="Categoría", required=True
    )
    porcentaje = fields.Float(string="Descuento (%)", required=True)
    fecha_inicio = fields.Date(
        string="Desde", required=True, default=fields.Date.context_today
    )
    fecha_fin = fields.Date(string="Hasta")
    active = fields.Boolean(string="Activo", default=True)

    @api.constrains("porcentaje", "fecha_inicio", "fecha_fin")
    def _check_beneficio(self):
        for beneficio in self:
            if not 0 < beneficio.porcentaje <= 50:
                raise ValidationError(
                    "El descuento debe ser mayor que 0 % y no superar el 50 %."
                )

            if beneficio.fecha_fin and beneficio.fecha_fin <= beneficio.fecha_inicio:
                raise ValidationError(
                    "La fecha final debe ser posterior a la fecha inicial."
                )