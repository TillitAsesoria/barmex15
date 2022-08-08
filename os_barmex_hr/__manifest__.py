{
    'name': 'OS Barmex HR',
    'version': '15.0',
    'author': 'OS Barmex HR',
    'website': '',
    'category': 'hr',
    'sequence': 3,
    'licence': 'AGPL-3',
    'summary': 'OS Barmex HR',
    'depends': [
        'crm',
        'hr',
        'hr_expense',
        'os_barmex'
    ],
    'data': [
        'views/barmex_hr_employee.xml',
        'views/barmex_hr_expense.xml',
        'views/barmex_hr_job.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
