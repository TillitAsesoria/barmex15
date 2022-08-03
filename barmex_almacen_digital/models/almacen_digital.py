import string
from odoo import models,fields

class AlmacenDigital(models.Model):
    _name = "almacen.digital"
    _description = 'guardar las facturas desde el Web Service del SAT'
    
    name = fields.Char(string="UUID")
    fecha_comprobante = fields.Date(string='Fecha')
    serie = fields.Char(string="Serie")
    folio = fields.Char(string="Folio")
    rfc_emisor = fields.Char(string="RFC")
    nombre_emisor = fields.Char(string="Nombre")
    moneda = fields.Char(string="Moneda")
    tipo_de_cambio = fields.Float(string="Tipo de Cambio")
    total = fields.Float(string="Total")
    forma_de_pago = fields.Integer(string="Forma de pago")
    compra_gasto = fields.Selection(selection=[('compra', 'Compra'),('gasto', 'Gasto')], string='Compra/Gasto', default='gasto')
    productos_ids = fields.One2many("almacen.digital_productos","factura_id","Productos")
    tipo_de_comprobante = fields.Char(string="Tipo de comprobante")
    impuestos = fields.Float(string="Impuestos")

    
class AlmacenDigitalProductos(models.Model):
    _name = "almacen.digital_productos"
    _description = 'guardar productos'

    name = fields.Char("Producto")
    cantidad = fields.Float("Cantidad")
    precio = fields.Float("Precio")
    factura_id = fields.Many2one("almacen.digital","Factura")
    clave_prod_serv = fields.Integer("Clave productos y servicios")
    clave_unidad = fields.Char("Clave unidades")
    uuid = fields.Char("UUID")
