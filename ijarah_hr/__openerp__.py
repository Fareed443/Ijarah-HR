
{
    'name': 'Ijarah ',
    'version': '1.00',
    'author': 'Afras Trading & Corporating',
    'category': 'Category',
    'depends': 	['base','hr','account','product','account_accountant','hr_contract','hr_payroll','hr_payroll_account','base_iban',
'jasper_reports','portal_hr_employees','hr_holidays',],
    'demo': [],
    'description': """Ijarah HR Module
    """,
    'data': [		
             'Security/ijarah_security.xml',
             'Security/ir.ui.menu.csv',
             'Security/ir.model.access.csv',       
#	        'ijarah_hr_employee_inherit_view.xml', 
	        'ijarah_hr_contract_inherit_view.xml',
	        'ijarah_hr_payslip_inherit_view.xml',
       		'wizard/ijarah_send_mail_wiz_view.xml',		
	        'ijarah_hr_payslip_run_inherit_view.xml',
	        'ijarah_deduction_view.xml',
	        'ijarah_ot_view.xml',
		'ijarah_bonus_view.xml',
		'ijarah_loan_view.xml',
		'ijarah_equipment_view.xml',
		'ijarah_grades_view.xml',
		'ijarah_visa_type_view.xml',
		'ijarah_product_view.xml',
		'ijarah_my_view.xml',
		'ijarah_eos_view.xml',
		'ijarah_hr_leave_inherit_view.xml',
		'ijarah_sales_com_view.xml',
		'ijarah_training_expense_view.xml',
		'ijarah_resign_form_view.xml',	
		'sales_commission_batch_view.xml',
		'data/hr_contract_data.xml',
		'data/ijarah_hr_equip_data.xml',
		'data/ijarah_hr_emp_visa_data.xml',
		'data/ijarah_leave_type_data.xml',
#		'data/ijarah_grades_data.xml',
		'data/ijarah_payroll_structure_data.xml',		
		'hr_public_holidays_view.xml',	
		'hr_holidays_view.xml',	
		'reports.xml',	
		'ijarah_scheduler.xml',
		'import_ijarah_contract_view.xml',
		'ijarah_hr_emp_inherit_new_view.xml',
		'Security/ir_rule.xml',       
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}

