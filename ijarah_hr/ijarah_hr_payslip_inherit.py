from openerp.osv import osv, fields
from datetime import datetime,time
from datetime import datetime
from dateutil import relativedelta
from lxml import etree    
import datetime
import time
import math
from openerp.tools.translate import _
from datetime import date, timedelta
from datetime import date
from openerp import netsvc
from openerp import tools
import openerp.addons.decimal_precision as dp
import time
from datetime import date
from datetime import datetime
from openerp.tools.safe_eval import safe_eval as eval


class hr_payslip(osv.osv):
	"""Employee Payslip """		
	
	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):

			self.fetch_loan(cr,uid,ids,context)	# Calling fetch_loan Button function !!!!!!!!!!!!!!!!!!!!!                            
			self.fetch_deduct_amount(cr,uid,ids,context)
			self.fetch_ot_amount(cr,uid,ids,context)
			self.fetch_bonus_amount(cr,uid,ids,context)
			self.fetch_eos_amount(cr,uid,ids,context)
			self.fetch_train_amount(cr,uid,ids,context)
			self.fetch_asset_deduct_amount(cr,uid,ids,context)
			self.fetch_leave_unpaid_amount(cr,uid,ids,context)
			self.fetch_leave_unapprove_amount(cr,uid,ids,context)

			res = {}
			
			for order in self.browse(cr, uid, ids, context=context):
				res[order.id] = {               
				    'gross_amount': 0.00,
				    'net_amount':0.00,
				   
				}
				val = val1 = val2 = val3 = val4= 0.00
				
			return res		
			
	_name = 'hr.payslip'
	_inherit = 'hr.payslip'
	_description = 'Employee Payslip'
	_columns = {
#				'cost_center': fields.many2one('account.analytic.account', 'Cost Center'),
				'leave_unpaid_amount': fields.function(_amount_all,method=True,string='Leave Deduction Amount',multi='sums',store=True,type='float'),
				'leave_unapprove_amount': fields.function(_amount_all,method=True,string='Leave Deduction UnApprove Amount',multi='sums',store=True,type='float'),

				'asset_deduct_amount': fields.function(_amount_all,method=True,string='Asset Dedcution Amount',multi='sums',store=True,type='float'),
				'eos_amount': fields.function(_amount_all,method=True,string='EOS Amount',multi='sums',store=True,type='float'),
				'train_amount': fields.function(_amount_all,method=True,string='Training Amount',multi='sums',store=True,type='float'),
				'bonus_amount': fields.function(_amount_all,method=True,string='Bonus Amount',multi='sums',store=True,type='float'),
				'loan_amount': fields.function(_amount_all,method=True,string='Loan Amount',multi='sums',store=True,type='float'),
				'deduct_amount': fields.function(_amount_all,method=True,string='Deduct Amount',multi='sums',store=True,type='float'),
				'ot_amount': fields.function(_amount_all,method=True,string='OT Amount',multi='sums',store=True,type='float'),
				'credit_pay':fields.many2one("account.account","Credit Account"),
				'gross_amount': fields.function(_amount_all,method=True,string='Gross Amount',multi='sums',store=True,type='float'),
				'net_amount': fields.function(_amount_all,method=True,string='Net Amount',multi='sums',store=True,type='float'),
				'employee_name':fields.char("Employee Name"),
				'contract_structure':fields.char("Contract Type"),
								  
	}
	_defaults = {
			'leave_unpaid_amount':0.00,	
			'leave_unapprove_amount':0.00,	
			'asset_deduct_amount':0.00,	
			'eos_amount':0.00,	
			'train_amount':0.00,	
			'bonus_amount':0.00,	
			'loan_amount':0.00,	
			'deduct_amount':0.00,
			'ot_amount':0.00,	

	}
	def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):
		def _sum_salary_rule_category(localdict, category, amount):
		    if category.parent_id:
		        localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
		    localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
		    return localdict

		class BrowsableObject(object):
		    def __init__(self, pool, cr, uid, employee_id, dict):
		        self.pool = pool
		        self.cr = cr
		        self.uid = uid
		        self.employee_id = employee_id
		        self.dict = dict

		    def __getattr__(self, attr):
		        return attr in self.dict and self.dict.__getitem__(attr) or 0.0

		class InputLine(BrowsableObject):
		    """a class that will be used into the python code, mainly for usability purposes"""
		    def sum(self, code, from_date, to_date=None):
		        if to_date is None:
		            to_date = datetime.now().strftime('%Y-%m-%d')
		        result = 0.0
		        self.cr.execute("SELECT sum(amount) as sum\
		                    FROM hr_payslip as hp, hr_payslip_input as pi \
		                    WHERE hp.employee_id = %s AND hp.state = 'done' \
		                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
		                   (self.employee_id, from_date, to_date, code))
		        res = self.cr.fetchone()[0]
		        return res or 0.0

		class WorkedDays(BrowsableObject):
		    """a class that will be used into the python code, mainly for usability purposes"""
		    def _sum(self, code, from_date, to_date=None):
		        if to_date is None:
		            to_date = datetime.now().strftime('%Y-%m-%d')
		        result = 0.0
		        self.cr.execute("SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours\
		                    FROM hr_payslip as hp, hr_payslip_worked_days as pi \
		                    WHERE hp.employee_id = %s AND hp.state = 'done'\
		                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
		                   (self.employee_id, from_date, to_date, code))
		        return self.cr.fetchone()

		    def sum(self, code, from_date, to_date=None):
		        res = self._sum(code, from_date, to_date)
		        return res and res[0] or 0.0

		    def sum_hours(self, code, from_date, to_date=None):
		        res = self._sum(code, from_date, to_date)
		        return res and res[1] or 0.0

		class Payslips(BrowsableObject):
		    """a class that will be used into the python code, mainly for usability purposes"""

		    def sum(self, code, from_date, to_date=None):
		        if to_date is None:
		            to_date = datetime.now().strftime('%Y-%m-%d')
		        self.cr.execute("SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
		                    FROM hr_payslip as hp, hr_payslip_line as pl \
		                    WHERE hp.employee_id = %s AND hp.state = 'done' \
		                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s",
		                    (self.employee_id, from_date, to_date, code))
		        res = self.cr.fetchone()
		        return res and res[0] or 0.0

		#we keep a dict with the result because a value can be overwritten by another rule with the same code
		result_dict = {}
		rules = {}
		categories_dict = {}
		blacklist = []
		payslip_obj = self.pool.get('hr.payslip')
		inputs_obj = self.pool.get('hr.payslip.worked_days')
		obj_rule = self.pool.get('hr.salary.rule')
		payslip = payslip_obj.browse(cr, uid, payslip_id, context=context)
		worked_days = {}
		for worked_days_line in payslip.worked_days_line_ids:
		    worked_days[worked_days_line.code] = worked_days_line
		inputs = {}
		for input_line in payslip.input_line_ids:
		    inputs[input_line.code] = input_line

		categories_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, categories_dict)
		input_obj = InputLine(self.pool, cr, uid, payslip.employee_id.id, inputs)
		worked_days_obj = WorkedDays(self.pool, cr, uid, payslip.employee_id.id, worked_days)
		payslip_obj = Payslips(self.pool, cr, uid, payslip.employee_id.id, payslip)
		rules_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, rules)

		localdict = {'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj, 'worked_days': worked_days_obj, 'inputs': input_obj}
		#get the ids of the structures on the contracts and their parent id as well
		structure_ids = self.pool.get('hr.contract').get_all_structures(cr, uid, contract_ids, context=context)
		#get the rules of the structure and thier children
		rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
		#run the rules by sequence
		sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]

		for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
		    employee = contract.employee_id
		    localdict.update({'employee': employee, 'contract': contract})
		    for rule in obj_rule.browse(cr, uid, sorted_rule_ids, context=context):
		        key = rule.code + '-' + str(contract.id)
		        localdict['result'] = None
		        localdict['result_qty'] = 1.0
		        #check if the rule can be applied
		        if obj_rule.satisfy_condition(cr, uid, rule.id, localdict, context=context) and rule.id not in blacklist:
		            #compute the amount of the rule
		            amount, qty, rate = obj_rule.compute_rule(cr, uid, rule.id, localdict, context=context)
		            #check if there is already a rule computed with that code
		            previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
		            #set/overwrite the amount computed for this rule in the localdict
		            if amount > 0.00:    ############# Fareed Customize ############################################
		                tot_rule = amount * qty * rate / 100.0
		                localdict[rule.code] = tot_rule
		                rules[rule.code] = rule
		                #sum the amount for its salary category
		                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
		                #create/overwrite the rule in the temporary results
		                result_dict[key] = {
		                    'salary_rule_id': rule.id,
		                    'contract_id': contract.id,
		                    'name': rule.name,
		                    'code': rule.code,
		                    'category_id': rule.category_id.id,
		                    'sequence': rule.sequence,
		                    'appears_on_payslip': rule.appears_on_payslip,
		                    'condition_select': rule.condition_select,
		                    'condition_python': rule.condition_python,
		                    'condition_range': rule.condition_range,
		                    'condition_range_min': rule.condition_range_min,
		                    'condition_range_max': rule.condition_range_max,
		                    'amount_select': rule.amount_select,
		                    'amount_fix': rule.amount_fix,
		                    'amount_python_compute': rule.amount_python_compute,
		                    'amount_percentage': rule.amount_percentage,
		                    'amount_percentage_base': rule.amount_percentage_base,
		                    'register_id': rule.register_id.id,
		                    'amount': amount,
		                    'employee_id': contract.employee_id.id,
		                    'quantity': qty,
		                    'rate': rate,
		                    'categ_name': rule.category_id.name,	 #### Custmoize By Fareed ##################				
		                }
		        else:
		                #blacklist this rule and its children
		                blacklist += [id for id, seq in self.pool.get('hr.salary.rule')._recursive_search_of_rules(cr, uid, [rule], context=context)]

		result = [value for code, value in result_dict.items()]
		return result
	
	def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
		empolyee_obj = self.pool.get('hr.employee')
		contract_obj = self.pool.get('hr.contract')
		worked_days_obj = self.pool.get('hr.payslip.worked_days')
		input_obj = self.pool.get('hr.payslip.input')

		if context is None:
			context = {}
		#delete old worked days lines
		old_worked_days_ids = ids and worked_days_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
		if old_worked_days_ids:
			worked_days_obj.unlink(cr, uid, old_worked_days_ids, context=context)

		#delete old input lines
		old_input_ids = ids and input_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
		if old_input_ids:
			input_obj.unlink(cr, uid, old_input_ids, context=context)


		#defaults
		res = {'value':{
					'line_ids':[],
					'input_line_ids': [],
					'worked_days_line_ids': [],
					#'details_by_salary_head':[], TODO put me back
					'name':'',
					'contract_id': False,
					'struct_id': False,
					'contract_structure':None
					}
			}
		if (not employee_id) or (not date_from) or (not date_to):
			return res
		ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
		employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
		res['value'].update({
				'name': _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
				'company_id': employee_id.company_id.id,
				'employee_name':employee_id.name_related,		# Customize
				'contract_id':employee_id.cont_id.id,
				'struct_id':employee_id.structure_id.id,
				'contract_structure':str(employee_id.cont_id.type_id.name)  + '/' + str(employee_id.cont_id.contract_type.name) + '/' +  							str(employee_id.cont_id.contract_detail.name)
						})
		'''
		if not context.get('contract', False):
		#fill with the first contract of the employee
			contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)
		else:
			if contract_id:
			#set the list of contract for which the input have to be filled
				contract_ids = [contract_id]
			else:
			#if we don't give the contract, then the input to fill should be for all current contracts of the employee
				contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)

		if not contract_ids:
			return res
		contract_record = contract_obj.browse(cr, uid, contract_ids[0], context=context)
		res['value'].update({
					'contract_id': employee_id.cont_id.id#contract_record and contract_record.id or False
		})
		struct_record = contract_record and contract_record.struct_id or False
		if not struct_record:
			return res
		res['value'].update({
					'struct_id': struct_record.id,
		})
		#computation of the salary input
		worked_days_line_ids = self.get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context=context)
		input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
		res['value'].update({
				'worked_days_line_ids': worked_days_line_ids,
				'input_line_ids': input_line_ids,
		})
		'''
		return res

######################################################## Leave Deduction Unapproved ##############################################################################
	def fetch_leave_unapprove_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee EOS Amount :
		cr.execute ("""SELECT hr_holidays.employee_id FROM hr_holidays
					WHERE hr_holidays.employee_id = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		cr.execute ("""SELECT SUM(hr_holidays.number_of_days_temp) AS TOTALDAYS
					FROM 
					hr_holidays,hr_holidays_status
					WHERE hr_holidays.employee_id = %s
					AND hr_holidays.state = 'validate'
					AND hr_holidays.paid = 'False'
					AND hr_holidays_status.id = hr_holidays.holiday_status_id
					AND hr_holidays_status.name='UnApproved'
					AND hr_holidays.date_from between %s AND %s """,(emp_id,this.date_from,this.date_to))
		x = cr.fetchone()
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
		if x : 
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
			if emp_id == None or x[0] == None :
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has figured the Debit Account!')%(x))
				return True
			
			elif emp_id == this.employee_id.id  or x[0] != None :
				#raise osv.except_osv(_('Configuration'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
				cr.execute("""UPDATE hr_payslip SET leave_unapprove_amount = %s WHERE hr_payslip.id = %s AND employee_id =%s """,(x,ids[0],emp_id))

######################################################## Leave Deduction Unpaid ##############################################################################
	def fetch_leave_unpaid_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee EOS Amount :
		cr.execute ("""SELECT hr_holidays.employee_id FROM hr_holidays
					WHERE hr_holidays.employee_id = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		cr.execute ("""SELECT SUM(hr_holidays.number_of_days_temp) AS TOTALDAYS
					FROM 
					hr_holidays,hr_holidays_status
					WHERE hr_holidays.employee_id = %s
					AND hr_holidays.state = 'validate'
					AND hr_holidays.paid = 'False'
					AND hr_holidays_status.id = hr_holidays.holiday_status_id
					AND hr_holidays_status.name='Unpaid'
					AND hr_holidays.date_from between %s AND %s """,(emp_id,this.date_from,this.date_to))
		x = cr.fetchone()
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
		if x : 
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
			if emp_id == None or x[0] == None :
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has figured the Debit Account!')%(x))
				return True
			
			elif emp_id == this.employee_id.id  or x[0] != None :
				#raise osv.except_osv(_('Configuration'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
				cr.execute("""UPDATE hr_payslip SET leave_unpaid_amount = %s WHERE hr_payslip.id = %s AND employee_id =%s """,(x,ids[0],emp_id))

######################################################## Assets Deduction Amount ###############################################################
	def fetch_asset_deduct_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee EOS Amount :
		cr.execute ("""SELECT ijarah_hr_emp_equip.name FROM ijarah_hr_emp_equip
					WHERE ijarah_hr_emp_equip.name = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		cr.execute ("""SELECT SUM(ijarah_hr_emp_equip.total_amount) AS TOTALAMOUNT
					FROM 
					ijarah_hr_emp_equip
					WHERE ijarah_hr_emp_equip.name = %s
					AND ijarah_hr_emp_equip.state = 'Received'
					AND ijarah_hr_emp_equip.paid = 'False'
					AND ijarah_hr_emp_equip.received_date between %s AND %s """,(emp_id,this.date_from,this.date_to))
		x = cr.fetchone()
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
		if x : 
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
			if emp_id == None or x[0] == None :
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has figured the Debit Account!')%(x))
				return True
			
			elif emp_id == this.employee_id.id  or x[0] != None :
				#raise osv.except_osv(_('Configuration'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
				cr.execute("""UPDATE hr_payslip SET asset_deduct_amount = %s WHERE hr_payslip.id = %s AND employee_id =%s """,(x,ids[0],emp_id))

####################################################################################################################################################3
######################################################## Training Expense Amount ###############################################################
	def fetch_train_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee EOS Amount :
		cr.execute ("""SELECT ijarah_hr_emp_train_exp.name FROM ijarah_hr_emp_train_exp
					WHERE ijarah_hr_emp_train_exp.name = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		cr.execute ("""SELECT SUM(ijarah_hr_emp_train_exp.amount) AS TOTALAMOUNT
					FROM 
					ijarah_hr_emp_train_exp
					WHERE ijarah_hr_emp_train_exp.name = %s
					AND ijarah_hr_emp_train_exp.state = 'Done'
					AND ijarah_hr_emp_train_exp.date_end between %s AND %s """,(emp_id,this.date_from,this.date_to))
		x = cr.fetchone()
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
		if x : 
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
			if emp_id == None or x[0] == None :
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has figured the Debit Account!')%(x))
				return True
			
			elif emp_id == this.employee_id.id  or x[0] != None :
				#raise osv.except_osv(_('Configuration'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
				cr.execute("""UPDATE hr_payslip SET train_amount = %s WHERE hr_payslip.id = %s AND employee_id =%s """,(x,ids[0],emp_id))


######################################################## End of Service Amount ###############################################################
	def fetch_eos_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee EOS Amount :
		cr.execute ("""SELECT ijarah_hr_emp_eos.name FROM ijarah_hr_emp_eos
					WHERE ijarah_hr_emp_eos.name = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		cr.execute ("""SELECT SUM(ijarah_hr_emp_eos.amount) AS TOTALAMOUNT
					FROM 
					ijarah_hr_emp_eos
					WHERE ijarah_hr_emp_eos.name = %s
					AND ijarah_hr_emp_eos.state = 'Confirmed'
					AND ijarah_hr_emp_eos.eos_date between %s AND %s """,(emp_id,this.date_from,this.date_to))
		x = cr.fetchone()
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
		if x : 
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
			if emp_id == None or x[0] == None :
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has figured the Debit Account!')%(x))
				return True
			
			elif emp_id == this.employee_id.id  or x[0] != None :
				#raise osv.except_osv(_('Configuration'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
				cr.execute("""UPDATE hr_payslip SET eos_amount = %s WHERE hr_payslip.id = %s AND employee_id =%s """,(x,ids[0],emp_id))

################################################################# Bonus Amount ####################################################################
	def fetch_bonus_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee Bonus Amount :
		cr.execute ("""SELECT ijarah_hr_emp_bonus.name FROM ijarah_hr_emp_bonus WHERE ijarah_hr_emp_bonus.name = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		cr.execute ("""SELECT SUM(ijarah_hr_emp_bonus_child.name) AS TOTALAMOUNT
					FROM 
					ijarah_hr_emp_bonus,ijarah_hr_emp_bonus_child
					WHERE ijarah_hr_emp_bonus.name = %s
					AND ijarah_hr_emp_bonus.state = 'Open'
					AND ijarah_hr_emp_bonus_child.status = 'True'
					AND ijarah_hr_emp_bonus_child.paid = 'False'
					AND ijarah_hr_emp_bonus.id = ijarah_hr_emp_bonus_child.bonus_ids
					AND ijarah_hr_emp_bonus_child.month between %s AND %s """,(emp_id,this.date_from,this.date_to))
		x = cr.fetchone()

		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s"  has not properly configured the Debit Account!')%(x))
		if x:
			if emp_id == None or x[0] == None :
				return True
			
			elif emp_id == this.employee_id.id  or x[0] != None:
#				raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s"  has not properly configured the Debit Account!')%(x))
				cr.execute("""UPDATE hr_payslip SET bonus_amount = %s WHERE hr_payslip.id = %s AND employee_id =%s """,(x,ids[0],emp_id))

################################################################# Overtime Amount ####################################################################
	def fetch_ot_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee Deduction Amount :
		cr.execute ("""SELECT ijarah_hr_emp_ot.name FROM ijarah_hr_emp_ot
					WHERE ijarah_hr_emp_ot.name = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		cr.execute ("""SELECT SUM(ijarah_hr_emp_ot.ot_amount) AS TOTALAMOUNT
					FROM 
					ijarah_hr_emp_ot
					WHERE ijarah_hr_emp_ot.name = %s
					AND ijarah_hr_emp_ot.state = 'Open'
					AND ijarah_hr_emp_ot.paid = 'False'
					AND ijarah_hr_emp_ot.date_from between %s AND %s """,(emp_id,this.date_from,this.date_to))
		x = cr.fetchone()
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
		if x : 
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
			if emp_id == None or x[0] == None :
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has figured the Debit Account!')%(x))
				return True
			
			elif emp_id == this.employee_id.id  or x[0] != None :
				#raise osv.except_osv(_('Configuration'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
				cr.execute("""UPDATE hr_payslip SET ot_amount = %s WHERE hr_payslip.id = %s AND employee_id =%s """,(x,ids[0],emp_id))

####################################################################### Deduction ######################################################################
	def fetch_deduct_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee Deduction Amount :
		cr.execute ("""SELECT ijarah_hr_emp_deduct.name FROM ijarah_hr_emp_deduct
					WHERE ijarah_hr_emp_deduct.name = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		cr.execute ("""SELECT SUM(ijarah_hr_emp_deduct.deduct_amount) AS TOTALAMOUNT
					FROM 
					ijarah_hr_emp_deduct
					WHERE ijarah_hr_emp_deduct.name = %s
					AND ijarah_hr_emp_deduct.state = 'Open'
					AND ijarah_hr_emp_deduct.paid = 'False'
					AND ijarah_hr_emp_deduct.for_month between %s AND %s """,(emp_id,this.date_from,this.date_to))
		x = cr.fetchone()
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
		if x : 
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
			if emp_id == None or x[0] == None :
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has figured the Debit Account!')%(x))
				return True
			
			elif emp_id == this.employee_id.id  or x[0] != None :
				#raise osv.except_osv(_('Configuration'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
				cr.execute("""UPDATE hr_payslip SET deduct_amount = %s WHERE hr_payslip.id = %s AND employee_id =%s """,(x,ids[0],emp_id))
			
##################################################################### LOAN Deduction ################################################################

	def fetch_loan(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None) 	
		# Check Employee Loan :
		cr.execute ("""SELECT ijarah_hr_emp_loan.name 
					FROM 
					ijarah_hr_emp_loan,ijarah_hr_emp_loan_child
					WHERE ijarah_hr_emp_loan.name = %s
					AND ijarah_hr_emp_loan.id =  ijarah_hr_emp_loan_child.loan_ids""",[this.employee_id.id])
		emp_id = cr.fetchone()			
		#Check Paid 
		cr.execute ("""SELECT SUM(ijarah_hr_emp_loan_child.name) AS TOTALAMOUNT
					FROM 
					ijarah_hr_emp_loan,ijarah_hr_emp_loan_child
					WHERE ijarah_hr_emp_loan.name = %s
					AND ijarah_hr_emp_loan.state = 'Open'
					AND ijarah_hr_emp_loan.deduct_type = 'Deductable'
					AND ijarah_hr_emp_loan_child.status = 'True'
					AND ijarah_hr_emp_loan_child.paid = 'False'
					AND ijarah_hr_emp_loan.id = ijarah_hr_emp_loan_child.loan_ids
					AND ijarah_hr_emp_loan_child.month between %s AND %s """,(emp_id,this.date_from,this.date_to))
		x = cr.fetchone()
		
		if x : 
			if emp_id == None or x[0] == None :
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has figured the Debit Account!')%(x))
				return True
			
			elif emp_id == this.employee_id.id  or x[0] != None :
				#raise osv.except_osv(_('Configuration'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
				cr.execute("""UPDATE hr_payslip SET loan_amount = %s WHERE hr_payslip.id = %s AND employee_id =%s """,(x,ids[0],emp_id))


########################################################## Loan Posting Function #######################################################
	def post_loan(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
		loan_amount = this.loan_amount
		if loan_amount:												
					cr.execute("""SELECT ijarah_hr_emp_loan_child.id 
								FROM
								ijarah_hr_emp_loan,ijarah_hr_emp_loan_child
								WHERE ijarah_hr_emp_loan.name = %s
								AND ijarah_hr_emp_loan.state = 'Open'
								AND ijarah_hr_emp_loan.deduct_type = 'Deductable'
								AND ijarah_hr_emp_loan_child.status = 'True'
								AND ijarah_hr_emp_loan_child.loan_ids = ijarah_hr_emp_loan.id
								AND ijarah_hr_emp_loan_child.paid = 'False'
								AND ijarah_hr_emp_loan_child.month between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))
#					x = cr.fetchall()
#					raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has figured the Debit Account!')%(x[1]))
					for m in cr.fetchall():
						cr.execute("""UPDATE ijarah_hr_emp_loan_child SET paid = True WHERE id = %s """,[m[0]])
										

						cr.execute ("""UPDATE ijarah_hr_emp_loan_child SET deduct = ijarah_hr_emp_loan_child.name
								WHERE id = %s """ , [m[0]])

				# Loan total installment update					
						cr.execute("""UPDATE ijarah_hr_emp_loan 
									SET total_install = 
									(SELECT SUM (ijarah_hr_emp_loan_child.deduct) 
									FROM ijarah_hr_emp_loan_child 
							        	Where loan_ids = ijarah_hr_emp_loan.id)""")
					
						cr.execute("""UPDATE ijarah_hr_emp_loan SET net_amount = (req_amount - total_install) 
									WHERE name = '%s' """,[this.employee_id.id] )									
					

		elif not loan_amount:
					return True		
################################################################ OT Posting ########################################################################
	def post_ot(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
		ot_amount = this.ot_amount
		if ot_amount:						
				####### Set Paid True ##########						
			cr.execute("""SELECT ijarah_hr_emp_ot.id 
					FROM
					ijarah_hr_emp_ot
					WHERE ijarah_hr_emp_ot.name = %s
					AND ijarah_hr_emp_ot.state = 'Open'
					AND ijarah_hr_emp_ot.paid = 'False'
					AND ijarah_hr_emp_ot.date_from between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))

			for m in cr.fetchall():
				cr.execute("""UPDATE ijarah_hr_emp_ot SET paid = True, state = 'Done' WHERE id = %s """,[m[0]])


		elif not ot_amount:
			return True		

####################################################################################################################################################
################################################################ Asset Deduction Posting ############################################################
	def post_asset_deduct_amount(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
		#for gp in self.browse(cr, uid, ids, context=context):
		#	for line in gp.line_ids:
		asset_deduct_amount = this.asset_deduct_amount
		if asset_deduct_amount:						
			cr.execute("""SELECT ijarah_hr_emp_equip.id 
					FROM
					ijarah_hr_emp_equip
					WHERE ijarah_hr_emp_equip.name = %s
					AND ijarah_hr_emp_equip.state = 'Received'
					AND ijarah_hr_emp_equip.paid = 'False'
					AND ijarah_hr_emp_equip.received_date between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))
			for m in cr.fetchall():
				cr.execute("""UPDATE ijarah_hr_emp_equip SET paid = 'True' WHERE id = %s """,[m[0]])

		elif not asset_deduct_amount:
			return True		

#############################################################################################################################################################
################################################################ Unapprove Leave Amount Posting ################################################################
	def post_leave_unapprove_amount(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
		leave_unapp_amount = this.leave_unapprove_amount
		if leave_unapp_amount:						
				####### Set Paid True ##########						
			cr.execute ("""SELECT hr_holidays.id
					FROM 
					hr_holidays,hr_holidays_status
					WHERE hr_holidays.employee_id = %s
					AND hr_holidays.state = 'validate'
					AND hr_holidays.paid = 'False'
					AND hr_holidays_status.id = hr_holidays.holiday_status_id
					AND hr_holidays_status.name='UnApproved'
					AND hr_holidays.date_from between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))

			for m in cr.fetchall():
				cr.execute("""UPDATE hr_holidays SET paid = True WHERE id = %s """,[m[0]])


		elif not leave_unapp_amount:
			return True		

####################################################################################################################################################

################################################################ Unpaid Leave Amount Posting ################################################################
	def post_leave_unpaid_amount(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
		leave_unpaid_amount = this.leave_unpaid_amount
		if leave_unpaid_amount:						
				####### Set Paid True ##########						
			cr.execute ("""SELECT hr_holidays.id
					FROM 
					hr_holidays,hr_holidays_status
					WHERE hr_holidays.employee_id = %s
					AND hr_holidays.state = 'validate'
					AND hr_holidays.paid = 'False'
					AND hr_holidays_status.id = hr_holidays.holiday_status_id
					AND hr_holidays_status.name='Unpaid'
					AND hr_holidays.date_from between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))

			for m in cr.fetchall():
				cr.execute("""UPDATE hr_holidays SET paid = True WHERE id = %s """,[m[0]])


		elif not leave_unpaid_amount:
			return True		

####################################################################################################################################################

################################################################ End of Service Posting ############################################################
	def post_eos(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
		#for gp in self.browse(cr, uid, ids, context=context):
		#	for line in gp.line_ids:
		eos_amount = this.eos_amount
		if eos_amount:						
			cr.execute("""SELECT ijarah_hr_emp_eos.id 
					FROM
					ijarah_hr_emp_eos
					WHERE ijarah_hr_emp_eos.name = %s
					AND ijarah_hr_emp_eos.state = 'Confirmed'
					AND ijarah_hr_emp_eos.eos_date between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))

			for m in cr.fetchall():
				cr.execute("""UPDATE ijarah_hr_emp_eos SET state = 'Paid' WHERE id = %s """,[m[0]])

		elif not eos_amount:
			return True		

#############################################################################################################################################################



################################################################ Deduction Posting ############################################################
	def post_deduct(self, cr, uid, ids, context=None):
				
		this = self.browse(cr,uid, ids[0], context=None)  
		#for gp in self.browse(cr, uid, ids, context=context):
		#	for line in gp.line_ids:
		deduct_amount = this.deduct_amount
		if deduct_amount:						
			cr.execute("""SELECT ijarah_hr_emp_deduct.id 
					FROM
					ijarah_hr_emp_deduct
					WHERE ijarah_hr_emp_deduct.name = %s
					AND ijarah_hr_emp_deduct.state = 'Open'
					AND ijarah_hr_emp_deduct.paid = 'False'
					AND ijarah_hr_emp_deduct.for_month between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))
#			x = cr.fetchall()
			for m in cr.fetchall():
			#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(m[0]))
				cr.execute("""UPDATE ijarah_hr_emp_deduct SET paid = True, state = 'Done' WHERE id = %s """,[m[0]])

		elif not deduct_amount:
			return True		

#############################################################################################################################################################
################################################################ Bonus Posting ##############################################################################
	def post_bonus(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
		bonus_amount = this.bonus_amount
		if bonus_amount:						
					####### Set Paid True ##########						
			cr.execute("""SELECT ijarah_hr_emp_bonus_child.id 
					FROM
					ijarah_hr_emp_bonus,ijarah_hr_emp_bonus_child
					WHERE ijarah_hr_emp_bonus.name = %s
					AND ijarah_hr_emp_bonus.state = 'Open'
					AND ijarah_hr_emp_bonus_child.status = 'True'
					AND ijarah_hr_emp_bonus_child.bonus_ids = ijarah_hr_emp_bonus.id
					AND ijarah_hr_emp_bonus_child.paid = 'False'
					AND ijarah_hr_emp_bonus_child.month between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))

			for m in cr.fetchall():
				cr.execute("""UPDATE ijarah_hr_emp_bonus_child SET paid = True WHERE id = %s """,[m[0]])


		elif not bonus_amount:
					return True		

#############################################################################################################################################################
	
	def compute_sheet(self, cr, uid, ids, context=None):
		slip_line_pool = self.pool.get('hr.payslip.line')
		sequence_obj = self.pool.get('ir.sequence')

		for payslip in self.browse(cr, uid, ids, context=context):
			number = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')
		#delete old payslip lines
			old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
		#            old_slipline_ids
			if old_slipline_ids:
				slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)
			
			if payslip.contract_id:
		#set the list of contrac#t for which the rules have to be applied
				contract_ids = [payslip.contract_id.id]
			else:
		#if we don't give the contract, then the rules to apply should be for all current contracts of the employee
				contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)
			lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
			#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(lines))	
			#for lines in payslip.line_ids:
			#if slip_line_pool.amount > 0.00:			
			self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number,}, context=context)
			#return True
		return True
	
	
	def process_sheet(self, cr, uid, ids, context=None):
		self.post_loan(cr, uid, ids, context)
		self.post_ot(cr,uid,ids,context)
		self.post_deduct(cr,uid,ids,context)
		self.post_bonus(cr,uid,ids,context)
		self.post_eos(cr,uid,ids,context)
		self.post_asset_deduct_amount(cr,uid,ids,context)
		self.post_leave_unpaid_amount(cr,uid,ids,context)
		self.post_leave_unapprove_amount(cr,uid,ids,context)
		return self.write(cr, uid, ids, {'paid': True, 'state': 'done'}, context=context)

hr_payslip()

class hr_payslip_line(osv.osv):
	
	def _amount_all(self, cr, uid, ids, name, args, context):
		res = {}
		for x in self.browse(cr, uid, ids, context=context):
			res[x.id] = {               
				'total_amount': 0.00,
			}
			val = val1= val2 = val3= 0.00
			val1 += x.amount
		res[x.id]['total_amount'] = val1 
		return res	

	_inherit = 'hr.payslip.line'
	_description = 'Payslip Line'
	_columns = {
			'total_amount':fields.function(_amount_all,method=True,string='Total Amount',multi='sums',store=True,type='float'),
			'categ_name':fields.char('Category Name'),

	}	
	_defaults = {
			'total_amount':0.00,	
	}
	_order = 'contract_id, sequence'

hr_payslip_line()

