from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, get_lang
from odoo.exceptions import ValidationError, Warning


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lco_price_dist = fields.Float(
        'Reseller price',
        store=True)
    lco_price_diff = fields.Float(string='Difference',
                                  store=True)

    lco_prod_prospecto = fields.Boolean(
        string='Prospect',
        related='product_id.lco_is_prospect_prod')

    is_listprice_modified = fields.Boolean(
        string='Accept price modification?',
        store=True,
        readonly=True)

    lco_delivery_time = fields.Char(string='Delivery Time')

    def _modify_price(self):
        if self._product_in_pricelist().fixed_price == 0 or \
                self.order_id.pricelist_id.is_modify_listprice:
            self.is_listprice_modified = True

    @api.onchange('product_id')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()

        if self.order_id.partner_id:
            if self.order_id.pricelist_id:
                if self.product_id:
                    product_pricelist = self._product_in_pricelist()
                    self._modify_price()

                    if not product_pricelist:
                        raise ValidationError(_(
                            "{} isn't in pricelist".format(
                                self.product_id.name
                            )))

            else:
                raise ValidationError(_('Pricelist not selected'))
        else:
            raise ValidationError(_('Customer not selected'))

        vals = {}

        product_dist = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.lco_property_product_pricelist_id.id,
            uom=self.product_uom.id
        )

        if self.order_id.lco_property_product_pricelist_id and \
                self.order_id.partner_id:
            vals['lco_price_dist'] = \
                self.env['account.tax']._fix_tax_included_price_company(
                    self._get_dist_display_price(product_dist),
                    product_dist.taxes_id, self.tax_id, self.company_id
                )

        self.update(vals)

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        dist = self.lco_price_dist
        diff = self.lco_price_diff
        if self.order_id.partner_id.invoicing_currency:
            res['price_unit'] = self._change_currency(self.price_unit)
            dist = self._change_currency(dist)
            diff = self._change_currency(diff)

        res['lco_price_dist'] = dist
        res['lco_price_diff'] = diff
        res['l10n_mx_edi_customs_number'] = self._get_petition()

        if self.display_type:
            res['account_id'] = False

        return res

    def _get_petition(self):
        delivery = self.env['stock.move.line'].search(
            [('product_id', '=', self.product_id.id),
             ('picking_id.sale_id', '=', self.order_id.id)])
        pedimento = []
        for record in delivery:
            pedimento.append(record.petition)
        res = ''

        if len(pedimento) == 0:
            res = ''
        else:
            res = ','.join(pedimento)
        return res

    def _change_currency(self, amount):

        local_cur = self.env.company.currency_id
        today = datetime.now().date()
        origin = self.order_id.currency_id

        res = origin._convert(amount, local_cur, self.env.company, today)
        return res

    def _get_dist_display_price(self, product):
        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in
            self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                ptav.price_extra and
                ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=tuple(
                    no_variant_attributes_price_extra)
            )

        if self.order_id.lco_property_product_pricelist_id.discount_policy == 'with_discount':
            return product.with_context(
                pricelist=self.order_id.lco_property_product_pricelist_id.id).price
        product_context = dict(
            self.env.context,
            partner_id=self.order_id.partner_id.id,
            date=self.order_id.date_order,
            uom=self.product_uom.id)

        final_price, rule_id = self.order_id.lco_property_product_pricelist_id.with_context(
            product_context).get_product_price_rule(
            product or self.product_id,
            self.product_uom_qty or 1.0,
            self.order_id.partner_id)
        base_price, currency = \
            self.with_context(product_context)._get_real_price_currency(
                product, rule_id,
                self.product_uom_qty,
                self.product_uom,
                self.order_id.lco_property_product_pricelist_id.id)
        if currency != self.order_id.lco_property_product_pricelist_id.currency_id:
            base_price = currency._convert(
                base_price,
                self.order_id.lco_property_product_pricelist_id.currency_id,
                self.order_id.company_id or self.env.company,
                self.order_id.date_order or fields.Date.today())
        return max(base_price, final_price)

    def _get_display_price(self, product):
        res = super(SaleOrderLine, self)._get_display_price(product)
        if self.product_id.sale_offer:
            pricelist = self._product_in_pricelist()
            res = pricelist.fixed_price

        return res

    def _product_in_pricelist(self):
        pricelist = self.order_id.pricelist_id.item_ids.filtered(
            lambda l: l.product_tmpl_id.id == self.product_id.product_tmpl_id.id)
        if pricelist:
            return pricelist
        else:
            raise ValidationError(_("Producto Invalido"))



