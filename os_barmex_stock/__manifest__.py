{
    'name': 'OS Barmex Stock',
    'version': '15.0',
    'author': 'OS Barmex Stock',
    'website': '',
    'category': 'stock',
    'sequence': 6,
    'licence': 'AGPL-3',
    'summary': 'OS Barmex Stock',
    'depends': [
        'os_barmex',
        'stock'
    ],
    'data': [
        'security/company_filters.xml',
        'security/ir.model.access.csv',
        'views/barmex_foreign_trade.xml',
        'views/barmex_foreign_trade_customs.xml',
        'views/barmex_stock_move.xml',
        'views/barmex_stock_picking.xml',
        'views/barmex_stock_production_lot.xml',
        'views/barmex_stock_warehouse.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
