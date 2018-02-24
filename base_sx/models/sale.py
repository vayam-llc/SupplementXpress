# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    real_time_margin = fields.Float(string='Order Margin',compute='calculate_real_time_margin',store="True",readonly="True")
    real_time_margin_perc = fields.Float(string='Order Margin (%)',compute='calculate_real_time_margin',store="True",readonly="True")

    @api.depends('order_line.product_id','order_line.product_uom_qty','order_line.price_unit')
    def calculate_real_time_margin(self):
        for record in self:
            calcmargin = 0
            for line in record.order_line:
                calcmargin += line.real_time_margin
            record.real_time_margin = calcmargin
            if record.amount_untaxed > 0:
                record.real_time_margin_perc = round((calcmargin/record.amount_untaxed)*100,2)

    @api.multi
    def action_confirm(self):
        if self.partner_id.credit_limit > 0:
            customer_limit = self.partner_id.credit_limit
            customer_credit = self.partner_id.credit
            order_total = self.amount_total
            if (customer_credit + order_total) > customer_limit:
                action_data = self.env.ref('base_sx.action_sale_order_credit_limit_wizard').read()[0]
                action_data.update({'domain':[('sale_id','=',self.id)],'context':{'default_sale_id':self.id}})
                return action_data
        else:
            self._action_confirm()
            if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
                self.action_done()
            return True

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    real_time_margin = fields.Float(string='Margin',compute='calculate_real_time_margin',store="True",readonly="True")
    real_time_margin_perc = fields.Float(string='Margin (%)',compute='calculate_real_time_margin',store="True",readonly="True")

    @api.depends('product_id','product_uom_qty','price_unit')
    def calculate_real_time_margin(self):
        for record in self:
            record.real_time_margin = (record.price_unit - record.product_id.standard_price)*record.product_uom_qty
            if record.price_unit > 0:
                record.real_time_margin_perc = round(((record.price_unit - record.product_id.standard_price)/record.price_unit)*100,2)

class SaleOrderCreditLimitWizard(models.TransientModel):
    _name = "sale.order.credit.limit.wizard"
    _description = "Sale Order Credit Limit Wizard"

    sale_id = fields.Many2one('sale.order',string="Sale Order")
    credit_limit = fields.Float('Credit Limit',compute="_compute_over", store=False,readonly=True)
    credit = fields.Float('Credit',compute="_compute_over", store=False,readonly=True)
    over_limit = fields.Float('Over By',compute="_compute_over",store=False,readonly=True)

    @api.multi
    @api.depends('sale_id')
    def _compute_over(self):
        for wiz in self:
            wiz.credit = wiz.sale_id.partner_id.credit
            wiz.credit_limit = wiz.sale_id.partner_id.credit_limit
            wiz.over_limit = wiz.credit + wiz.sale_id.amount_total - wiz.credit_limit

    @api.multi
    def force_confirm(self):
        for wiz in self:
            saleorder = wiz.sale_id
            saleorder._action_confirm()
            if saleorder.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
                saleorder.action_done()
            return True
