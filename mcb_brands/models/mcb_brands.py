from odoo import models,fields,api,_
import datetime



class mcb_product_brand(models.Model):
    _inherit = 'product.brand'

    is_mcb = fields.Boolean(string='Is MCB', default=False)
    mcb = fields.One2many('mcb.brand','mcb_product_brand')


class mcb_product__brand_relation(models.Model):
    _name = 'mcb.brand'

    mcb_product_brand = fields.Many2one('product.brand')
    tier = fields.Many2one('tier.brand', string="Tier")
    rebate = fields.Char(string="Rebate Percentage")
    amount = fields.Float(string="Amount")



class TierBrand(models.Model):
    _name = 'tier.brand'
    _rec_name = 'tier_name1'

    tier_name1 = fields.Char(string="Name")


