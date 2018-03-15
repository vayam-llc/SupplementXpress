# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    past_ninety_sales = fields.Float('90 Days Sales',compute='_compute_values',store=False)
    past_ninety_sales_value = fields.Float('90 Days Sales ($)',compute='_compute_values',store=False)
    quantity_available = fields.Float('Current Qty',compute='_compute_values',store=False)
    quantity_over = fields.Float('Overstock Qty',compute='_compute_values',store=False)
    avg_daily_sales = fields.Float('Avg. Daily Sales',compute='_compute_values',store=False)
    min_proposed = fields.Float('Minimum Proposed',compute='_compute_values',store=False)
    days_on_hand = fields.Float('Days on Hand',compute='_compute_values',store=False)
    perc_of_total = fields.Float("Perc of Total",compute='_compute_values',store=False)
    movement_classification = fields.Selection([
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ], string='Movement Classification',compute='_compute_values',store=False)

    @api.multi
    def open_rebalance_wizard(self):
        action_data = self.env.ref('base_sx.action_stock_movement_wizard').read()[0]
        action_data.update({'context':{'default_location_id':self.location_id.id,'default_product_id':self.product_id.id,'default_stock_warehouse_orderpoint':self.id}})
        return action_data

    @api.multi
    def _compute_values(self):
        for record in self:
            N = 90
            now = datetime.now()
            daysago = now - timedelta(days=N)
            moves = record.env['stock.move'].search([
            ('date_done','>=',daysago.strftime('%Y-%m-%d %H:%M:%S')),
            ('date_done','<',now.strftime('%Y-%m-%d %H:%M:%S')),
            ('location_dest_id.usage','=','customer'),
            ('location_id','=',record.location_id.id),
            ('state','in',['done']),
            ('product_id','=',record.product_id.id),
            ])
            moves_not_location = record.env['stock.move'].search([
            ('date_done','>=',daysago.strftime('%Y-%m-%d %H:%M:%S')),
            ('date_done','<',now.strftime('%Y-%m-%d %H:%M:%S')),
            ('location_dest_id.usage','=','customer'),
            ('location_id','=',record.location_id.id),
            ('state','in',['done']),
            ])
            sales = 0
            sales += sum(moves.mapped('quantity_done'))
            sales_not_location = 0
            sales_not_location += sum(moves_not_location.mapped('quantity_done'))
            record.past_ninety_sales = sales
            record.past_ninety_sales_value = sales * record.product_id.list_price
            record.avg_daily_sales = sales/N
            products_dict = {}
            for m in moves_not_location:
                this_product_amount = products_dict.get(m.product_id.id, [0,''])
                products_dict.update({m.product_id.id: [this_product_amount[0] + m.quantity_done,m.product_id.name]})
            sorted_products = [ (v,k) for k,v in products_dict.items() ]
            sorted_products.sort(reverse=True)
            cumm_amount = 0
            index = 0
            for a in sorted_products:
                index += 1
                cumm_amount += a[0][0]
                if a[1] == record.product_id.id and sales_not_location > 0:
                    percent = round((cumm_amount/sales_not_location),2)
                    record.perc_of_total = round((sales/sales_not_location),4)*100
                    if percent <= 0.50 or record.perc_of_total >= 50:
                        record.movement_classification = 'a'
                        record.min_proposed = 1.64 * record.avg_daily_sales
                    elif percent <= 0.75 or record.perc_of_total >= 25:
                        record.movement_classification = 'b'
                        record.min_proposed = 1.04 * record.avg_daily_sales
                    elif percent <= 0.85 or record.perc_of_total >= 10:
                        record.movement_classification = 'c'
                        record.min_proposed = 0.84 * record.avg_daily_sales
                    else:
                        record.movement_classification = 'd'
                        record.min_proposed = 0 * record.avg_daily_sales
                    break
            quants = record.env['stock.quant'].search([
            ('location_id','=',record.location_id.id),
            ('location_id.usage','in',['internal','transit']),
            ('quantity','>',0),
            ('product_id','=',record.product_id.id),
            ])
            avl = sum(quants.mapped('quantity'))
            record.quantity_available = avl
            record.quantity_over = avl - record.min_proposed
            if record.avg_daily_sales > 0:
                record.days_on_hand = avl/record.avg_daily_sales

class StockMovementWizard(models.TransientModel):
    _name = "stock.movement.wizard"
    _description = 'Stock Movement Wizard'

    quantity = fields.Float("Quantity", required=True)
    location_id = fields.Many2one('stock.location', string="Source Location")
    location_dest_id = fields.Many2one('stock.location', string="Destination Location")
    product_id = fields.Many2one('product.product', string="Product")
    picking_type_id = fields.Many2one('stock.picking.type', string="Picking Type")
    stock_warehouse_orderpoint = fields.Many2one('stock.warehouse.orderpoint', string="Reordering Rule")
    orderpoint_ids = fields.Many2many('stock.warehouse.orderpoint',compute='_find_other_order_points',store=True)

    @api.multi
    @api.depends('location_id')
    def _find_other_order_points(self):
        for record in self:
            orderpoints = record.env['stock.warehouse.orderpoint'].search([('product_id','=',record.product_id.id)])
            if orderpoints:
                record.orderpoint_ids = [(6,0,orderpoints.ids)]

    @api.onchange('orderpoint_ids')
    def _apply_domain_on_locations(self):
        for record in self:
            locations = record.orderpoint_ids.mapped('location_id').ids
            action = {'domain': {'location_dest_id': [('id', 'in', locations)],'location_id': [('id', 'in', locations)]}}
            return action

    @api.onchange('location_id')
    def select_picking_type(self):
        for record in self:
            types = record.env['stock.picking.type'].search([('code','=','internal'),'|',('default_location_src_id','=',record.location_id.id),('default_location_dest_id','=',record.location_id.id)])
            if types:
                record.picking_type_id = types[0]
    @api.multi
    def create_move(self):
        for record in self:
            quants = sum(record.env['stock.quant'].search([('location_id','=',record.location_id.id),('product_id','=',record.product_id.id)]).mapped('quantity'))
            if quants < record.quantity:
                raise UserError(_('Not enough inventory to satisfy a move of %s %s.' % (record.quantity,record.product_id.uom_id.name)))
            picking_data = {
                'location_dest_id': record.location_dest_id.id,
                'origin': 'Rebalance Wizard',
                'location_id': record.location_id.id,
                'move_type': 'one',
                'picking_type_id': record.picking_type_id.id,
            }
            picking = record.env['stock.picking'].create(picking_data)
            new_move = record.env['stock.move']
            move_data = {
                'location_dest_id': record.location_dest_id.id,
                'product_uom': record.product_id.uom_id.id,
                'product_id': record.product_id.id,
                'product_uom_qty': record.quantity,
                'name': 'Movement Wizard',
                'date': datetime.now(),
                'date_expected': datetime.now(),
                'location_id': record.location_id.id,
                'picking_id': picking.id,
            }
            new_record = new_move.new(move_data)
            new_move += new_record
            picking.move_lines += new_move
            picking.action_confirm()
            picking.action_assign()
            return {}
