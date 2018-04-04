# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    past_price_unit = fields.Float('Past Unit Price',compute='_compute_past_purchase_price',store=True,readonly=True)
    avg_past_price_unit = fields.Float('Avg. Past Unit Price',compute='_compute_past_purchase_price',store=True,readonly=True)

    @api.depends('product_id')
    def _compute_past_purchase_price(self):
        for line in self:
            if line.product_id:
                purchase_order_lines = line.env['purchase.order.line'].search([
                ('partner_id','=',line.partner_id.id),
                ('product_id','=',line.product_id.id),
                ('state','not in',['cancel','draft','sent','to approve'])
                ])
                if purchase_order_lines:
                    qty = 0
                    subtotal = 0
                    for poline in purchase_order_lines:
                        qty += poline.product_qty
                        subtotal += poline.price_subtotal
                    if qty > 0:
                        avg = round(subtotal/qty,2)
                    else:
                        avg = 0
                    line.past_price_unit = purchase_order_lines[0].price_unit
                    line.avg_past_price_unit = avg

    @api.onchange('price_unit')
    def onchange_price_unit(self):
       if round(self.price_unit,2) > round(self.past_price_unit,2):
           return {'value':{},'warning':{'title':'Current Purchase Price High','message':'The selected purchase price of $%s is greater than the last purchased price of $%s  by $%s(Avg. Vendor Price: $%s).' % (round(self.price_unit,2),round(self.past_price_unit,2),round(self.price_unit - self.past_price_unit,2),self.avg_past_price_unit)}}

    @api.multi
    def open_past_prices(self):
        action_data = self.env.ref('base_sx.action_purchase_order_line_tree').read()[0]
        action_data.update({'domain':[('product_id','=',self.product_id.id),('state','not in',['cancel','draft','sent','to approve']),('id','!=',self.id)]})
        return action_data
