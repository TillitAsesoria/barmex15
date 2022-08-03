from odoo import api, models, fields, _


class ProductPricelistCust(models.Model):
    _inherit = 'product.pricelist'

    customer_ids = fields.One2many('barmex.customer.product.pricelist',
                                   'pricelist_id',
                                   string='Pricelist Customer',
                                   copy=False)

    customer_pricelist_ids = fields.One2many('barmex.customer.product.pricelist',
                                   'pricelist_usd_id',
                                   string='Pricelist Customer',
                                   copy=False)

    lco_customer_type = fields.Many2one('barmex.partner.type',
                                        string='Customer type',
                                        stored=True)

    is_modify_listprice = fields.Boolean(string='Accept price modification?',
                                         default=False)

    reseller_price = fields.Boolean(string="Reseller Price")