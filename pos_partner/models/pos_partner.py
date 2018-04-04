
from odoo import models,fields

class CustomerType(models.Model):
    _name='customer.type'

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")


class PosPartner(models.Model):
    _inherit = 'res.partner'

    customer_type = fields.Many2one('customer.type','Customer Type')