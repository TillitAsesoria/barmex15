from odoo import models, fields, _


class Arancel(models.Model):
    _inherit = 'product.unspsc.code'

    fecha_inicio_vigencia = fields.Char("Inicio de vigencia")
    fecha_fin_vigencia = fields.Char("Inicio de vigencia")
    imp = fields.Float("IMP")
    ext = fields.Float("EXT")
