from odoo import models,fields

class CRMLead(models.Model):
    _inherit = "crm.lead"
    _description = 'add currency to crm.lead'

    currency_lead = fields.Selection([('MXN','MXN'),('USD','USD'),('EUR','EUR'),('other','Other')],'Moneda', default='MXN')