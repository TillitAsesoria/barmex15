from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ForeignTrade(models.Model):
    _name = 'barmex.foreign.trade'
    _description = 'Foreign trade'
    _order = 'id desc'
    _check_company_auto = True
    _sql_constraints = [
        ('unique_petition', 'unique(year, customs,agent,petition,partner_id)',
         _('Petition number is not unique!')
         )]

    name = fields.Char(string="Name",
                       compute='set_name')

    petition_no = fields.Char(string="Petition Number",
                              compute='set_petition')

    partner_id = fields.Many2one('res.partner',
                                 string='Vendor')

    move_id = fields.Many2one('stock.picking')

    tax_id = fields.Char(string='Tax ID',
                         related='partner_id.tax_id',
                         store=True)

    year = fields.Integer(string='Year',
                          required=True)

    customs = fields.Many2one('barmex.foreign.trade.customs',
                              string='Customs',
                              required=True)

    agent = fields.Integer(string='Agent',
                           required=True)

    petition = fields.Char('Petition',
                           required=True)

    petition_date = fields.Datetime('Petition date')

    exchange_rate = fields.Float('Exchange rate')

    usd_amount = fields.Float('USD Amount')

    insurance_amount = fields.Float('Insurance Amount')

    insurance = fields.Float('Insurance')

    freight = fields.Float('Freight')

    packaging = fields.Float('Packaging')

    other = fields.Float('Others')

    dta = fields.Float('DTA')

    vat = fields.Float('VAT')

    prv = fields.Float('PRV')

    igi = fields.Float('IGI')

    additional_1 = fields.Float('Aditional 1')

    additional_2 = fields.Float('Aditional 2')

    val_mon_fac = fields.Float('Val. Mon. Fac.')

    val_dls_fac = fields.Float('Val. Dls. Fac.')

    customs_value = fields.Float('Customs Value')

    rate_invoice_cur = fields.Float('Rate Invoice Currency')

    brand = fields.Char('Brand')

    invoice_num = fields.Char('Invoice Number')

    invoice_date = fields.Date('Invoice Date')

    invoice_val_mxn = fields.Float('Invoice Value MXN')

    qty = fields.Integer('Petitions Qty',
                         default=1,
                         readonly=True)

    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company)

    @api.constrains('tax_id')
    def _tax_id(self):
        if self.tax_id == '':
            raise ValidationError(_('Tax Id required'))

    @api.constrains('customs')
    def _customs(self):
        if self.customs == 0:
            raise ValidationError(_('Customs invalid'))

    @api.constrains('agent')
    def _agent(self):
        if self.agent == 0:
            raise ValidationError(_('Agent invalid'))

    @api.constrains('year')
    def _year(self):
        if self.year == 0:
            raise ValidationError(_('Year invalid'))

    @api.depends('tax_id', 'petition', 'customs', 'agent', 'year')
    def set_name(self):
        for record in self:
            record.update({
                'name': "{}{}{}{}{}".format(record.tax_id, record.petition,
                                            record.customs.code, record.agent,
                                            record.year)
            })

    @api.depends('petition', 'customs', 'agent', 'year')
    def set_petition(self):
        for record in self:
            record.update({
                'petition_no': "{}  {}  {}  {}".format(record.year,
                                                       record.customs.code,
                                                       record.agent,
                                                       record.petition)
            })
