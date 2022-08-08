from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountMove(models.Model):
    _inherit = ['account.move']

    def _get_amount_currency_usd(self):
        for record in self:
            if record.barmex_currency_rate == 0:
                record.barmex_currency_rate = 1
            if record.currency_id.name == "USD":
                record.amount_currency_usd = record.amount_total_signed / record.barmex_currency_rate
            else:
                record.amount_currency_usd = record.amount_total_signed * record.barmex_currency_rate
        # suma = 0.00
        # for line in self.line_ids:
        #     print('pepe', line.amount_currency)
        #     suma = suma + line.amount_currency
        # self.amount_currency_usd = suma

    movement_id = fields.Many2one('res.partner')

    barmex_uuid = fields.Char(string='UUID',
                              compute='_set_uuid',
                              store=True,
                              readonly=True)

    discount_total = fields.Monetary(string='Discount',
                                     compute='_discount_total')

    barmex_reason = fields.Many2one('barmex.reason',
                                    string='Reason')

    barmex_currency_rate = fields.Monetary(string='Tasa de cambio')

    xml_ids = fields.One2many('barmex.invoice',
                              'invoice_id')

    state = fields.Selection(
        selection_add=[
            ('lock', 'Credit Lock'),
            ('total_lock', 'Total Lock'),
        ], ondelete={'lock': 'cascade', 'total_lock': 'cascade'})

    previous_state = fields.Char(string='Previous State',
                                 readonly=True)

    credit_notes = fields.Char('Credit Notes',
                               compute='_get_credit_notes',
                               readonly=True,
                               store=True)
    out_debit_note = fields.Boolean('Customer debit note', readonly=True)
    in_debit_note = fields.Boolean('Supplier debit note', readonly=True)

    collector_id = fields.Many2one('barmex.collector',
                                   string='Collector')

    # partner_addenda_id = fields.Many2one(string="Addenda Type",
    #                                      related="partner_id.addenda_id")

    addenda_id = fields.Many2one('barmex.addenda.record',
                                 string="Addenda",
                                 domain="[('id','=',addenda_num)]")

    partner_cobrador = fields.Many2one(
        related='partner_id.cobrador_employee_ids', string="Cobrador",
        readonly=True)

    addenda_num = fields.Integer('Addenda ID')
    folio_cliente = fields.Char('ID Cliente')
    amount_currency_usd = fields.Float('Monto USD',
                                       compute=_get_amount_currency_usd)

    # @api.depends('amount_total_signed','barmex_currency_rate')
    # @api.onchange('amount_total_signed','barmex_currency_rate')
    # def _get_amount_currency_usd(self):
    #     # suma = 0.00
    #     # for line in self.line_ids:
    #     #     print('pepe', line.amount_currency)
    #     #     suma = suma + line.amount_currency
    #     # self.amount_currency_usd = suma
    #     for record in self:
    #         from_currency = "USD"
    #         to_currency = "MXN"
    #         api_key = "40WHJCOAYB0DRGC5"
    #         base_url = r"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"
    #         main_url = base_url + "&from_currency=" + from_currency + "&to_currency=" + to_currency + "&apikey=" + api_key 
    #         req_ob = requests.get(main_url)
    #         result = req_ob.json()
    #         usd_value = float(result["Realtime Currency Exchange Rate"]['5. Exchange Rate'])
    #         if record.currency_id.name == "USD":   
    #             record.barmex_currency_rate = usd_value
    #             aux = record.amount_total_signed
    #             record.amount_currency_usd = aux
    #             record.amount_total_signed = aux / usd_value
    #         elif record.currency_id.name == "MXN":
    #             record.barmex_currency_rate = 1.00
    #             record.amount_currency_usd = usd_value * record.amount_total_signed

    @api.depends('invoice_line_ids.lco_price_diff')
    def _discount_total(self):
        """
        Compute the total discount amount for the invoice.
        """
        for move in self:
            total = 0.0
            for line in move.invoice_line_ids:
                if line.lco_price_diff > 0:
                    total += line.lco_price_diff * line.quantity

            move.update({
                'discount_total': total,
            })

    def credit_note(self):
        invoices = sorted(self, key=lambda x: x.partner_id.id)
        vendor = invoices[0].partner_id

        ids = ''

        for record in self:
            if record.partner_id != vendor:
                raise Warning(_("Function not available for multiple vendors"))
            else:
                ids += '{},'.format(record.id)

        form = self.env.ref('barmex.barmex_credit_note', False).id

        note = self.env['barmex.credit.note'].create({
            'name': 'Test',
            'move_ids': ids,
            'reason': self.env['barmex.reason'].search(
                [('discount', '=', True)], limit=1).id,
        })

        return {
            'name': _('Credit note'),
            'type': 'ir.actions.act_window',
            'res_model': 'barmex.credit.note',
            'res_id': note.id,
            'view_id': form,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }

    @api.onchange('partner_id')
    def _onchange_partner_id(self):

        super(AccountMove, self)._onchange_partner_id()

        if not self.partner_id:
            self.folio_cliente = ""
        else:
            self.folio_cliente = self.partner_id.barmex_id_cust

        if self.partner_id.collector_ids:
            self.collector_id = self.partner_id.collector_ids[0].id

        if self.partner_id and self.type == 'out_invoice':
            self.journal_id = self.partner_id.lco_sale_zone.journal_id.id
            self.l10n_mx_edi_usage = self.partner_id.l10n_mx_edi_usage

    def action_post(self):
        if self.env.company.collection_lock_date:
            if (
                    self.date and self.date <= self.env.company.collection_lock_date) or (
                    self.invoice_date and self.invoice_date <= self.env.company.collection_lock_date) or (
                    not self.date and not self.invoice_date and datetime.now().date() <= self.env.company.collection_lock_date):
                if not self.user_has_groups(
                        'barmex.group_account_user_barmex'):
                    raise Warning(_("User can't post due Collections lock"))

        msg = ''
        for record in self.filtered(lambda x: x.type == 'entry'):
            date = record.invoice_date if record.invoice_date else record.date
            for line in record.line_ids:
                msg += line.get_credit_message(date)
                if msg:
                    msg += _('This document will be locked.')

        for record in self.filtered(lambda x: x.type == 'out_invoice'):
            msg = record.get_credit_message()

        if msg:
            return (
                self.env['barmex.alert'].create({
                    'exception_msg': msg,
                    'partner_id': record.partner_id.id,
                    'origin_reference': '{},{}'.format('account.move',
                                                       record.id),
                    'continue_method': 'action_lock',
                }).action_show(_('Credit Alert')))
        else:
            return super(AccountMove, self).action_post()

    def get_credit_message(self):
        ret = ''

        date = self.invoice_date if self.invoice_date else self.date
        amount = self.currency_id._convert(self.amount_total,
                                           self.partner_id.credit_currency,
                                           self.env.company, date)

        if not self.partner_id.exceed_limit:
            if self.partner_id.open_invoice_exceeded:
                ret = _(
                    'Invoice credit limit exceeded.\nThis invoice will be locked.')

            elif self.partner_id.open_invoice_risk + amount > self.partner_id.open_invoice_amount and self.partner_id.open_invoice_include:
                ret = _(
                    'Invoice credit limit will be exceeded with this invoice.\nThis invoice will be locked.')

            elif self.partner_id.general_limit < self.partner_id.total_risk + amount:
                ret = _(
                    'Credit limit will be exceeded with this invoice.\nThis invoice will be locked.')

            elif self.partner_id.credit_exceeded:
                ret = _('Credit limit exceeded.\nThis invoice will be locked.')

            elif self.partner_id.due_invoice_lock and self.partner_id.locked_by_due:
                ret = _('Has due invoices.\nThis invoice will be locked.')

        return ret

    def action_lock(self):
        self.state = 'lock'

    def approve_invoice(self):
        self.post()

    @api.depends('l10n_mx_edi_cfdi_uuid', 'xml_ids')
    def _set_uuid(self):
        for record in self:
            uuid = ''
            if record.xml_ids:
                uuid = record.xml_ids[0].uuid
            else:
                uuid = record.l10n_mx_edi_cfdi_uuid
            record.update({
                'barmex_uuid': uuid
            })

    def related_xml(self):
        xml = self.env['barmex.invoice'].search([('invoice_id', '=', self.id)],
                                                limit=1)

        return {
            'name': _('XML Files'),
            'type': 'ir.actions.act_window',
            'res_model': 'barmex.invoice',
            'view_id': False,
            'view_type': 'tree,form',
            'view_mode': 'list',
            'target': 'current',
            'domain': [('id', '=', xml.id)],
        }

    @api.depends('reversal_move_id.state')
    def _get_credit_notes(self):
        for record in self:
            res = ''
            for nc in record.reversal_move_id:
                res += '{} '.format(nc.name)

            record.update({
                'credit_notes': res
            })

    def total_debit(self):
        sum = 0
        for line in self.line_ids:
            sum += line.debit

        return sum

    def total_credit(self):
        sum = 0
        for line in self.line_ids:
            sum += line.debit

        return sum

    def total_lines(self):
        sum = 0
        for line in self.line_ids:
            sum += 1
        return sum

    def _get_sequence(self):
        res = super()._get_sequence()
        debit_seq = self.journal_id.debit_sequence_id
        if not any((self.in_debit_note, self.out_debit_note)) or not debit_seq:
            return res
        return debit_seq

    def rate(self):
        res = 1
        if self.currency_id != self.env.company.currency_id:
            res = self.currency_id._convert(1, self.env.company.currency_id,
                                            self.company_id, self.invoice_date,
                                            round=False)
        return res

    def _get_external_trade_values(self, values):

        res = super(AccountMove, self)._get_external_trade_values(values)

        if not self.l10n_mx_edi_external_trade:
            return res

        customer = res['customer']

        res['receiver_reg_trib'] = customer.tax_id

        return res

    @api.model
    def l10n_mx_edi_get_customer_rfc(self):
        return self.vat

    def _l10n_mx_edi_post_sign_process(self, xml_signed, code=None, msg=None):

        super(AccountMove, self)._l10n_mx_edi_post_sign_process(xml_signed,
                                                                code, msg)

        template_id = self.env.ref('barmex.barmex_email_invoice_template').id
        mail = self.env['mail.template'].browse(template_id)
        type = ''
        if self.type == 'out_invoice':
            type = _('Invoice')

        if self.type == 'out_refund':
            type = _('Credit Note')

        if self.out_debit_note:
            type = _('Debit Note')

        mail.subject = type + mail.subject
        mail.body_html = _(
            "<p>Dear: {}</br>Attached you'll find PDF & XML files related to {} {}.</br>Greetings!</p>".format(
                self.partner_id.name, type, self.name))

        if self.partner_id.invoicing_mail:
            mail.email_to = self.partner_id.invoicing_mail
            mail.send_mail(self.id, force_send=True)

        if self.partner_id.payment_mail:
            mail.email_to = self.partner_id.payment_mail
            mail.send_mail(self.id, force_send=True)

    @api.onchange('currency_id')
    def change_currency(self):

        # curr=self.env.ref('base.main_company').currency_id
        # rate = self.env['res.currency'].search([('name','=','USD')],limit=1).rate
        # tc = 1 / rate
        # return {
        #    'warning': {
        #        'title': 'Entro a onChange',
        #        'message': tc,
        #    }
        # }

        tasa_cambio = 1 / (self.env['res.currency'].search(
            [('id', '=', int(self.currency_id))], limit=1).rate)
        self.barmex_currency_rate = tasa_cambio
