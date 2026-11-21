import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError

CATEGORIAS_CLIENTE = [
    ("becado", "Estudiante becado"),
    ("estudiante", "Estudiante regular"),
    ("empleado", "Empleado"),
    ("visitante", "Visitante"),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    categoria_cliente = fields.Selection(
        CATEGORIAS_CLIENTE,
        string="Categoría de cliente",
        default="visitante",
    )
    codigo_carnet = fields.Char(string="Código de carné", copy=False)
    facultad = fields.Char(string="Facultad")
    @api.constrains("categoria_cliente", "codigo_carnet")
    def _check_codigo_carnet(self):
        for partner in self:
            if partner.categoria_cliente in ("becado", "estudiante"):
                codigo = partner.codigo_carnet or ""
                if not re.fullmatch(r"[0-9]{8}", codigo):
                    raise ValidationError(
                        "El código de carné del estudiante debe tener exactamente 8 dígitos."
                    )