# -*- coding: utf-8 -*-
{
    'name': "school_mgmt_extented",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'school_mgmt'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/employee_teacher.xml',
        # 'views/alumniextended.xml',

        'menu/menu.xml',
        
        'data/ask_vaccation_sequence.xml',
        'data/payment_sequence.xml',
        'data/allocation_mail.xml',
        
        'report/faculty_report.xml',
        'report/report.xml',
        'report/report_absence.xml',

        # plaquette

        'views/plaquette.xml',
        

         # Note et axame

        'views/notecontrole.xml',

        # emploi du temps

        'views/absence_view.xml',
        'views/timetable_view.xml',
        'views/timetable.xml',
        'views/examtime.xml',
        'views/herite.xml',
        'views/other_payment_type.xml',
        'views/payment_type_views.xml',
        'views/contract_views.xml',

        # allocation des enseignements
        'views/allocation_views.xml',
        'warning_report/report_contract.xml',
        'report/report_contract.xml',
        'report/report.xml',
        'views/warning.xml',
        'views/consolidation_views.xml',
        'views/desistement_views.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}