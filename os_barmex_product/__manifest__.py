{
    'name': 'OS Barmex Product',
    'version': '15.0',
    'author': 'OS Barmex Product',
    'website': '',
    'category': 'product',
    'sequence': 4,
    'licence': 'AGPL-3',
    'summary': 'OS Barmex Product',
    'depends': [
        'os_barmex',
        'product',
        'l10n_mx_edi_extended'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/barmex_automated_actions.xml',
        'views/barmex_dialog_box.xml',
        'views/barmex_product_brand.xml',
        'views/barmex_product_category.xml',
        'views/barmex_product_group.xml',
        'views/barmex_product_pricelist.xml',
        'views/barmex_product_product.xml',
        'views/barmex_product_speciallity.xml',
        'views/barmex_product_subgroup.xml',
        'views/barmex_product_subline.xml',
        'views/barmex_product_template.xml',
        'views/barmex_product_template_product_form.xml',
        'views/menu.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
