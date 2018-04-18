from odoo import api, fields, models, tools, _


class PurchaseCategory(models.Model):
    _name = 'purchase.category'

    name = fields.Char(compute="category_name")
    max_qty = fields.Integer(string="Maximum quantity")
    min_qty = fields.Integer(string="Minimum quantity")


    @api.depends('max_qty','min_qty')
    def category_name(self):
        for data in self:
            if data.max_qty and data.min_qty:
                data.name = str(data.max_qty)+'+'+str(data.min_qty)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_category = fields.Many2one('purchase.category', string='Purchase category')



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_category = fields.Many2one(string='Product category', related='product_id.product_tmpl_id.purchase_category', readonly=True)
    split= fields.Boolean('Splitted?')

    def order_line_splitting(self, res):
        print(res)
        reminder = 0.0
        min_line_qty = 0.0
        max_line_qty = 0.0
        purchase_category_qty = res.purchase_category.min_qty + res.purchase_category.max_qty
        print('purchase_category_qty', purchase_category_qty)
        if purchase_category_qty != 0:
            reminder = res.product_qty % purchase_category_qty
        print("reminder", reminder)

        if reminder != 0:
            qty_required = purchase_category_qty - reminder
            set_product_qty = res.product_qty + qty_required
        else:
            set_product_qty = res.product_qty

        if purchase_category_qty != 0:
            min_line_qty = (res.purchase_category.max_qty / purchase_category_qty) * (set_product_qty)
            max_line_qty = (res.purchase_category.min_qty / purchase_category_qty) * (set_product_qty)

        res.product_qty = min_line_qty
        res.split = True
        vals = {
            'product_id': res.product_id.id,
            'name': res.product_id.name,
            'order_id': res.order_id.id,
            'price_unit':0.0,
            'product_qty': max_line_qty,
            'product_uom': res.product_id.uom_po_id.id,
            'purchase_category': res.purchase_category.id,
            'date_planned': res.date_planned,
            'split': True
        }
        self.env['purchase.order.line'].create(vals)

    # function for creating new orderline
    @api.model
    def create(self, vals):
        po = super(PurchaseOrderLine, self).create(vals)
        for data in po:
            if data.purchase_category and data.split == False:
                self.order_line_splitting(data)

        return po


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    purchase_category = fields.Many2one(string='Purchase category', related='product_id.product_tmpl_id.purchase_category', readonly=True)
    category_check = fields.Boolean(compute='purchase_category_check_', string="Quantity multiple")

    @api.depends('purchase_category')
    def purchase_category_check_(self):
        for record in self:
            if len(record.purchase_category)>0:
                record.category_check = True
            else:
                record.category_check = False






