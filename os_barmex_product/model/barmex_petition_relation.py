from odoo import models, fields, api, _


class PetitionRelation(models.Model):
    _name = 'barmex.petition.relation'
    _description = 'Petition Relation'
    _order = 'id desc'
    _check_company_auto = True

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.company)
    product_id = fields.Many2one(
        'product.product',
        string="Product")
    available = fields.Float(string="Available")
    petition = fields.Char(string="Petition")
    date = fields.Date(string="Date")
