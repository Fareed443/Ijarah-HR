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

#			self.fetch_loan(cr,uid,ids,context)	# Calling fetch_loan Button function !!!!!!!!!!!!!!!!!!!!!                            
			self.fetch_deduct_amount(cr,uid,ids,context)
			self.fetch_ot_amount(cr,uid,ids,context)
			self.fetch_bonus_amount(cr,uid,ids,context)
#			self.fetch_gosi_amount(cr,uid,ids,context)
			res = {}
			for order in self.browse(cr, uid, ids, context=context):
				res[order.id] = {               
				    'gross_amount': 0.00,
				    'net_amount':0.00,
				   
				}
				val = val1 = val2 = val3 = val4= 0.00
				for line in order.line_ids:
				    val1 += line.amount + line.ot_amount
				    val2 += (line.deduct + line.other_deduct)
			
				res[order.id]['gross_amount'] = val1 
				res[order.id]['net_amount'] = 	val1 - val2
				
			return res		
	
	_name = 'hr.payslip'
	_inherit = 'hr.payslip'
	_description = 'Employee Payslip'
	_columns = {
#				'cost_center': fields.many2one('account.analytic.account', 'Cost Center'),
				'if_ot':fields.boolean('If OverTime'),
				'ot': fields.float('OT'),
				'bonus_amount': fields.function(_amount_all,method=True,string='Bonus Amount',multi='sums',store=True,type='float'),
				'credit_pay':fields.many2one("account.account","Credit Account",required=True),
				'gross_amount': fields.function(_amount_all,method=True,string='Gross Amount',multi='sums',store=True,type='float'),
				'net_amount': fields.function(_amount_all,method=True,string='Net Amount',multi='sums',store=True,type='float'),
				'employee_name':fields.char("Employee Name"),
								  
	}
	_defaults = {
			'ot': 0.00,
	}
	
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
					}
			}
		if (not employee_id) or (not date_from) or (not date_to):
			return res
		ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
		employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
		res['value'].update({
						'name': _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
						'company_id': employee_id.company_id.id,
#						'cost_center':employee_id.cost_center.id,		# Customize 
						'employee_name':employee_id.name_related,		# Customize
						})
		
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
					'contract_id': contract_record and contract_record.id or False
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
		return res
	
################################################################# GOSI DEDUCTION ####################################################################
	def fetch_gosi_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee Gosi Amount :
		cr.execute ("""SELECT employee_id FROM hr_contract
					WHERE employee_id = %s """,[this.employee_id.id])

		emp_id = cr.fetchone()			
#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(emp_id ))
		cr.execute ("""SELECT gosi FROM hr_contract WHERE employee_id = %s """,(emp_id))

		x = cr.fetchone()
		
					
		cr.execute("""UPDATE hr_payslip_line SET gosi_deduct =  (SELECT 
							hr_contract.gosi
							FROM hr_contract,hr_salary_rule,hr_payslip
							WHERE hr_contract.employee_id = %s
							AND hr_payslip.id  = hr_payslip_line.slip_id
							AND hr_payslip_line.salary_rule_id = hr_salary_rule.id 
							AND hr_salary_rule.name = 'Basic'
							AND hr_salary_rule.code = 'BASIC')
							WHERE hr_payslip_line.slip_id = %s  """,(this.employee_id.id,ids[0],))

	
################################################################# Bonus Amount ####################################################################
	def fetch_bonus_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee Bonus Amount :
		cr.execute ("""SELECT ijarah_hr_emp_bonus.name FROM ijarah_hr_emp_bonus
					WHERE ijarah_hr_emp_bonus.name = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		#Check Paid Condition
		cr.execute ("""SELECT ijarah_hr_emp_bonus_child.paid
					FROM 
					ijarah_hr_emp_bonus_child,ijarah_hr_emp_bonus
					WHERE ijarah_hr_emp_bonus.name = %s
					AND ijarah_hr_emp_bonus.state = 'Open'
					AND ijarah_hr_emp_bonus.id = ijarah_hr_emp_bonus_child.bonus_ids
					AND ijarah_hr_emp_bonus_child.month between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))
		z = cr.fetchone()
		#Check Status 
		cr.execute ("""SELECT ijarah_hr_emp_bonus_child.status
					FROM 
					ijarah_hr_emp_bonus_child,ijarah_hr_emp_bonus
					WHERE ijarah_hr_emp_bonus.name = %s
					AND ijarah_hr_emp_bonus.state = 'Open'
					AND ijarah_hr_emp_bonus.id = ijarah_hr_emp_bonus_child.bonus_ids
					AND ijarah_hr_emp_bonus_child.month between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))
		x = cr.fetchone()


#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s"  has not properly configured the Debit Account!')%(z))
		if x:
			if emp_id == None and z == False and x == False :
				return True
			
			elif emp_id == this.employee_id.id  or x[0] == True and z[0] == False :
				cr.execute("""SELECT ijarah_hr_emp_bonus_child.name
						FROM ijarah_hr_emp_bonus,ijarah_hr_emp_bonus_child,hr_payslip
						WHERE ijarah_hr_emp_bonus.name = %s
						AND ijarah_hr_emp_bonus_child.bonus_ids = ijarah_hr_emp_bonus.id
						AND ijarah_hr_emp_bonus_child.month between hr_payslip.date_from AND hr_payslip.date_to
						""",(this.employee_id.id,))

				x = cr.fetchone()			
#				raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s"  has not properly configured the Debit Account!')%(x))

				cr.execute("""UPDATE hr_payslip SET bonus_amount = %s WHERE hr_payslip.id = %s  """,(x,ids[0],))

		
			elif emp_id == this.employee_id.id or z[0] == False and x[0] == False:
				return True
			elif emp_id == this.employee_id.id or z[0] == True and x[0] == True:
				return True	

################################################################# Overtime Amount ####################################################################
	def fetch_ot_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee Deduction Amount :
		cr.execute ("""SELECT ijarah_hr_emp_ot.name FROM ijarah_hr_emp_ot
					WHERE ijarah_hr_emp_ot.name = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		cr.execute ("""SELECT ijarah_hr_emp_ot.paid
					FROM 
					ijarah_hr_emp_ot
					WHERE ijarah_hr_emp_ot.name = %s
					AND ijarah_hr_emp_ot.state = 'Open'	
					AND ijarah_hr_emp_ot.date_from between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))
		x = cr.fetchone()
#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" and %s has not properly configured the Debit Account!')%(emp_id , x))
		
		if x : 
			if emp_id == None and x == False :
				return True
			
			elif emp_id == this.employee_id.id  or x[0] == False :
				cr.execute("""UPDATE hr_payslip_line SET ot_amount =  (SELECT 
							ijarah_hr_emp_ot.ot_amount
							FROM ijarah_hr_emp_ot,hr_salary_rule,hr_payslip
							WHERE ijarah_hr_emp_ot.name = %s
							AND ijarah_hr_emp_ot.date_from between hr_payslip.date_from AND hr_payslip.date_to
							AND hr_payslip.id  = hr_payslip_line.slip_id
							AND hr_payslip_line.salary_rule_id = hr_salary_rule.id 
							AND hr_salary_rule.name = 'Basic'
							AND hr_salary_rule.code = 'BASIC')
							WHERE hr_payslip_line.slip_id = %s  """,(this.employee_id.id,ids[0],))

####################################################################### Deduction ######################################################################
	def fetch_deduct_amount(self, cr, uid, ids, context=None):								
		this = self.browse(cr,uid, ids[0], context=None)
		# Check Employee Deduction Amount :
		cr.execute ("""SELECT ijarah_hr_emp_deduct.name FROM ijarah_hr_emp_deduct
					WHERE ijarah_hr_emp_deduct.name = %s """,[this.employee_id.id])
		emp_id = cr.fetchone()			

		cr.execute ("""SELECT ijarah_hr_emp_deduct.paid
					FROM 
					ijarah_hr_emp_deduct
					WHERE ijarah_hr_emp_deduct.name = %s
					AND ijarah_hr_emp_deduct.state = 'Open'
					AND ijarah_hr_emp_deduct.for_month between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))
		x = cr.fetchone()
#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" and %s has not properly configured the Debit Account!')%(emp_id , x))
		
		if x : 
			if emp_id == None and x == False :
				return True
			
			elif emp_id == this.employee_id.id  or x[0] == False :
				cr.execute("""UPDATE hr_payslip_line SET other_deduct =  (SELECT 
							ijarah_hr_emp_deduct.deduct_amount
							FROM ijarah_hr_emp_deduct,hr_salary_rule,hr_payslip
							WHERE ijarah_hr_emp_deduct.name = %s
							AND ijarah_hr_emp_deduct.for_month between hr_payslip.date_from AND hr_payslip.date_to
							AND hr_payslip.id  = hr_payslip_line.slip_id
							AND hr_payslip_line.salary_rule_id = hr_salary_rule.id 
							AND hr_salary_rule.name = 'Basic'
							AND hr_salary_rule.code = 'BASIC')
							WHERE hr_payslip_line.slip_id = %s  """,(this.employee_id.id,ids[0],))
			
##################################################################### LOAN Deduction #######################################################################

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
		cr.execute ("""SELECT ijarah_hr_emp_loan_child.paid
					FROM 
					ijarah_hr_emp_loan,ijarah_hr_emp_loan_child
					WHERE ijarah_hr_emp_loan.name = %s
					AND ijarah_hr_emp_loan.state = 'Open'
					AND ijarah_hr_emp_loan.id = ijarah_hr_emp_loan_child.loan_ids
					AND ijarah_hr_emp_loan_child.month between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))
		x = cr.fetchone()

		#Check Status 
		cr.execute ("""SELECT ijarah_hr_emp_loan_child.status
					FROM 
					ijarah_hr_emp_loan_child,ijarah_hr_emp_loan
					WHERE ijarah_hr_emp_loan.name = %s
					AND ijarah_hr_emp_loan.state = 'Open'
					AND ijarah_hr_emp_loan.id = ijarah_hr_emp_loan_child.loan_ids
					AND ijarah_hr_emp_loan_child.month between %s AND %s """,(this.employee_id.id,this.date_from,this.date_to))
		z = cr.fetchone()

#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" and %s has not properly configured the Debit Account!')%(emp_id , x))
		
		if z : 
			if emp_id == None and x == False and z == False :
				return True
			
			elif emp_id == this.employee_id.id  or z[0] == True and x[0] == False :
				cr.execute("""UPDATE hr_payslip_line SET deduct =  (SELECT 
							ijarah_hr_emp_loan_child.name
							FROM ijarah_hr_emp_loan , ijarah_hr_emp_loan_child,hr_salary_rule,hr_payslip
							WHERE ijarah_hr_emp_loan.name = %s
							AND ijarah_hr_emp_loan_child.loan_ids = ijarah_hr_emp_loan.id
							AND ijarah_hr_emp_loan_child.month between hr_payslip.date_from AND hr_payslip.date_to
							AND hr_payslip.id  = hr_payslip_line.slip_id
							AND hr_payslip_line.salary_rule_id = hr_salary_rule.id 
							AND hr_salary_rule.name = 'Basic'
							AND hr_salary_rule.code = 'BASIC')
							WHERE hr_payslip_line.slip_id = %s  """,(this.employee_id.id,ids[0],))

			elif emp_id == this.employee_id.id or z[0] == False and x[0] == False:
				return True
			elif emp_id == this.employee_id.id or z[0] == True and x[0] == True:
				return True	


######################################################################## Loan Posting Function ###################################################################
	def post_loan(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
		for gp in self.browse(cr, uid, ids, context=context):
			for line in gp.line_ids:
				deduct_id = line.deduct
				if deduct_id:												
					cr.execute("""UPDATE ijarah_hr_emp_loan_child SET paid = True
								WHERE ijarah_hr_emp_loan_child.id = (SELECT ijarah_hr_emp_loan_child.id 
								FROM
								ijarah_hr_emp_loan,ijarah_hr_emp_loan_child
								WHERE ijarah_hr_emp_loan.name = %s
								AND ijarah_hr_emp_loan_child.loan_ids = ijarah_hr_emp_loan.id
								AND ijarah_hr_emp_loan_child.month between %s AND %s)""",(this.employee_id.id,this.date_from,this.date_to))

					cr.execute ("""UPDATE ijarah_hr_emp_loan_child SET deduct = ijarah_hr_emp_loan_child.name
								WHERE ijarah_hr_emp_loan_child.id = (
								SELECT 
								ijarah_hr_emp_loan_child.id
								FROM 
								ijarah_hr_emp_loan_child,
								ijarah_hr_emp_loan
								WHERE ijarah_hr_emp_loan.name = %s
								AND ijarah_hr_emp_loan_child.loan_ids = ijarah_hr_emp_loan.id 
								AND ijarah_hr_emp_loan_child.paid = TRUE 
								AND ijarah_hr_emp_loan_child.month between %s AND %s) """,(this.employee_id.id,this.date_from,this.date_to))

				# Loan total installment update					
					cr.execute("""UPDATE ijarah_hr_emp_loan 
									SET total_install = 
									(SELECT SUM (ijarah_hr_emp_loan_child.deduct) 
									FROM ijarah_hr_emp_loan_child 
							        	Where loan_ids = ijarah_hr_emp_loan.id)""")
					
					cr.execute("""UPDATE ijarah_hr_emp_loan SET net_amount = (req_amount - total_install) 
									WHERE name = '%s' """,[this.employee_id.id] )									


				elif not deduct_id:
					return True		
################################################################ OT Posting #################################################################################
	def post_ot(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
		for gp in self.browse(cr, uid, ids, context=context):
			for line in gp.line_ids:
				ot_id = line.ot_amount
				if ot_id:						
					####### Set Paid True ##########						
					cr.execute("""UPDATE ijarah_hr_emp_ot SET paid = True
								WHERE name = %s
								AND state = 'Open'								
								AND date_from between %s AND %s""",(this.employee_id.id,this.date_from,this.date_to))

				# State update to Done #####					
					cr.execute("""UPDATE ijarah_hr_emp_ot SET state = 'Done'
								WHERE name = %s
								AND state = 'Open'								
								AND date_from  between %s AND %s""",(this.employee_id.id,this.date_from,this.date_to))

				elif not ot_id:
					return True		

#############################################################################################################################################################
################################################################ Deduction Posting (other_deduct)############################################################
	def post_deduct(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
		for gp in self.browse(cr, uid, ids, context=context):
			for line in gp.line_ids:
				other_deduct = line.other_deduct
				if other_deduct:						
					####### Set Paid True ##########						
					cr.execute("""UPDATE ijarah_hr_emp_deduct SET paid = True
								WHERE name = %s
								AND state = 'Open'								
								AND for_month between %s AND %s""",(this.employee_id.id,this.date_from,this.date_to))

				# State update to Done #####					
					cr.execute("""UPDATE ijarah_hr_emp_deduct SET state = 'Done'
								WHERE name = %s
								AND state = 'Open'								
								AND for_month between %s AND %s""",(this.employee_id.id,this.date_from,this.date_to))

				elif not other_deduct:
					return True		

#############################################################################################################################################################
################################################################ Bonus Posting ##############################################################################
	def post_bonus(self, cr, uid, ids, context=None):		
		this = self.browse(cr,uid, ids[0], context=None)  
#		for gp in self.browse(cr, uid, ids, context=context):
#			for line in gp.line_ids:
		bonus_amount = this.bonus_amount
		if bonus_amount:						
					####### Set Paid True ##########						
			cr.execute("""UPDATE ijarah_hr_emp_bonus_child SET paid = True
								WHERE ijarah_hr_emp_bonus_child.id = (SELECT ijarah_hr_emp_bonus_child.id 
								FROM
								ijarah_hr_emp_bonus,ijarah_hr_emp_bonus_child
								WHERE ijarah_hr_emp_bonus.name = %s
								AND ijarah_hr_emp_bonus.state = 'Open'
								AND ijarah_hr_emp_bonus_child.bonus_ids = ijarah_hr_emp_bonus.id
								AND ijarah_hr_emp_bonus_child.month between %s AND %s)""",(this.employee_id.id,this.date_from,this.date_to))
				
				# State update to Done #####					
					#cr.execute("""UPDATE ijarah_hr_emp_bonus SET state = 'Done'
					#			WHERE name = %s
					#			AND state = 'Open'								
					#			AND date_from between %s AND %s""",(this.employee_id.id,this.date_from,this.date_to))

		elif not bonus_amount:
					return True		

#############################################################################################################################################################
	
	def compute_sheet(self, cr, uid, ids, context=None):
		slip_line_pool = self.pool.get('hr.payslip.line')
		sequence_obj = self.pool.get('ir.sequence')
		'''
		for gp in self.browse(cr, uid, ids, context=context):
			for line in gp.line_ids:
				val = val1 = val2 = val3 = val4 = 0.00
				val1 += line.ot_amount+line.amount
				val2 += ( line.deduct + line.other_deduct )
				val4 = float(line.quantity) * line.amount * line.rate / 100
				cr.execute("""UPDATE hr_payslip_line SET total_amount = %s WHERE hr_payslip_line.slip_id = %s """,(val4,ids[0],)) # Remove id.
				cr.execute("""UPDATE hr_payslip SET net_amount = 
						(SELECT SUM (hr_payslip_line.total_amount) 
						FROM hr_payslip_line
						WHERE hr_payslip.id = hr_payslip_line.slip_id)
						Where hr_payslip.id = '%s' """ ,(ids[0],))
						
				return True
		'''	
		for payslip in self.browse(cr, uid, ids, context=context):
			number = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')
		#delete old payslip lines
			old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
		#            old_slipline_ids
			if old_slipline_ids:
				slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)
			
			if payslip.contract_id:
		#set the list of contract for which the rules have to be applied
				contract_ids = [payslip.contract_id.id]
			else:
		#if we don't give the contract, then the rules to apply should be for all current contracts of the employee
				contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)
			lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
			self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number,}, context=context)

		return True
	
	def process_sheet(self, cr, uid, ids, context=None):
		self.post_loan(cr, uid, ids, context)
		self.post_ot(cr,uid,ids,context)
		self.post_deduct(cr,uid,ids,context)
		self.post_bonus(cr,uid,ids,context)
		move_pool = self.pool.get('account.move')
		period_pool = self.pool.get('account.period')
		timenow = time.strftime('%Y-%m-%d')
		for slip in self.browse(cr, uid, ids, context=context):			
			line_ids = []
			debit_sum = 0.0
			credit_sum = 0.0
			if not slip.period_id:
				search_periods = period_pool.find(cr, uid, slip.date_to, context=context)
				period_id = search_periods[0]
			else:
				period_id = slip.period_id.id
			default_partner_id = slip.employee_id.address_home_id.id
			name = _('Payslip of %s') % (slip.employee_id.name)
			move = {
			'narration': name,
			'date': timenow,
			'ref': slip.number,
			'journal_id': slip.journal_id.id,
			'period_id': period_id,
#			'cost_analytic_id':slip.cost_center.id,
			}
				
			if not slip.credit_pay:
				return True
			
			if slip.credit_pay:
				for line in slip.line_ids:
					net_amount_parent = slip.net_amount		    	   
					amt = slip.credit_note and -line.total_amount or line.total_amount
					debit_account_id = line.salary_rule_id.account_credit.id
					credit_account_parent = slip.credit_pay.id			
					if debit_account_id:
						debit_line = (0, 0, {
							'name': line.name,
				            'date': timenow,
				            'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_debit.type in ('receivable', 'payable')) and partner_id or False,
				            'account_id': debit_account_id,
				            'journal_id': slip.journal_id.id,
				            'period_id': period_id,
				            'debit': amt > 0.0 and amt or 0.0,
				            'credit': amt < 0.0 and -amt or 0.0,
				            'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
				            'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
				            'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
						})
						line_ids.append(debit_line)
						debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']		
					
				if credit_account_parent:		       
						credit_line = (0, 0, {
							'name': slip.credit_pay.name,
				            'date': timenow,
				            'partner_id': (line.salary_rule_id.register_id.partner_id or line.salary_rule_id.account_credit.type in ('receivable', 'payable')) and partner_id or False,
				            'account_id': credit_account_parent,
				            'journal_id': slip.journal_id.id,
				            'period_id': period_id,
				            'debit': net_amount_parent < 0.0 and -net_amount_parent or 0.0,
				            'credit': net_amount_parent > 0.0 and net_amount_parent or 0.0,
				            'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
				            'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
				            'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
						})
						line_ids.append(credit_line)
						credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']						
#										
										
				if debit_sum > credit_sum:
					acc_id = slip.journal_id.default_credit_pay.id
					if not acc_id:
						raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(slip.journal_id.name))
					adjust_credit = (0, 0, {
						'name': _('Adjustment Entry'),
						'date': timenow,
						'partner_id': False,
						'account_id': acc_id,
						'journal_id': slip.journal_id.id,
						'period_id': period_id,
						'debit': 0.0,
						'credit': debit_sum - credit_sum,})
					line_ids.append(adjust_credit)
									
				elif debit_sum < credit_sum:
					acc_id = slip.journal_id.default_debit_account_id.id
					if not acc_id:
						raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(slip.journal_id.name))
					adjust_debit = (0, 0, {
						'name': _('Adjustment Entry'),
						'date': timenow,
						'partner_id': False,
						'account_id': acc_id,
						'journal_id': slip.journal_id.id,
						'period_id': period_id,
						'debit': credit_sum - debit_sum,
						'credit': 0.0,
					})
					line_ids.append(adjust_debit)
			move.update({'line_id': line_ids})
			move_id = move_pool.create(cr, uid, move, context=context)
			self.write(cr, uid, [slip.id], {'move_id': move_id, 'period_id' : period_id}, context=context)
			if slip.journal_id.entry_posted:
					move_pool.post(cr, uid, [move_id], context=context)   # Function Posting
	#		return self.write(cr, uid, ids, {'paid': True, 'state': 'done'}, context=context)
		return super(hr_payslip, self).process_sheet(cr, uid, [slip.id], context=context)		
			############################################################################################################				
hr_payslip()

class hr_payslip_line(osv.osv):
	
	
	def _amount_all(self, cr, uid, ids, name, args, context):
		res = {}
		for x in self.browse(cr, uid, ids, context=context):
			res[x.id] = {               
				'total_amount': 0.00,
			}
			val = val1= val2 = val3= 0.00
			val1 += x.amount + x.ot_amount
			val2 += ( x.deduct + x.other_deduct )
#				    val2 += line.total_amount		
		res[x.id]['total_amount'] = val1 - val2
		return res			
	
	_inherit = 'hr.payslip.line'
	_description = 'Payslip Line'
	_columns = {
			'deduct': fields.float('Loan Deduction'),
			'ot_amount': fields.float('Overtime Amount'),
#			'total_amount': fields.float('Total Amount'),
			'total_amount':fields.function(_amount_all,method=True,string='Total Amount',multi='sums',store=True,type='float'),
#			'deduct':fields.function(_amount_all,method=True,string='Loan',multi='sums',store=True,type='float'),
			'other_deduct':fields.float('Deduction'),
			
	}	
	_defaults = {
			'deduct': 0.00,
			'total_amount':0.00,
			'other_deduct':0.00,
			
	}
	
	
                 
hr_payslip_line()

