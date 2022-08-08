from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    type_vendor = fields.Many2one('barmex.vendor.type')