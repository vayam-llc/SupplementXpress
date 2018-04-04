# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models
from datetime import datetime, timedelta


class IncomingOutgoingReport(models.Model):
    _name = "incoming.outgoing.report"
    _description = "Rebalancing Report"
    _auto = False

    location_id = fields.Many2one('stock.location', string="Location")
    company_id = fields.Many2one('res.company', string="Company")
    product_id = fields.Many2one('product.product', string="Product")
    product_template_id = fields.Many2one('product.template', string="Product Template")
    quantity = fields.Float('Qty On Hand')
    incoming = fields.Float('Incoming')
    outgoing = fields.Float('Outgoing')
    available = fields.Float('Available')
    net_available = fields.Float('Net Available')
    reorderpoint = fields.Boolean('Reorderpoint')
    product_min_qty = fields.Float('Min Qty')
    product_max_qty = fields.Float('Max Qty')
    product_max_qty = fields.Float('Max Qty')
    past_ninety_sales = fields.Float('90 Days Sales',compute='_compute_past_90',store=False)

    @api.multi
    def _compute_past_90(self):
        for record in self:
            if record.reorderpoint == True:
                N = 90
                now = datetime.now()
                daysago = now - timedelta(days=N)
                moves = record.env['stock.move'].search([
                ('date_done','>=',daysago.strftime('%Y-%m-%d %H:%M:%S')),
                ('date_done','<',now.strftime('%Y-%m-%d %H:%M:%S')),
                ('location_dest_id.usage','=','customer'),
                ('location_id','=',record.location_id.id),
                ('state','in',['done']),
                ('is_done','=',True),
                ('product_id','=',record.product_id.id),
                ])
                sales = 0
                sales += sum(moves.mapped('quantity_done'))
                record.past_ninety_sales = sales


    def _select(self):
        select_str = """
            SELECT MIN(id) as id,
                    virtual_table.location_id as location_id,
                    virtual_table.company_id as company_id,
                    virtual_table.product_id as product_id,
                    virtual_table.product_tmpl_id as product_template_id,
                    SUM(virtual_table.incoming) as incoming,
                    SUM(virtual_table.outgoing) as outgoing,
                    SUM(virtual_table.quantity) as quantity,
                    (SUM(virtual_table.quantity) - SUM(virtual_table.outgoing)) as available,
                    (SUM(virtual_table.quantity) + SUM(virtual_table.incoming) - SUM(virtual_table.outgoing)) as net_available,
                    SUM(virtual_table.product_min_qty) as product_min_qty,
                    SUM(virtual_table.product_max_qty) as product_max_qty,
                    virtual_table.reorderpoint as reorderpoint
        """
        return select_str

    def _from(self):
        from_str = """
                (SELECT
                    rule.id + (999999) AS id,
                    rule.product_id AS product_id,
                    product_template.id AS product_tmpl_id,
                    (rule.product_min_qty - rule.product_min_qty) AS quantity,
                    source_location.id AS location_id,
                    source_location.company_id AS company_id,
                    (rule.product_min_qty - rule.product_min_qty) AS incoming,
                    (rule.product_min_qty - rule.product_min_qty) AS outgoing,
                    rule.product_min_qty AS product_min_qty,
                    rule.product_max_qty AS product_max_qty,
                    (rule.id = rule.id) AS reorderpoint
                FROM
                    stock_warehouse_orderpoint as rule
                JOIN
                    stock_location source_location ON rule.location_id = source_location.id
                JOIN
                    product_product ON product_product.id = rule.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE rule.active='true')
                UNION ALL
                (SELECT
                    quant.id AS id,
                    quant.product_id AS product_id,
                    product_template.id AS product_tmpl_id,
                    quant.quantity AS quantity,
                    source_location.id AS location_id,
                    source_location.company_id AS company_id,
                    (quant.quantity - quant.quantity) AS incoming,
                    (quant.quantity - quant.quantity) AS outgoing,
                    (quant.quantity - quant.quantity) AS product_min_qty,
                    (quant.quantity - quant.quantity) AS product_max_qty,
                    (quant.id > quant.id) AS reorderpoint
                FROM
                    stock_quant as quant
                JOIN
                    stock_location source_location ON quant.location_id = source_location.id
                JOIN
                    product_product ON product_product.id = quant.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.quantity>0 AND source_location.usage in ('internal', 'transit'))
                UNION ALL
                (SELECT
                    (-100000) - move.id AS id,
                    move.product_id AS product_id,
                    product_template.id AS product_tmpl_id,
                    (move.ordered_qty - move.ordered_qty) AS quantity,
                    dest_location.id AS location_id,
                    dest_location.company_id AS company_id,
                    (move.ordered_qty) AS incoming,
                    (move.ordered_qty - move.ordered_qty) AS outgoing,
                    (move.ordered_qty - move.ordered_qty) AS product_min_qty,
                    (move.ordered_qty - move.ordered_qty) AS product_max_qty,
                    (move.id > move.id) AS reorderpoint
                FROM
                    stock_move as move
                JOIN
                    stock_picking_type types ON move.picking_type_id = types.id
                JOIN
                    stock_location source_location ON move.location_id = source_location.id
                JOIN
                    stock_location dest_location ON move.location_dest_id = dest_location.id
                JOIN
                    product_product ON product_product.id = move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE move.state in ('waiting','confirmed','assigned') AND types.code in ('incoming','internal'))
                UNION ALL
                (SELECT
                    (100000) + move.id AS id,
                    move.product_id AS product_id,
                    product_template.id AS product_tmpl_id,
                    (move.ordered_qty - move.ordered_qty) AS quantity,
                    source_location.id AS location_id,
                    source_location.company_id AS company_id,
                    (move.ordered_qty - move.ordered_qty) AS incoming,
                    move.ordered_qty AS outgoing,
                    (move.ordered_qty - move.ordered_qty) AS product_min_qty,
                    (move.ordered_qty - move.ordered_qty) AS product_max_qty,
                    (move.id > move.id) AS reorderpoint
                FROM
                    stock_move as move
                JOIN
                    stock_picking_type types ON move.picking_type_id = types.id
                JOIN
                    stock_location source_location ON move.location_id = source_location.id
                JOIN
                    stock_location dest_location ON move.location_dest_id = dest_location.id
                JOIN
                    product_product ON product_product.id = move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE move.state in ('waiting','confirmed','assigned') AND types.code in ('outgoing','internal'))
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY location_id,
                    company_id,
                    product_id,
                    product_template_id,
                    reorderpoint
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            AS virtual_table
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
