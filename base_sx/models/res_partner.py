# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = "res.partner"

    manufacture_price = fields.Boolean('Manufacture Wholesale Price (MWSP)')
    vip_price = fields.Boolean('VIP Price')
