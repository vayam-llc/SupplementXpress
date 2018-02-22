from odoo import fields,models,api,_
import re
from odoo.osv import expression
from odoo.tools import float_is_zero

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    secondary_uom_id = fields.Many2one('product.uom',string="Unit Of Measure")
    secondary_price = fields.Float('Price')
    secondary_barcode = fields.Char(
        'Barcode', copy=False, oldname='ean13',
        help="International Article Number used for product identification.")

    _sql_constraints = [
        ('barcode_secondary_uniq', 'unique(secondary_barcode)', _("A barcode can only be assigned to one product !")),
    ]



class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        print("inside uom change")
        if not self.product_uom:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id,
                quantity=self.product_uom_qty,
                date_order=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )

            # multi_price = self.env['product.product'].search([('secondary_uom_id','=',self.product_id.product_tmpl_id.id),('uom_id','=',self.product_uom.id)])
            if self.product_uom.id == self.product_id.uom_id.id:
                self.price_unit = self.product_id.secondary_price
            else:
                self.price_unit = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)


class Product(models.Model):

    _inherit = 'product.product'


    secondary_uom_id = fields.Many2one('product.uom',string="Secondary Unit Of Measure",related = 'product_tmpl_id.secondary_uom_id')
    secondary_price = fields.Float('Price',related='product_tmpl_id.secondary_price')
    secondary = fields.Boolean()
    secondary_barcode = fields.Char(
        'Barcode', copy=False, oldname='ean13',
        help="International Article Number used for product identification.",related = 'product_tmpl_id.secondary_barcode')

    # _sql_constraints = [
    #     ('barcode_secondary_uniq', 'unique(secondary_barcode)', _("A barcode can only be assigned to one product !")),
    # ]


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            products = self.env['product.product']
            if operator in positive_operators:
                products = self.search([('default_code', '=', name)] + args, limit=limit)
                if not products:
                    products = self.search([('barcode', '=', name)] + args, limit=limit)
                    if not products:
                        products = self.search([('secondary_barcode', '=', name)]+args,limit=limit)
            if not products and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                products = self.search(args + [('default_code', operator, name)], limit=limit)
                if not limit or len(products) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(products)) if limit else False
                    products += self.search(args + [('name', operator, name), ('id', 'not in', products.ids)], limit=limit2)
            elif not products and operator in expression.NEGATIVE_TERM_OPERATORS:
                products = self.search(args + ['&', ('default_code', operator, name), ('name', operator, name)], limit=limit)
            if not products and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    products = self.search([('default_code', '=', res.group(2))] + args, limit=limit)
            # still no results, partner in context: search on supplier info as last hope to find something
            if not products and self._context.get('partner_id'):
                suppliers = self.env['product.supplierinfo'].search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)])
                if suppliers:
                    products = self.search([('product_tmpl_id.seller_ids', 'in', suppliers.ids)], limit=limit)
        else:
            products = self.search(args, limit=limit)
        return products.name_get()


class PosOrderLine(models.Model):

    _inherit = 'pos.order.line'

    secondary = fields.Boolean('Is Secondary UOM')

class PosOrder(models.Model):

    _inherit = 'pos.order'

    def create_picking(self):
        """Create a picking for each order and validate it."""
        print("inside")
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                continue
            address = order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
            order_picking = Picking
            return_picking = Picking
            moves = Move
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = StockWarehouse._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id

            if picking_type:
                message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
                picking_vals = {
                    'origin': order.name,
                    'partner_id': address.get('delivery', False),
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                }
                pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if pos_qty:
                    order_picking = Picking.create(picking_vals.copy())
                    order_picking.message_post(body=message)
                neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if neg_qty:
                    return_vals = picking_vals.copy()
                    return_vals.update({
                        'location_id': destination_id,
                        'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                        'picking_type_id': return_pick_type.id
                    })
                    return_picking = Picking.create(return_vals)
                    return_picking.message_post(body=message)

            for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_digits=l.product_id.uom_id.rounding)):
                uom_id = line.product_id.uom_id.id
                print("unit_price=%s"%line.price_unit)
                if line.price_unit == line.product_id.secondary_price:
                    uom_id = line.product_id.secondary_uom_id.id
                moves |= Move.create({
                    'name': line.name,
                    'product_uom': uom_id,
                    'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                    'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': location_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                })

            # prefer associating the regular order picking, not the return
            order.write({'picking_id': order_picking.id or return_picking.id})

            if return_picking:
                order._force_picking_done(return_picking)
            if order_picking:
                order._force_picking_done(order_picking)

            # when the pos.config has no picking_type_id set only the moves will be created
            if moves and not return_picking and not order_picking:
                moves._action_assign()
                moves.filtered(lambda m: m.state in ['confirmed', 'waiting']).force_assign()
                moves.filtered(lambda m: m.product_id.tracking == 'none')._action_done()

        return True

