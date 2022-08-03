import string
from odoo import _, api, fields, models
from odoo.tools.misc import clean_context
from datetime import datetime
from odoo.exceptions import UserError

#stock/models/stock_rule.py

class StockSchedulerCompute(models.TransientModel):
    _name = "stock.scheduler.compute"
    _description = 'Run Scheduler Manually'
    _inherit = "stock.scheduler.compute"
    
    almacen = fields.Many2one('stock.warehouse', string="Almacen", required=True)
    marca = fields.Many2one('product.category', string='Marca', required=True)
    date_planned = fields.Date('Scheduled Date',  default=datetime.today())

    route_ids = fields.Many2many(
        'stock.location.route', string='Preferred Routes',
        help="Apply specific route(s) for the replenishment instead of product's default routes.",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company')

    def abastecimientos(self):

        #Buscar productos que pertenezcan a esa categoria
        productos_ids = self.env['product.product'].search(
                    [('categ_id', '=', self.marca.id)]
                ).with_context(location=self.almacen.lot_stock_id.id)
        if productos_ids:
            #productos = self.env['product.product'].browse(productos_ids)
            for producto in productos_ids:
                uom_reference = producto.uom_id
                #Busca por cada producto el stock max /min configurado
                max_min_cant = self.env['stock.warehouse.orderpoint'].search(
                    [('warehouse_id', '=', self.almacen.id),('product_id', '=', producto.id)]
                )
                max_min_cant_count = self.env['stock.warehouse.orderpoint'].search_count(
                    [('warehouse_id', '=', self.almacen.id),('product_id', '=', producto.id)]
                )
                print(f'PRODUCTO {producto.default_code}')
                print(f'{max_min_cant_count}')
                #No funciona, checar si el resultado de Search esta vacio
                if max_min_cant_count > 0:
                    print('PRODUCTO MAYOR A 0')
                    if producto.free_qty <= max_min_cant.product_min_qty:
                        print(f'PRODUCTO {producto.default_code} NECESITA MAS STOCK. MINIMO: {max_min_cant.product_min_qty}')
                        try:
                            self.env['procurement.group'].with_context(clean_context(self.env.context)).run([
                                self.env['procurement.group'].Procurement(
                                    producto,
                                    max_min_cant.product_max_qty - producto.free_qty, #OBTENER ESTE NUMERO
                                    uom_reference,
                                    self.almacen.lot_stock_id,  # Location
                                    _(f"{self.almacen.name} abastecimiento"),  # Name
                                    _(f"{self.almacen.name} Stock MAX MIN"),  # Origin
                                    self.almacen.company_id,
                                    self._prepare_run_abastecimientos(max_min_cant)  # Values
                                )
                            ])
                        except UserError as error:
                            raise UserError(error)
                else:
                    print('PRODUCTO IGUAL A 0')
                    #raise UserError(f'El producto {producto.default_code} no tiene configuradas reglas de stock maximo y minimo en el almacen {self.almacen.name}')
        return {
            'type': 'ir.actions.client',
            'tag': 'reload', #display_notification
            'params': {
                'message': 'Proceso de planificador finalizado, ir al menu de compras para revisar las solicitudes',
                'type': 'success',
                'sticky': False,
            }
        }

    def _prepare_run_abastecimientos(self, orderpoint= False):
        replenishment = self.env['procurement.group'].create({})

        values = {
            'warehouse_id': self.almacen,
            'route_ids': self.route_ids,
            'date_planned': self.date_planned,
            'group_id': replenishment,
            'orderpoint_id': orderpoint
        }
        return values