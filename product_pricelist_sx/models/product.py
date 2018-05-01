# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class Producttemplate(models.Model):
    _inherit = "product.template"

    ws_price = fields.Float(
        'MSWP', digits=dp.get_precision('Product Price'),
        help="Provide the whole sale price of products here.")

class Productproduct(models.Model):
    _inherit = "product.product"

    ws_price = fields.Float('MSWP', compute='_compute_product_wsp_price',
         digits=dp.get_precision('Product Price'),
        help="Provide the whole sale price of products here.")

    @api.depends('ws_price', 'price_extra')
    def _compute_product_wsp_price(self):
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['product.uom'].browse([self._context['uom']])
        for product in self:
            if to_uom:
                ws_price = product.uom_id._compute_price(product.product_tmpl_id.ws_price, to_uom)
            else:
                ws_price = product.product_tmpl_id.ws_price
            product.ws_price = ws_price + product.price_extra


    @api.multi
    def wholesaleprice_compute(self, price_type, uom=False, currency=False, company=False):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['product.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_context(force_company=company and company.id or self._context.get('force_company', self.env.user.company_id.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            prices[product.id] = product[price_type] or 0.0
            # check if wholesale price is not zero
            if price_type == 'list_price':
                prices[product.id] += product.price_extra
                if product.price_compute('ws_price')[product.id] > 0:
                        prices[product.id] = product.price_compute('ws_price')[product.id]

            if uom:
                prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id.compute(prices[product.id], currency)

        return prices