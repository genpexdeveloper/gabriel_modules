{
    'name': 'Incontinence Protection Website',
    'category': 'Theme',
    'summary': 'Customisations for Incontinence Protection E-Commerce front end',
    'version': '1.0',
    'description': """
Incontinence Protection Customisations
======================================

        """,
    'author': 'OpenERP S.A',
    'depends': ['ip_web_addons'],
    'data': [
        'views/product_form.xml',
        'views/layout.xml',
        'views/homepage.xml',
        'views/products.xml',
        'views/product.xml',
        'views/login.xml',
        'views/snippets.xml',
        'views/checkout.xml',
        'views/account.xml',
        'views/address.xml',
        'views/_partial/top-cart.xml',
        'views/_partial/top-search.xml',
        'views/_partial/main-nav.xml',
        'views/_partial/recommended-products.xml',
        'views/_partial/bought-together-products.xml',
        'views/_partial/product-reviews.xml',
        'views/_partial/product-description.xml',
        'views/_partial/brands-list.xml'
    ],
    'installable': True,
}
