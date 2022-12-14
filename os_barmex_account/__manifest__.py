{
    'name': 'OS Barmex Account',
    'version': '15.0',
    'author': 'OS Barmex Account',
    'website': '',
    'category': 'hr',
    'sequence': 2,
    'licence': 'AGPL-3',
    'summary': 'OS Barmex Account',
    'depends': [
        'os_barmex',
        'os_barmex_product'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/barmex_account_asset.xml',
        'views/barmex_account_bank_statement.xml',
        'views/barmex_account_change_lock_date.xml',
        'views/barmex_account_journal.xml',
        'views/barmex_account_move.xml',
        'views/barmex_account_move_debit_view.xml',
        'views/barmex_account_move_reversal.xml',
        'views/barmex_account_payment.xml',
        'views/barmex_action.xml',
        'views/barmex_conversion.xml',
        'views/barmex_credit_note.xml',
        'views/barmex_payment.xml',
        'views/barmex_server_action.xml',
        'views/barmex_writeoff_reasons.xml',
        'wizards/barmex_account_journal_wizard.xml',
        'wizards/barmex_alert.xml',
        'views/barmex_menu.xml',

        'reports/barmex_account_journal_report.xml',
        'reports/barmex_account_journal_template.xml',
        'reports/barmex_account_payment_report.xml',
        'reports/barmex_base_templates.xml',
        'reports/barmex_cost_effectiveness.xml',
        'reports/barmex_cost_effectiveness_template.xml',
        'reports/barmex_customer_aging.xml',
        'reports/barmex_customer_aging_template.xml',
        'reports/barmex_invoice_report.xml',
        'reports/barmex_invoice_template.xml',
        'reports/barmex_note_cargo_template.xml',
        'reports/barmex_reception_template.xml',
        'reports/barmex_reports.xml',
        'reports/barmex_requisition_template.xml',
        'reports/barmex_transfer_template.xml',
        'reports/barmex_delivery_templates.xml',
        'reports/barmex_inventory_template.xml',
        'reports/report.xml'


    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
