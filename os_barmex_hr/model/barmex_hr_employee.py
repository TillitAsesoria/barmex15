# -*- coding: utf-8 -*-
from odoo import models, fields, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    lco_opportunity_ids = fields.Many2many(
        'crm.lead',
        'crm_lead_hr_employee_rel',
        'hr_employee_id',
        'crm_lead_id',
        string='Opportunities')
    lco_ventas_mostrador = fields.Boolean('Check-in sale')
    address_id = fields.Many2one(
        'res.partner', 'Work Address',
        domain="['|',('type', '=', 'other'),('parent_id','=', address_filter)]"
    )
    address_filter = fields.Integer(compute="set_filter")
    employee_sale_zone = fields.Many2one(
        'barmex.sale.zone',
        string='Sale zone',
        stored=True,
        track_visibility=True,
        check_company=True)
    sequence = fields.Integer(default=1)

    def set_filter(self):
        for record in self:
            record.update({
                'address_filter': self.env.company.partner_id.id,
            })


class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    lco_ventas_mostrador = fields.Boolean('Check-in sale')
