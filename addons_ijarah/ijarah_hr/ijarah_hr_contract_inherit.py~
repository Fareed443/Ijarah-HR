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
from openerp.tools.safe_eval import safe_eval as eval
import re

class hr_contract(osv.osv):
	"""Employee Contract """		
	def _salary_calculation(self, cr, uid, ids, name, args, context):
		res = {}
		for x in self.browse(cr, uid, ids, context=context):
			res[x.id] = {               
				'wage': 0.00,
			}
			val = val1 = val2 = val3= 0.00
			val2 += x.basic_salary + x.housing_allo + x.trans_allo
		res[x.id]['wage'] = val2 
		return res			
	'''
	def _check_unique_name(self, cr, uid, ids, context=None):
		check_ids = self.search(cr, 1 ,[], context=context)
		lst = [x.employee_name.lower() for x in self.browse(cr, uid, check_ids, context=context) if x.employee_name and x.id not in ids]
		for self_obj in self.browse(cr, uid, ids, context=context):
			if self_obj.employee_name and self_obj.employee_name.lower() in  lst:
				return False
		return True
	'''
	def _check_eng_name(self, cr, uid, ids, context=None):
		for employee in self.browse(cr, uid, ids, context=context):
			if employee.employee_name:
				if (re.match('^[\w -]+$', employee.employee_name) is None):
					return False
		return True

	def _check_arabic_name(self, cr, uid, ids, context=None):
		for employee in self.browse(cr, uid, ids, context=context):
			if employee.employee_arabic_name:
				if (re.match('^[\w -]+$', employee.employee_arabic_name) is not None):
					return False
		return True

	def _check_emp_no(self, cr, uid, ids, context=None):  # Only For OutSource Contract Type
		for x in self.browse(cr, uid, ids, context=context):
			if x.name:
				if (re.match('^[\w -]+$', x.name) is None):
					return False
		return True

	def _get_structure(self, cr, uid, context=None):
		type_ids = self.pool.get('hr.payroll.structure').search(cr, uid, [('code', '=', 'BS')])
		return type_ids and type_ids[0] or False



	def _get_type(self, cr, uid, context=None):
		type_ids = self.pool.get('hr.contract.type').search(cr, uid, [('name', 'in', ['Ijarah','OutSource'])])
		return type_ids or False


	def write(self, cr, uid, ids, vals, context=None):	
		title = vals.get('title')
		type_id = vals.get('type_id')
		name = vals.get('name')		
		year_diff = vals.get('year_diff')
		this = self.pool.get('ijarah.hr.grade').browse(cr,uid,title)
		current_id = self.browse(cr,uid, ids[0], context=None)
		hr_cont_type = self.pool.get('hr.contract.type').browse(cr,uid,type_id)				
		res={}
#		if vals.get('dept_id'):
#			vals['dept_id']	= current_id.dept_id
#			res.update({'dept_id':current_id.dept_id})
#			print current_id.dept_id.id		
			#cr.execute("""UPDATE hr_employee set department_id = %s WHERE cont_id = %s""",[current_id.dept_id.id,ids[0]])
	
		if vals.get('title'):
			vals['band'] = this.band
			vals['grade'] = this.grade
			vals['role'] = this.roles
			sal_range = "Between SAR"
			to = "to"			
			amount1 = str(this.amount1)
			amount2 = str(this.amount2)
			sal = sal_range+" "+amount1+" "+to+" "+amount2
			vals['sal_range']=sal			
			res.update({'band':this.band,'grade':this.grade,'role':this.roles,'sal_range':sal})
		if vals.get('type_id'):
			if hr_cont_type.name == 'Ijarah':
				now = datetime.datetime.now().strftime("%m")
				current_month = str(now)
				cm = str(current_month)
				result = {'name': {}}
				comp_life = str(current_id.year_diff)
				middle = cm
				cr.execute("""SELECT max(id) from hr_contract where type_id = (SELECT id from hr_contract_type where name = 'Ijarah')""")
				x = cr.fetchone()
				cr.execute("""SELECT name from hr_contract where id = %s """,x)
				max_seq = cr.fetchone()
			
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(comp_life))			
				#if max_seq:
				if max_seq == None :
						result = comp_life + cm + '01'			
				elif max_seq != None:
						seq = max_seq[0]
						year_index = str(seq[0:1])					
						month_index = str(seq[1:3])
						pad_index = str(seq[3:5])
						if month_index != middle:
							middle = cm
							pad = '01'
						else:						
							ps = pad_index[0]
							if ps == '0':
								pad = int(pad_index) + 1
								pad = '0'+ str(pad)
								pad_len = len(pad)
								pad_str = str(pad)
								if pad_len == 3:
									pad = pad_str
									pad = str(pad)
									pad = pad[1:3]
									pad = str(pad)	

							elif ps != '0':
								pad = int(pad_index) + 1
								pad = str(pad)
						result = comp_life + middle + pad				
						vals['name']= result							
						res.update({'name':result})
						cr.execute("""SELECT id from hr_employee WHERE is_ijarah=TRUE and cont_id = %s""",[ids[0]])
						iid = cr.fetchone()
						#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(iid))					
						if iid == None:
								return True
						if iid != None:						
							cr.execute("""UPDATE hr_employee set ijarah_emp_no = %s WHERE cont_id = %s""",[result,ids[0]])
			
			if hr_cont_type.name == 'OutSource':
					#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%())				
					result = vals['name']	
					vals['name']= result							
					res.update({'name':result})
					cr.execute("""SELECT id from hr_employee WHERE is_ijarah=TRUE and cont_id = %s""",[ids[0]])
					iid = cr.fetchone()
					#raise osv.except_osv(_('Configuration Error!'),_('The "%s" has t!')%(iid))					
					if iid == None:
							return True
					if iid != None:						
						cr.execute("""UPDATE hr_employee set ijarah_emp_no = %s WHERE cont_id = %s""",[result,ids[0]])

		result = super(hr_contract, self).write(cr, uid, ids, vals, context=context)	
		return result	

	
	def create(self, cr, user, vals,context=None):		
		title=vals['title']
		type_id = vals['type_id']
		year_diff = vals['year_diff']
		this = self.pool.get('ijarah.hr.grade').browse(cr,user,title)
		hr_cont_type = self.pool.get('hr.contract.type').browse(cr,user,type_id)
                vals['band'] = this.band
		vals['grade'] = this.grade
		vals['role']=this.roles
		sal_range = "Between SAR"
		to = "to"			
		amount1 = str(this.amount1)
		amount2 = str(this.amount2)
		sal = sal_range+" "+amount1+" "+to+" "+amount2
		vals['sal_range']=sal
		'''
		if hr_cont_type.name == 'Ijarah':
			now = datetime.datetime.now().strftime("%m")
			current_month = str(now)
			cm = str(current_month)
			result = {'name': {}}
			comp_life = str(year_diff)
			middle = cm
			cr.execute("""SELECT max(id) from hr_contract where type_id = (SELECT id from hr_contract_type where name = 'Ijarah')""")
			x = cr.fetchone()
			cr.execute("""SELECT name from hr_contract where id = %s """,x)
			max_seq = cr.fetchone()
			#if max_seq:
			if max_seq == None :
					result = comp_life + cm + '01'			
			elif max_seq != None:
					seq = max_seq[0]
					year_index = str(seq[0:1])					
					month_index = str(seq[1:3])
					pad_index = str(seq[3:5])
					if month_index != middle:
						middle = cm
						pad = '01'
					else:						
						ps = pad_index[0]
						if ps == '0':
							pad = int(pad_index) + 1
							pad = '0'+ str(pad)
							pad_len = len(pad)
							pad_str = str(pad)
							if pad_len == 3:
								pad = pad_str
								pad = str(pad)
								pad = pad[1:3]
								pad = str(pad)	

						elif ps != '0':
							pad = int(pad_index) + 1
							pad = str(pad)
					result = comp_life + middle + pad				
		if hr_cont_type.name == 'OutSource':
				result = vals['name']	
		vals['name']= result	
		'''
		return super(hr_contract,self).create(cr, user, vals, context)




	def _get_number_of_years(self, cd, ds):
        	"""Returns Difference of Years."""
        	
		DATETIME_FORMAT = "%Y-%m-%d"
		date_start = datetime.datetime.strptime(ds, DATETIME_FORMAT)
		current_date = datetime.datetime.strptime(cd, DATETIME_FORMAT)
		r = relativedelta.relativedelta(date_start, current_date)
		x = r.years
		return x
	
	_name = 'hr.contract'
	_inherit = 'hr.contract'
	_rec = 'employee_id'
	_description = 'Employee Contract Details'
	_columns = {
		'type_id': fields.many2one('hr.contract.type', "Contract", required=True,domain=[('name','in',['Ijarah','OutSource'])],),
		'contract_type': fields.many2one('hr.contract.type','Contract Type',required=True),
		'contract_detail': fields.many2one('hr.contract.type','Contract Detail',domain=[('name','=',['Test'])],),
		'contract_dur':fields.selection([('Annually', 'Annually'),('Bi-Annual', 'Bi-Annual')],'Contract Duration'),
		'title':fields.many2one("ijarah.hr.grade","Title"),
		'band':fields.char("Band"),	
		'grade':fields.char("Grades"),
		'role':fields.char("Roles"),
		'sal_range':fields.char("Salary Range"),
                'housing_allo':fields.float("Monthly Housing",size=64),
                'trans_allo':fields.float("Monthly Transportation",size=64),
                'bonus':fields.float("Bonus & Rewards",size=64),
               'gosi':fields.float("GOSI",size=64),
		'iqama':fields.float("Iqama Fees",size=64),
		'if_saudi':fields.boolean("Monthly Gosi & Sanid Included?"),	
		'basic_salary':fields.float("Basic Salary"),
		'employee_arabic_name':fields.char("Arabic Name",size=35),		
		'nationality': fields.many2one('res.country', 'Nationality'),
		'religion':fields.char("Religion"),
		'identification_no':fields.char("Identification Number"),
		'passport':fields.char("Passport No"),
		'dept_id':fields.many2one('hr.department', 'Department'),
		'gender': fields.selection([('male', 'Male'),('female', 'Female')],'Gender',required=True),
		'marital': fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status'),
		'birthday':fields.date("Date of Birth"),
		'qualification':fields.char("Qualification"),
		'degree':fields.char("Degree"),
		'exp':fields.char("Experience"),
        	'company_id': fields.many2one('res.company', 'Company',readonly=True),
		'employee_name':fields.char("Employee Name",required=True,size=35),
		'wage': fields.function(_salary_calculation,method=True,string='Total Salary',multi='sums',store=True,type='float'),
		'state': fields.selection([('Draft', 'Draft'),('Confirm', 'Confirm')],'Status'),
		'name': fields.char('Contract Reference', size=64, required=True),
		'employee_id': fields.many2one('hr.employee', "Employee", required=False),
		'employee_contract_type': fields.selection([('Family', 'Family'),('Single', 'Single')],'Employment Contract'),
		'employee_ticket': fields.selection([('Economic', 'Economic'),('Business', 'Business')],'Air Ticket'),
		'ticket_qty':fields.selection([('Annually', 'Annually'),('Per Contract', 'Per Contract')],'Quantity'),
		'exit_qty':fields.selection([('Annually', 'Annually'),('Per Contract', 'Per Contract')],'Exit Entry Visa Qty'),
		'ds':fields.date("Start Date"),
		'cd':fields.date("Current Date"),
		'year_diff':fields.char('No of Years'),
		'type_id_char':fields.char("Type Name"),
		'eos_per_month':fields.float("Monthly End of Service"),
		'sanid':fields.float("Sanid"),
        }
	_defaults = {
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.contract', context=c),
		'state'  : lambda * a :'Draft',
		'type_id': None,
		'ds':'2012-01-01',
		'cd':lambda *a: time.strftime('%Y-%m-%d'),
		'struct_id':_get_structure,
		'gosi':0.00,
		'sanid':0.00,
#		'basic_salary':0.00,
		'eos_per_month':0.00,
		'housing_allo':0.00,				
	}
	_sql_constraints = [
        	('empname_unique', 'unique(name)', 'Employee Number must be unique!'),
    ]
	_constraints = [(_check_eng_name, 'Error: Please Enter Valid Name', ['employee_name']),   # For English Name Validation
			(_check_arabic_name, 'Error: Please Enter Valid Arabic Name', ['employee_arabic_name']),
			(_check_emp_no, 'Error: Please Enter Valid Employee No', ['name']),] # For Employee Number Alphanumeric Character	
		# Customize Function

	def onchange_dob(self, cr, uid,ids,birthday,context=None):
		value = {}
		now = datetime.datetime.now().strftime("%Y-%m-%d")
		if birthday >= now:
			return { 'Warning':{'title':'warning','message':'Date Should not be  future and today Date'},'value' :{'birthday': ''}}	          
		else :
			return True

	def unlink(self, cr, uid, ids, context=None):
		contract_id = self.pool.get('hr.contract').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in contract_id:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Contract(s) which are already Confirmed state !'))
		#osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		#return True
		return super(hr_contract, self).unlink(cr, uid, ids, context=context)		
				
	def onchange_title(self,cr,uid,ids,title,context=None):					
		value = {}
		this = self.pool.get('ijarah.hr.grade').browse(cr, uid,title,context=context)
		sal_range = "Between SAR"
		to = "to"			
		amount1 = str(this.amount1)
		amount2 = str(this.amount2)
		if title:	
			value ={'band':this.band,'grade':this.grade,'role':this.roles,'sal_range':sal_range+" "+amount1+" "+to+" "+amount2} 
			return {'value': value}                
		return True

	def onchange_year(self,cr,uid,ids,cd,ds,context=None):
		now = datetime.datetime.now()		
		result = {'value': {}}
		diff_year = self._get_number_of_years(ds, cd)
		result['value']['year_diff'] = round(math.floor(diff_year))
		return result
#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%())

	def onchange_basic(self, cr, uid,ids,sal_range,title,basic_salary,context=None):
		value = {}
		this = self.pool.get('ijarah.hr.grade').browse(cr, uid,title,context=context)		
		amount1 = this.amount1
		amount2 = this.amount2
		if not title:
			return { 'warning':{'title':'warning','message':'Please Enter the Title and Salary Range for this Employee'},'value' :{'basic_salary':0.00}}
			
		if basic_salary: 	
			if basic_salary >= amount1 and basic_salary <= amount2:
				return {'value' :{'eos_per_month':(basic_salary * 0.5) / 12,'housing_allo':(basic_salary * 0.25)}}		
			else:
				return { 'Warning':{'title':'warning','message':'Salary Should not be greater than or less than the given range'},'value' :{'basic_salary': '','eos_per_month':'','housing_allo':''}}	                  		                  		
		else:
			return False
		
	def onchange_type_id(self,cr,uid,ids,type_id,year_diff,context=None):	
		this = self.pool.get('hr.contract.type').browse(cr, uid,type_id,context=context)		
		res = {'value':{},'domain':{},'warning':'Warning Message'}
		if not type_id:
			return	{'value':{'type_id_char':None,'contract_type':[]},'domain':{'contract_type':[('name','=','Test')]}}
		if this.name == 'Ijarah':
			now = datetime.datetime.now().strftime("%m")
			current_month = str(now)
			cm = str(current_month)
			result = {'name': {}}
			comp_life = str(year_diff)
			middle = cm
			cr.execute("""SELECT max(id) from hr_contract where type_id = (SELECT id from hr_contract_type where name = 'Ijarah')""")
			x = cr.fetchone()
			cr.execute("""SELECT name from hr_contract where id = %s """,x)
			max_seq = cr.fetchone()
			#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(comp_life))
			if max_seq == None :
				result = comp_life + cm + '01'			
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(result))

			elif max_seq!= None:
					seq = max_seq[0]
					year_index = str(seq[0:1])					
					month_index = str(seq[1:3])
					pad_index = str(seq[3:5])
					if month_index != middle:
						middle = cm
						pad = '01'
					else:						
						ps = pad_index[0]
						if ps == '0':
							pad = int(pad_index) + 1
							pad = '0'+ str(pad)
							pad_len = len(pad)
							pad_str = str(pad)
							if pad_len == 3:
								pad = pad_str
								pad = str(pad)
								pad = pad[1:3]
								pad = str(pad)	

						elif ps != '0':
							pad = int(pad_index) + 1
							pad = str(pad)
					result = comp_life + middle + pad		
			return	{'value':{'type_id_char':this.name,'name':result,'contract_type':[]},'domain':{'contract_type':[('name','in',['Saudi','Expat'])]}}

		if this.name == 'OutSource':
			return	{'value':{'type_id_char':this.name,'name':None,'contract_type':[]},'domain':{'contract_type':[('name','in',['STO','Afras','Excellent Solution'])]}}
		return True

	def onchange_contract_type(self,cr,uid,ids,contract_type,context=None):					
		this = self.pool.get('hr.contract.type').browse(cr, uid,contract_type,context=context)		
		res = {'value':{},'domain':{},'warning':'Warning Message'}
		value = {}
		if not contract_type:
			return	{'value':{'contract_detail':[]},'domain':{'contract_detail':[('name','=','Test')]}}
		if this.name == 'Saudi':
			return	{'value':{'contract_detail':[]},'domain':{'contract_detail':[('name','in',['Normal','HRDF'])]}}
		if this.name == 'Expat':
			return	{'value':{'contract_detail':[]},'domain':{'contract_detail':[('name','in',['Professional','Labor','Custom'])]}}
		return True

	def onchange_gosi(self, cr, uid,ids,if_saudi,basic_salary,housing_allo,nationality,context=None):
		value = {}
		this = self.pool.get('res.country').browse(cr, uid,nationality,context=context)		
		if not nationality and if_saudi == True:
			return { 'warning':{'title':'warning','message':'Please Enter the Nationality'},'value' :{'if_saudi':False,'gosi':0.00,'sanid':0.00}}	
		if if_saudi == True and this.name == 'Saudi Arabia':	
			value = {'gosi': (basic_salary + housing_allo) * 0.09,'sanid':(basic_salary + housing_allo) /100}
		if if_saudi == True and this.name != 'Saudi Arabia':
			return { 'warning':{'title':'warning','message':'Gosi & Sanid deduction are only for Saudi Nationality'},'value' :{'gosi':0.00,'if_saudi':False,'sanid':0.00}}	
		elif if_saudi == False:
			value = {'gosi': 0.00 ,'sanid':0.00}
		return {'value': value}
			
	def validate_state(self, cr, uid,ids,context=None):
		my_object = self.pool.get('hr.employee')
		this = self.browse(cr,uid, ids[0], context=None)
		current_id = str(this.id)
		current_emp_no = this.name
#		ids = obj.search(cr, uid, [])
	#	res = obj.read(cr, uid, ids, ['name', 'id'], context)
	#	res = [(r['id'], r['name']) for r in res]		
		#search_id = my_object.search(cr,uid,[('cont_id', '!=', None),('is_ijarah', '=',True)])
#		res = my_object.read(cr, uid, search_id,['ijarah_emp_no'],context)
		#res1 = my_object.read(cr, uid, search_id,['cont_id'],context)		
		#res1 = [(r['cont_id']) for r in res1]		
		cr.execute("""SELECT cont_id from hr_employee WHERE cont_id is not NULL and is_ijarah=TRUE""")
		x = cr.fetchall()
		x1 = ', '.join([str(i[0]) for i in x])		
#		x = cr.fetchone()
	#	res = [(r['cont_id']) for r in res ]
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(x))			
		##print res
		if current_id in x1:
			#raise osv.except_osv(_('Configuration Error!'),_('"%s" Mogood')%(x1))						
			self.write(cr, uid, ids, {'state':'Confirm'}, context=context)
			return True

		if current_id not in x1:
			#raise osv.except_osv(_('Configuration Error!'),_(' Muafi mogood "%s" ')%(x1))			
			my_object.create(cr, uid, { 
				'name':	this.employee_name,
				'arabic_name' :this.employee_arabic_name ,
				'ijarah_emp_no':this.name,
				'department_id':this.dept_id.id,
				'job_id':this.job_id.id,
				'country_id' : this.nationality.id,
				'religion':this.religion,
				'identification_id':this.identification_no,
				'passport_id':this.passport,
				'marital':this.marital,
				'gender':this.gender,
				'birthday':this.birthday,
				'qualification':this.qualification,
				'deg':this.degree,
				'experience':this.exp,
				'structure_id':this.struct_id.id,
				'cont_id':ids[0],	
				'company_id':this.company_id.id,
				'is_ijarah':True
			})
			cr.execute("""SELECT id from hr_employee where name_related = %s""",([this.employee_name]))
			x = cr.fetchone()[0]		
			self.write(cr, uid, ids, {'state':'Confirm','employee_id':x}, context=context)
		return True
	

	def roll_back(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'Draft'}, context=context)
		return True


hr_contract()


class hr_contract_type(osv.osv):

	def name_get(self, cr, uid, ids, context=None):
		if isinstance(ids, (list, tuple)) and not len(ids):
			return []
		if isinstance(ids, (long, int)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
		res = []
		for record in reads:
			name = record['name']
			if record['parent_id']:
#				name = record['parent_id'][1]+' / '+name
				name = name  # Customize By Fareed

			res.append((record['id'], name))
		return res

	def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
		res = self.name_get(cr, uid, ids, context=context)
		return dict(res)

	_name = 'hr.contract.type'
	_inherit= 'hr.contract.type'
	_description = 'Contract Type'
	_columns = {
		'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
		'parent_id': fields.many2one('hr.contract.type','Parent Category', select=True, ondelete='cascade'),
		'child_id': fields.one2many('hr.contract.type', 'parent_id', string='Child Categories'),
		'parent_left': fields.integer('Left Parent', select=1),
		'parent_right': fields.integer('Right Parent', select=1),
		'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of product categories."),
    }
	_defaults = {}
	_parent_name = "parent_id"
	_parent_store = True
	_parent_order = 'sequence, name'
	_order = 'parent_left'
	
	def _check_recursion(self, cr, uid, ids, context=None):
		level = 100
		while len(ids):
			cr.execute('select distinct parent_id from hr_contract_type where id IN %s',(tuple(ids),))
			ids = filter(None, map(lambda x:x[0], cr.fetchall()))
			if not level:
				return False
			level -= 1
		return True

	_constraints = [
		(_check_recursion, 'Error ! You cannot create recursive contracts.', ['parent_id'])
		]

	def child_get(self, cr, uid, ids):
		return [ids]

hr_contract_type()

