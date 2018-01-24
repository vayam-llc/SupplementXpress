# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = "stock.move"

    date_done = fields.Datetime('Closed Date',related='picking_id.date_done', store=True, readonly=True)
