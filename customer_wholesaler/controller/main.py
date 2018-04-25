from odoo.addons.website.controllers.main import Website
from odoo import http
from odoo.http import request
import json
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL


PPG = 18
PPR = 4


class WebsiteSale(WebsiteSale):

    @http.route(['/wholesale_page'], type='http', auth="public", website=True)
    def wholesale(self, page=0, category=None, search='', ppg=False, **post):
        user_details = request.env['res.users'].browse(request.uid)
        if(user_details.partner_id.wholesaler == True):
            if ppg:
                try:
                    ppg = int(ppg)
                except ValueError:
                    ppg = PPG
                post["ppg"] = ppg
            else:
                ppg = PPG

            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}

            domain = self._get_search_domain(search, category, attrib_values)

            keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

            compute_currency, pricelist_context, pricelist = self._get_compute_currency_and_context()

            request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

            url = "/shop"
            if search:
                post["search"] = search
            if category:
                category = request.env['product.public.category'].browse(int(category))
                url = "/shop/category/%s" % slug(category)
            if attrib_list:
                post['attrib'] = attrib_list

            categs = request.env['product.public.category'].search([('parent_id', '=', False)])
            Product = request.env['product.template']

            parent_category_ids = []
            if category:
                parent_category_ids = [category.id]
                current_category = category
                while current_category.parent_id:
                    parent_category_ids.append(current_category.parent_id.id)
                    current_category = current_category.parent_id

            product_count = Product.search_count(domain)
            pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

            ProductAttribute = request.env['product.attribute']
            if products:
                # get all products without limit
                selected_products = Product.search(domain, limit=False)
                attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', selected_products.ids)])
            else:
                attributes = ProductAttribute.browse(attributes_ids)

            values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
            }
            if category:
                values['main_object'] = category
            return request.render("customer_wholesaler.products", values)
        else:
            return request.render("theme_crafito.user_invalid")


   

