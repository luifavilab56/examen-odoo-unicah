from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    es_tutor_unicah = fields.Boolean(string="Es tutor UNICAH")


class UnicahTutoria(models.Model):
    _name = "unicah.tutoria"
    _description = "Sesión de tutoría UNICAH"
    _order = "fecha_inicio desc"

    name = fields.Char(string="Tema", required=True)
    estudiante_id = fields.Many2one(
        "res.partner",
        string="Estudiante",
        required=True,
        ondelete="restrict",
    )
    tutor_id = fields.Many2one(
        "res.partner",
        string="Tutor",
        required=True,
        ondelete="restrict",
        domain="[('es_tutor_unicah', '=', True)]",
    )
    fecha_inicio = fields.Datetime(string="Inicio", required=True)
    fecha_fin = fields.Datetime(string="Fin", required=True)
    estado = fields.Selection(
        [
            ("programada", "Programada"),
            ("realizada", "Realizada"),
            ("cancelada", "Cancelada"),
        ],
        string="Estado",
        required=True,
        default="programada",
    )
    duracion_horas = fields.Float(
        string="Duración (horas)",
        compute="_compute_duracion_horas",
        store=True,
        digits=(12, 2),
    )

    @api.depends("fecha_inicio", "fecha_fin")
    def _compute_duracion_horas(self):
        for sesion in self:
            if sesion.fecha_inicio and sesion.fecha_fin:
                diferencia = sesion.fecha_fin - sesion.fecha_inicio
                sesion.duracion_horas = diferencia.total_seconds() / 3600
            else:
                sesion.duracion_horas = 0.0

    @api.constrains("fecha_inicio", "fecha_fin", "estudiante_id", "tutor_id")
    def _check_sesion(self):
        for sesion in self:
            if (
                sesion.fecha_inicio
                and sesion.fecha_fin
                and sesion.fecha_fin <= sesion.fecha_inicio
            ):
                raise ValidationError(
                    "La hora de fin debe ser posterior a la hora de inicio."
                )
            if sesion.estudiante_id == sesion.tutor_id:
                raise ValidationError(
                    "El estudiante y el tutor deben ser contactos diferentes."
                )
            if sesion.tutor_id and not sesion.tutor_id.es_tutor_unicah:
                raise ValidationError(
                    "El contacto seleccionado no está habilitado como tutor UNICAH."
                )
            