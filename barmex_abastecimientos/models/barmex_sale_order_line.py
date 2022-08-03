from datetime import datetime
from unittest import result
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.misc import formatLang, get_lang
from odoo.exceptions import ValidationError, Warning
from odoo.tools.misc import clean_context
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round, float_is_zero
from odoo.exceptions import UserError
from collections import namedtuple, OrderedDict, defaultdict
from itertools import groupby


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    abastecimiento_compra = fields.Boolean(string='¿Compra?', help='Producto debe surtirse a través de una compra a proveedor')

    def _prepare_run_values_compra(self):
        replenishment = self.env['procurement.group'].create({'name': self.order_id.name})

        values = {
            'warehouse_id': self.order_id.warehouse_id or False,
            'route_ids':  self.route_id,
            'date_planned': self.order_id.date_order,
            'group_id': replenishment,
            'location_dest': self.order_id.warehouse_id.lot_stock_id or False,
            'propagate_date': self.order_id.date_order,
        }
        return values


    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        for line in self:
            if self.abastecimiento_compra:
                 try:
                    resul = self.env['product.product'].search([('id','=',self.product_id.id)]).with_context(location=self.order_id.warehouse_id.lot_stock_id.id)
                    print("Cantidad")
                    print(resul.qty_available)
                    self.env['procurement.group'].with_context(clean_context(self.env.context)).run([
                        self.env['procurement.group'].Procurement(
                            self.product_id,
                            self.product_uom_qty - resul.qty_available, #OBTENER ESTE NUMERO
                            self.product_uom,
                            self.order_id.warehouse_id.lot_stock_id,  # Location
                            _(f"{self.order_id.name} compra por stock"),  # Name
                            _(f"{self.order_id.name} compra por stock"),  # Origin
                            self.company_id,
                            self._prepare_run_values_compra()  # Values
                        )
                    ])
                 except UserError as error:
                    raise UserError(error)
        res = super(SaleOrderLine, self)._action_launch_stock_rule(previous_product_uom_qty)
        print(f'Resultado{res}')
        return res