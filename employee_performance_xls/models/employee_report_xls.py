from odoo import models,fields,api,_

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt
import base64
from io import BytesIO
from datetime import date,time,datetime

class ProductBrandPL(models.Model):
    _inherit = 'product.brand'

    # fields to generate xls
    is_pl = fields.Boolean(string='Is PL', default=False)


class InvoiceXLSWizard(models.Model):

    _name = 'employee.popup'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    # employee_name = fields.Many2one('res.users', required=True)

    # fields for download xls

    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name =  fields.Char('File Name', size=32)


    @api.multi
    def generate_xls_report(self):

        self.ensure_one()

        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('Employee Details')
        fp  = BytesIO()


        #Content/Text style
        header_content_style = xlwt.easyxf("font: name Helvetica size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
        sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Helvetica, height 170;")
        row = 1
        col = 0
        ws1.row(row).height = 500
        ws1.write_merge(row,row, 3,7, "Employee Performance information", header_content_style)
        row += 2
        ws1.write(row, col+1, "From :", sub_header_style)
        ws1.write(row, col+2, datetime.strftime(datetime.strptime(self.date_from,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y"), sub_header_content_style)
        row += 1
        ws1.write(row, col+1, "To :", sub_header_style)
        ws1.write(row, col+2, datetime.strftime(datetime.strptime(self.date_to,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y"), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Employee", sub_header_style)
        ws1.write(row, col + 2, "Sold Units", sub_header_style)
        ws1.write(row, col + 3, "Net sls Total", sub_header_style)
        ws1.write(row, col + 4, "sls Tax", sub_header_style)
        ws1.write(row, col + 5, "sls Total w tax", sub_header_style)
        ws1.write(row, col + 6, "Net Disc", sub_header_style)
        # ws1.write(row, col + 7, "Net Disc", sub_header_style)
        ws1.write(row, col + 7, "Ave units per tra", sub_header_style)
        ws1.write(row, col + 8, "Ave vl sold", sub_header_style)
        ws1.write(row, col + 9, "# of sales", sub_header_style)
        ws1.write(row, col + 10, "PL sales", sub_header_style)
        ws1.write(row, col + 11, "PL %", sub_header_style)


        #Searching for sales persons in sale orders
        row+=1
        sale_details = self.env['sale.order'].search([('state','=','sale'),('date_order','<=',self.date_to),('date_order','>=',self.date_from)])
        salesperson = sale_details.mapped('user_id')

        for data in salesperson: ## salesperson
            pl_temp=0
            total_products = 0
            net_disc = 0
            total_disc = 0
            temp = 0
            total_amount_untax = 0
            total_amount_tax = 0
            total_amount_wttax = 0
            avg_sold = 0
            pl_amount=0
            total_pl = 0
            pl_percentage = 0
            saleorders = sale_details.search([('user_id', '=', data.id)])# to get the sale orders corresponds to the user
            no_orders = len(saleorders)
            for data in saleorders: ## sale orders
                total_products = total_products + sum(data.order_line.mapped('product_uom_qty'))
                total_amount_untax = total_amount_untax + float(data.amount_untaxed)
                total_amount_tax = total_amount_tax + float(data.amount_tax)
                for i in data.order_line:  ## to get the discount
                    if(i.product_id.product_brand_id.is_pl==True):
                        pl_amount = pl_amount + i.price_subtotal
                        pl_temp = pl_amount
                    net_disc = net_disc + (((i.price_unit) * (i.discount / 100))*(i.product_uom_qty))
                    temp = net_disc

            total_amount_wttax = total_amount_wttax + total_amount_untax + total_amount_tax
            avg_sold = avg_sold + (total_amount_untax/no_orders)
            avg_units_trans = float(total_products/no_orders)
            total_pl = total_pl + pl_temp
            total_disc = total_disc + temp
            pl_percentage = int((total_pl*100)/total_amount_wttax)

            col=0
            # ba1.write(row, col, data.user_id.id, line_content_style)
            ws1.write(row, col + 1, data.user_id.name, line_content_style)
            ws1.write(row, col + 2, total_products, line_content_style)
            ws1.write(row, col + 3, total_amount_untax, line_content_style)
            ws1.write(row, col + 4, total_amount_tax, line_content_style)
            ws1.write(row, col + 5, total_amount_wttax, line_content_style)
            ws1.write(row, col + 6, total_disc, line_content_style)
            ws1.write(row, col + 7, avg_units_trans, line_content_style)
            ws1.write(row, col + 8, avg_sold, line_content_style)
            ws1.write(row, col + 9, no_orders, line_content_style)
            ws1.write(row, col + 10, total_pl, line_content_style)
            ws1.write(row, col + 11, pl_percentage, line_content_style)
            row+=1


        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name':'employee_performance_detail.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'employee.popup',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
