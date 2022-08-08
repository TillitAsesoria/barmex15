from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = ['stock.move.line']

    petition = fields.Char(string="Petition",
                           related="move_id.petition",
                           store=True)

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)

        if res.picking_id.picking_type_code == 'outgoing':
            demand = res.product_uom_qty
            pedimento = []
            while demand > 0:
                petition = res._get_move()
                if petition:
                    if petition.available < demand:
                        demand -= petition.available
                        petition.available = 0
                    else:
                        petition.available -= demand
                        demand = 0
                    pedimento.append(petition.petition)
                else:
                    demand = 0
            res.petition = ','.join(pedimento)
        return res

    def _get_move(self):
        domain = [
            ('product_id', '=', self.product_id.id),
            ('available', '>', 0)
        ]

        if self.product_id.categ_id.removal_strategy_id.method == 'fifo':
            return self.env['barmex.petition.relation'].search(
                domain, order='date asc', limit=1)
        if self.product_id.categ_id.removal_strategy_id.method == 'lifo':
            return self.env['barmex.petition.relation'].search(
                domain, order='date desc', limit=1)