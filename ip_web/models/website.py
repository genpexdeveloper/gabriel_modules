# -*- coding: utf-8 -*-
import uuid
import math
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
from openerp.addons.web import http
from openerp.osv import orm, fields
from openerp.addons.web.http import request
from openerp import SUPERUSER_ID


class Website(orm.Model):
    _inherit = 'website'
    def preprocess_request(self, cr, uid, ids, request, context=None):
        request.context.update({
            'website_sale_categories': self.get_categories(cr, uid, request, context),
            'website_sale_attributes': self.get_attribute_ids(),
        })
        return super(Website, self).preprocess_request(cr, uid, ids, request, context=context)
    
    def get_categories(self, cr, uid,ids, context=None):
        categories = []
        base_domain = self.pool['website'].sale_product_domain(self, cr, uid, ids)
        if context:
            product_obj = self.pool['product.template']
            category_obj = self.pool['product.public.category']
            #TODO change
            #category_ids = [product['public_categ_id'][0] for product in product_obj.read_group(cr, uid, base_domain, ['public_categ_ids'], ['public_categ_id'], context=context) if product['public_categ_id']]
            category_ids = self.pool['product.public.category'].search(cr, uid, [], context=context)
            categories = category_obj.browse(cr, uid, category_ids, context=context)
            all_categories = set(categories)
            for cat in categories:
                parent = cat.parent_id
                while parent:
                    all_categories.add(parent)
                    parent = parent.parent_id
            categories = list(all_categories)
            categories.sort(key=lambda x: x.sequence)
        return categories

    def pager(self, cr, uid, ids, url, total, page=1, step=30, scope=5, url_args=None, context=None):
        # Compute Pager
        page_count = int(math.ceil(float(total) / step))

        page = max(1, min(int(page if str(page).isdigit() else 1), page_count))
        scope -= 1

        pmin = max(page - int(math.floor(scope/2)), 1)
        pmax = min(pmin + scope, page_count)

        if pmax - pmin < scope:
            pmin = pmax - scope if pmax - scope > 0 else 1

        def get_url(page):
            _url = "%s/page/%s" % (url, page) if page > 1 else url
            if url_args:
                _url = "%s?%s" % (_url, werkzeug.url_encode(url_args))
            return _url

        return {
            "total":total,
            "page_count": page_count,
            "offset": (page - 1) * step,
            "page": {
                'url': get_url(page),
                'num': page
            },
            "page_start": {
                'url': get_url(pmin),
                'num': pmin
            },
            "page_previous": {
                'url': get_url(max(pmin, page - 1)),
                'num': max(pmin, page - 1)
            },
            "page_next": {
                'url': get_url(min(pmax, page + 1)),
                'num': min(pmax, page + 1)
            },
            "page_end": {
                'url': get_url(pmax),
                'num': pmax
            },
            "pages": [
                {'url': get_url(page), 'num': page}
                for page in xrange(pmin, pmax+1)
            ]
        }

    def get_attribute_ids(self):
        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(request.cr, request.uid, [], context=request.context)
        return attributes_obj.browse(request.cr, request.uid, attributes_ids, context=request.context)