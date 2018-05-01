# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

# filter pricelist on customer type once creating a partner
    def create(self, vals):
        if vals:
            if vals['customer_type']:
                p_pricelist_id = self.env['product.pricelist'].search([
                    ('customer_type', '=', int(vals['customer_type']))]).id
                if p_pricelist_id:
                    vals['property_product_pricelist'] = self.env['product.pricelist'].search([
                        ('customer_type', '=', int(vals['customer_type']))]).id
        return super(Partner, self).create(vals)

# filtering pricelist on changing customer type in partner form
    @api.onchange('customer_type')
    def onchange_customer_type(self):
        if self.customer_type:
            self.property_product_pricelist = self.env['product.pricelist'].search([
                ('customer_type', '=', self.customer_type.id)])
