from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = ['account.move.line']

    stock_move_id = fields.Many2one('stock.picking')
