from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):

    _inherit = "res.partner"

    sent_mail = fields.Boolean(string="Mail sent")
    sent_mail_24 = fields.Boolean(string="24 days notification")
    sent_mail_32 = fields.Boolean(string="32 days notification")
    sent_mail_60 = fields.Boolean(string="60 days notification")

    # function for sending welcome notification to the customer when it is created

    @api.model
    def create(self,vals):
        res = super(ResPartner, self).create(vals)
        if vals:
            template = self.env.ref('mail_notification.email_template_customer_welcome')
            mail_id = template.send_mail(res.id, force_send=True)
        return res

    # function for sending mail after 24 hours after customer creation

    @api.model
    def customer_notification(self):
        customers = self.env['res.partner'].search([('customer', '=', True)])
        for customer in customers:
            if customer.sent_mail == False:
                template = self.env.ref('mail_notification.email_template_customer_day_notification')
                mail_id = template.send_mail(customer.id, force_send=True)
                customer.write({
                    'sent_mail': True
                })


class SaleOrder(models.Model):

    _inherit = "sale.order"


    # function for sending mail for made a purchase but has not made another purchase in 24

    @api.model
    def customer_purchase_notification_24(self):
        sale_orders = self.env['sale.order'].search([('state', '=', 'sale')])
        today_dt = datetime.now()
        target_date_24 = today_dt - relativedelta(days=24)
        for sale_order in sale_orders:
            confirmation_date = fields.Datetime.from_string(sale_order.confirmation_date)
            if confirmation_date:
                if confirmation_date < target_date_24 and sale_order.partner_id.sent_mail_24 == False:
                    template = self.env.ref('mail_notification.email_template_last_purachse_24')
                    template.send_mail(sale_order.partner_id.id, force_send=True)
                    sale_order.partner_id.sent_mail_24.write({'sent_mail_24': True})

    # function for sending mail for made a purchase but has not made another purchase in 32

    @api.model
    def customer_purchase_notification_32(self):
        sale_orders = self.env['sale.order'].search([('state', '=', 'sale')])
        today_dt = datetime.now()
        target_date_32 = today_dt - relativedelta(days=32)
        for sale_order in sale_orders:
            confirmation_date = fields.Datetime.from_string(sale_order.confirmation_date)
            if confirmation_date:
                if confirmation_date < target_date_32 and sale_order.partner_id.sent_mail_32 == False:
                    template = self.env.ref('mail_notification.email_template_last_purachse_32')
                    template.send_mail(sale_order.partner_id.id, force_send=True)
                    sale_order.partner_id.sent_mail_32.write({'sent_mail_32': True})

    # function for sending mail for made a purchase but has not made another purchase in 60

    @api.model
    def customer_purchase_notification_60(self):
        sale_orders = self.env['sale.order'].search([('state', '=', 'sale')])
        today_dt = datetime.now()
        target_date_60 = today_dt - relativedelta(days=60)
        for sale_order in sale_orders:
            confirmation_date = fields.Datetime.from_string(sale_order.confirmation_date)
            if confirmation_date:
                if confirmation_date < target_date_60 and sale_order.partner_id.sent_mail_60 == False:
                    template = self.env.ref('mail_notification.email_template_last_purachse_60')
                    template.send_mail(sale_order.partner_id.id, force_send=True)
                    sale_order.partner_id.sent_mail_60.write({'sent_mail_60': True})