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


class ijarah_hr_emp_eos(osv.osv):

	def _check_eos_type(self, cr, uid, ids, context=None):
		for x in self.read(cr, uid, ids, ['eos_type', 'gender'], context=context):
		        if x['eos_type'] == 'Marriage' and  x['gender'] == 'male':
		            return False
		        if x['eos_type'] == 'Child Birth' and  x['gender'] == 'male':
		            return False
			return True

	def _check_eos_type_date(self, cr, uid, ids, context=None):
		for x in self.read(cr, uid, ids, ['eos_type', 'marriage_date','eos_date','child_birth_date','force_maj_date'], context=context):
		        if x['eos_type'] == 'Marriage' and  x['marriage_date'] >= x['eos_date']:
		            return False
		        if x['eos_type'] == 'Child Birth' and  x['child_birth_date'] >= x['eos_date']:
		            return False
		        if x['eos_type'] == 'Force Majeure' and  x['force_maj_date'] >= x['eos_date']:
		            return False
			return True


	########################### FOR Read Only No of Years ##########################
	def _check_all(self, cr, uid, ids, name, args, context):
		res = {}			
		for x in self.browse(cr, uid, ids, context=context):
			res[x.id] = {               
#				'noy':0.00 ,
				'amount':0.00,
				'service_period':'',
			}
#		res[x.id]['noy'] = self.onchange_dates(cr, uid,ids,context)
		res[x.id]['amount'] = self.onchange_amount_readonly(cr, uid,ids,context)
		res[x.id]['service_period'] = self.onchange_service_period(cr, uid,ids,context)

		return res			
	################################################################################

	def _get_number_of_years(self, date_start,eos_date):
        	"""Returns Difference of Years."""
        	
		DATETIME_FORMAT = "%Y-%m-%d"
		date_start = datetime.datetime.strptime(date_start, DATETIME_FORMAT)
		eos_date = datetime.datetime.strptime(eos_date, DATETIME_FORMAT)
		r = relativedelta.relativedelta(eos_date,date_start)
		x = r.years
		return x

	def _get_service_period(self, date_start,eos_date):
        	"""Returns Difference of Service Period."""
        	
		DATETIME_FORMAT = "%Y-%m-%d"
		date_start = datetime.datetime.strptime(date_start, DATETIME_FORMAT)
		eos_date = datetime.datetime.strptime(eos_date, DATETIME_FORMAT)
		r = relativedelta.relativedelta(eos_date,date_start)
		duration = "{0.years} years, {0.months} months and {0.days} days".format(r)
		return duration

	def _get_marriage_period(self, marriage_date,eos_date):
        	"""Returns Difference of Marriage Date And End of Service Date"""
		DATETIME_FORMAT = "%Y-%m-%d"
#		md = datetime.datetime.strptime(marriage_date, DATETIME_FORMAT)  #Marriage Date
#		ed = datetime.datetime.strptime(eos_date, DATETIME_FORMAT) 	# EOS Date
#		diff_month = (12*ed.year + ed.month) - (12*md.year + md.month)	
#		return diff_month
		md = datetime.datetime.strptime(marriage_date, DATETIME_FORMAT)  #Force Majeure Date
		ed = datetime.datetime.strptime(eos_date, DATETIME_FORMAT) 	# EOS Date
		timedelta = ed - md
		diff_day = timedelta.days + float(timedelta.seconds) / 86400
		return diff_day

	def _get_child_period(self, child_birth_date,eos_date):
        	"""Returns Difference of Child Birth Date and End of Service Period."""
		DATETIME_FORMAT = "%Y-%m-%d"
#		cbd = datetime.datetime.strptime(child_birth_date, DATETIME_FORMAT)  #Child Birth Date
#		ed = datetime.datetime.strptime(eos_date, DATETIME_FORMAT) 	# EOS Date
#		diff_month = (12*ed.year + ed.month) - (12*cbd.year + cbd.month)	
#		return diff_month
		cbd = datetime.datetime.strptime(child_birth_date, DATETIME_FORMAT)  #Force Majeure Date
		ed = datetime.datetime.strptime(eos_date, DATETIME_FORMAT) 	# EOS Date
		timedelta = ed - cbd
		diff_day = timedelta.days + float(timedelta.seconds) / 86400
		return diff_day

	def _get_force_period(self, force_maj_date,eos_date):
        	"""Returns Difference of Service Period."""
		DATETIME_FORMAT = "%Y-%m-%d"
		fd = datetime.datetime.strptime(force_maj_date, DATETIME_FORMAT)  #Force Majeure Date
		ed = datetime.datetime.strptime(eos_date, DATETIME_FORMAT) 	# EOS Date
		timedelta = ed - fd
		diff_day = timedelta.days + float(timedelta.seconds) / 86400
		return diff_day

	def create(self, cr, uid, vals,context=None):		
		name = vals['name']
		eos_type = vals['eos_type']
		nom = vals['no_of_month']
		nod = vals['no_of_days']
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
		remain_leave = this.remaining_leaves
		sal = this.contract_id.wage
		sal = sal / 30.0
		leave_amount = float(remain_leave * sal)		
                vals['salary'] = this.contract_id.wage # name.dbfieldname			
                vals['emp_name'] = this.name_related # name.dbfieldname			
                vals['job_id'] = this.job_id.id # name.dbfieldname
		vals['gender'] = this.contract_id.gender
		vals['housing_allo'] = this.contract_id.housing_allo
		vals['basic'] = this.contract_id.basic_salary				
		vals['trans_allo'] = this.contract_id.trans_allo
		vals['date_start'] = this.contract_id.date_start
		vals['remain_leave']=this.remaining_leaves
		vals['leave_amount']=leave_amount
		return super(ijarah_hr_emp_eos,self).create(cr, uid, vals, context)
			
	def write(self, cr, uid, ids, vals, context=None):						
		this = self.browse(cr,uid, ids[0], context=None)
		name = vals.get('name')
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
		res={}					
		if vals.get('name'):
			vals['salary'] = this.contract_id.basic_salary # name.dbfieldname			
			vals['emp_name'] = this.name_related # name.dbfieldname			
			vals['job_id'] = this.job_id.id # name.dbfieldname
			vals['gender'] = this.contract_id.gender
			vals['housing_allo'] = this.contract_id.housing_allo
			vals['basic'] = this.contract_id.basic_salary				
			vals['trans_allo'] = this.contract_id.trans_allo
			vals['date_start'] = this.contract_id.date_start
			vals['remain_leave']=this.remaining_leaves
			vals['leave_amount']=leave_amount
			vals['amount'] = self.onchange_amount_readonly(cr, uid,ids,context)						
			res.update({'salary': this.contract_id.basic_salary , 'emp_name':this.name_related,'job_id':this.job_id.id,
			'gender':this.contract_id.gender,'housing_allo':this.contract_id.housing_allo,'basic':this.contract_id.basic_salary,
			'trans_allo':this.contract_id.trans_allo,'date_start':this.contract_id.date_start
			,'amount':self.onchange_amount_readonly(cr, uid,ids,context)})		
		result = super(ijarah_hr_emp_eos, self).write(cr, uid, ids, vals, context=context)	
		return result
		
	_name = "ijarah.hr.emp.eos"
	_columns = {
		'name'	: fields.many2one("hr.employee","Employee No",required=True,domain="[('activate','=',True)]",states={'Confirmed':[('readonly',True)],'Paid':[('readonly',True)]}),
		'emp_name':fields.char("Employee Name",readonly=True,states={'Confirmed':[('readonly',True)],'Paid':[('readonly',True)]}),
		'job_id':fields.many2one("hr.job","Job Title",readonly=True,states={'Confirmed':[('readonly',True)]}),
		'salary':fields.float("Gross Salary",readonly=True,states={'Confirmed':[('readonly',True)]}),
		'eos_type':fields.selection([('Resigned', 'Resigned'),('End of Contract', 'End of Contract'),('Dismissal', 'Termination'),('Retirement or Death', 'Retirement or Death'),('Force Majeure', 'Force Majeure'),('Marriage', 'Marriage'),('Child Birth', 'Child Birth')],'EOS Type',required=True,states={'Confirmed':[('readonly',True)],'Paid':[('readonly',True)]}),
		'note':fields.text("Note",states={'Confirmed':[('readonly',True)],'Paid':[('readonly',True)]}),
		'state': fields.selection([('Draft', 'Draft'),('Confirmed', 'Confirmed'),('Paid', 'Paid'),],'Status',  readonly=True,),
		'y_m_d':fields.char("Total Days",readonly=True),
#		'noy':fields.float("No of Years",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'basic':fields.float("Basic Salary",readonly=True),
		'housing_allo':fields.float("Hosuing Allowance",readonly=True),
		'trans_allo':fields.float("Transportation Allowance",readonly=True),
#		'amount':fields.float("EOS Amount",readonly=True),
		'date_start':fields.date("Contract Start Date",readonly=True),
		'eos_date':fields.date("End Of Service Date",required=True,states={'Confirmed':[('readonly',True)],'Paid':[('readonly',True)]}),
		'remain_leave':fields.float("Remaining Leave",readonly=True),
		'leave_amount':fields.float("Leave Amount",readonly=True),
		'gender': fields.selection([('male', 'Male'),('female', 'Female')],'Gender',readonly=True,),
#		'noy':fields.function(_check_all,method=True,string='No of Years',store=True,multi='sums',type='float'),
		'noy':fields.float('No of Years'),
		'amount':fields.function(_check_all,method=True,string='Amounts',store=True,multi='sums',type='float'),
#		'amount':fields.float('Amount',readonly=True),
		'service_period':fields.function(_check_all,method=True,string='Service Period',store=True,multi='sums',type='char'),
		'marriage_date':fields.date("Marriage Date",states={'Confirmed':[('readonly',True)],'Paid':[('readonly',True)]}),
		'child_birth_date':fields.date("Child Birth Date",states={'Confirmed':[('readonly',True)],'Paid':[('readonly',True)]}),
		'no_of_month':fields.float("No of Months",states={'Confirmed':[('readonly',True)],'Paid':[('readonly',True)]}), #Only for Child Birth and Marriage Fields
		'force_maj_date':fields.date("Incident Date",states={'Confirmed':[('readonly',True)],'Paid':[('readonly',True)]}),
		'no_of_days':fields.float("No of Days",states={'Confirmed':[('readonly',True)],'Paid':[('readonly',True)]}), #Only for Force Majeure 
	}
	_constraints = [
		(_check_eos_type, 'Error! Only Female Employee avail this Eos Type', ['eos_type', 'gender']),
		(_check_eos_type_date, 'Error! Please Enter Valid Date.', ['eos_type', 'eos_date','marriage_date','force_maj_date','child_birth_date'])]
	
	_defaults = {			
		'state'  : lambda * a :'Draft',
#		'eos_date':lambda *a: time.strftime('%Y-%m-%d')
	}

	
	def unlink(self, cr, uid, ids, context=None):
		bonus = self.pool.get('ijarah.hr.emp.eos').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in bonus:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Bonus which are already Opened or Done state !'))
#		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
#		return True
		return super(ijarah_hr_emp_eos, self).unlink(cr, uid, ids, context=context)        

	def onchange_eos_type(self,cr,uid,ids,name,eos_type,context=None):					
		res = {'value':{},'domain':{},'warning':'Warning Message'}
		value = {}
		if eos_type:
			return	{'value':{'eos_date':'','noy':0.0,'amount':0.00,'no_of_month':0.00,'service_period':'','no_of_days':0.00,}}
		return True


	def onchange_date(self, cr, uid,ids,date_start,eos_date,marriage_date,child_birth_date,force_maj_date,context=None):
		result = {'value': {}}
		if marriage_date:
			if (eos_date and marriage_date) and (eos_date > marriage_date):
				diff_month = self._get_marriage_period(marriage_date, eos_date)
				result['value']['no_of_month'] = int(diff_month)
				result['value']['no_of_days'] = 0
				result['value']['noy'] = 0
			if eos_date <= marriage_date:
				return { 'warning':{'title':'warning','message':'End date should not be less than or equal to Marriage Date'},'value' :{'eos_date':'','noy':0,'service_period':'','no_of_month':0,'amount':0.00}}


#		if not marriage_date:
#			else:
#				result['value']['no_of_month'] = 0.0
		if child_birth_date:			
			if (eos_date and child_birth_date) and (eos_date > child_birth_date):
				diff_month = self._get_child_period(child_birth_date, eos_date)
				result['value']['no_of_month'] = int(diff_month)
				result['value']['no_of_days'] = 0
				result['value']['noy'] = 0

			if eos_date <= child_birth_date:
				return { 'warning':{'title':'warning','message':'End date should not be less than or equal to Child Birth Date'},'value' :{'eos_date':'','noy':0,'service_period':'','no_of_month':0,'amount':0.00}}

#			else:
#				result['value']['no_of_month'] = 0.0			
		if force_maj_date:
			if (eos_date and force_maj_date) and (eos_date > force_maj_date):
				diff_month = self._get_force_period(force_maj_date, eos_date)
				result['value']['no_of_days'] = int(diff_month)
				result['value']['noy'] = 0
				result['value']['no_of_month'] = 0

			if eos_date <= force_maj_date:
				return { 'warning':{'title':'warning','message':'End date should not be less than or equal to Incident Date'},'value' :{'eos_date':'','noy':0,'service_period':'','no_of_days':0,'amount':0.00}}

		if not eos_date:
				return	{'value':{'eos_date':'','noy':0,'no_of_month':0,'no_of_days':0}}
		
		if eos_date < date_start:
			return { 'warning':{'title':'warning','message':'End date should not be less than contract Date'},'value' :{'eos_date':'','noy':0}}
		if (date_start and eos_date) and (date_start <= eos_date):
			service_date = self._get_service_period(date_start, eos_date)
			diff_day = self._get_number_of_years(date_start, eos_date)
			result['value']['noy'] = round(math.floor(diff_day))
			result['value']['service_period'] = service_date
		else:
			result['value']['noy'] = 0
			result['value']['no_of_days'] = 0
			result['value']['no_of_month'] = 0

		return result

	def onchange_nom(self, cr, uid,ids,no_of_month,eos_type,salary,gender,context=None):
		nom = int(no_of_month)
#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(nom))
	 	if eos_type == 'Marriage' and gender == 'female':
			if nom >=1 and nom < 180:
				if nom >=1 and nom < 180:
					return { 'warning':{'title':'warning','message':'Employee is not entitled of End of Service Amount'},'value' :{'no_of_month':0,'eos_date':'','amount':0.00,'service_period':''}}
				return {'value': {}}	
			if nom >= 6:
				amount = (salary)				
				value ={'amount':amount}
				return {'value': value}	
	 	if eos_type == 'Child Birth' and gender == 'female':
			if nom >=1 and nom < 90 :
				if nom >=1 and nom < 90:
					return { 'warning':{'title':'warning','message':'Employee is not entitled of End of Service Amount'},'value' :{'no_of_month':0,'eos_date':'','amount':0.00,'service_period':''}}
				return {'value': {}}	
			if nom >= 90:
				amount = (salary) 
				value ={'amount':amount}
				return {'value': value}

		return True						

	def onchange_nod(self, cr, uid,ids,no_of_days,eos_type,salary,gender,context=None):
		nod = int(no_of_days)
#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(nom))
	 	if eos_type == 'Force Majeure':
			if nod <= 0:
				return { 'warning':{'title':'warning','message':'Employee is not entitled of End of Service Amount'},'value' :{'no_of_days':0,'eos_date':'','amount':0.00,'service_period':''}}
			if nod > 0:
				amount = (salary)				
				value ={'amount':amount}
				return {'value': value}								         		    	
		return True


	def onchange_empno(self, cr, uid,ids,name,context=None):
		if context is None:
			context = {}
		if not name:
			return	{'value':{'salary':0.00,'emp_name':False,'job_id':[],'basic':False,'housing_allo':0.00,'gender':False,'child_birth_date':'',
				'trans_allo':0.00,'date_start':'','remain_leave':0.00,'leave_amount':0.00,'noy':0.00,'eos_date':'','marriage_date':'',
				'no_of_month':0.00}}
		if name:		 
			this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
			contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
			remain_leave = this.remaining_leaves
			sal = this.contract_id.wage
			sal = sal / 30.0
			leave_amount = float(remain_leave * sal)
			value ={'salary':this.contract_id.wage,'emp_name':this.name_related,'job_id':this.job_id.id,
				'basic':this.contract_id.basic_salary,'housing_allo':this.contract_id.housing_allo,
				'trans_allo':this.contract_id.trans_allo,'date_start':this.contract_id.date_start,
				'remain_leave':this.remaining_leaves,'leave_amount':leave_amount,'gender':this.contract_id.gender,
				'eos_date':'','noy':0,'no_of_month':0,'no_of_days':0,
				'service_period':'',
				}
			return {'value': value}
		return True

	def onchange_noy(self, cr, uid,ids,noy,eos_type,salary,gender,context=None):
		noy = int(noy)

	 	if eos_type == 'Resigned':
			if noy < 2 :
				if noy < 2 :
					return { 'warning':{'title':'warning','message':'Employee(REs) is not entitled of End of Service Amount'},'value' :{'noy':'','service_period':'',}}
				return {'value': {}}	
			if noy >= 2 and noy < 5:
				amount = (salary * noy) * (1.0/3.0)
				value ={'amount':amount}
				return {'value': value}						

			if noy >= 5 and noy < 10:
				amount = (salary * noy) * (2.0/3.0)
				value ={'amount':amount}
				return {'value': value}						

			if noy >= 10:
				amount = (salary * noy)
				value ={'amount':amount}
				return {'value': value}
	 	if eos_type == 'End of Contract' or eos_type == 'Dismissal' or eos_type == 'Retirement or Death':
			if noy < 5:
				amount = (salary * noy) * (1.0/2.0)
				#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(amount))
				value ={'amount':amount}
				return {'value': value}						

			if noy >= 5:
				amount = (salary * noy)
				value ={'amount':amount}
				return {'value': value}	

		return True				
	
	def onchange_marriage_date(self, cr, uid,ids,marriage_date,date_start,gender,context=None):
		if gender == 'female':
			if marriage_date:
				if marriage_date < date_start:
					return { 'warning':{'title':'warning','message':'Marriage Date Should be greater than the Contract Start Date'},'value' :{'marriage_date':'','eos_date':'','service_period':''}}

			else:
				return	True

		if gender != 'female':
			return { 'warning':{'title':'warning','message':'Only Female Employees avail this End of Service '},'value' :{'marriage_date':'','eos_date':'','service_period':''}}


		return True

	def onchange_child_date(self, cr, uid,ids,child_birth_date,date_start,gender,context=None):
		if gender == 'female':
			if child_birth_date:
				if child_birth_date < date_start:
					return { 'warning':{'title':'warning','message':'Child Birth Date Should be greater than the Contract Start Date'},'value' :{'child_birth_date':'','eos_date':'','service_period':''}}
			else:
				return True

		if gender != 'female':
			return { 'warning':{'title':'warning','message':'Only Female Employees avail this End of Service '},'value' :{'child_birth_date':'','eos_date':'','service_period':''}}
		
		return True

	def onchange_force_date(self, cr, uid,ids,force_maj_date,date_start,context=None):
		if force_maj_date:
				if force_maj_date < date_start:
					return { 'warning':{'title':'warning','message':'Date Should be greater than the Contract Start Date'},'value' :{'force_maj_date':'','eos_date':''}}
				if force_maj_date < date_start:
					return True
		return True		

	def validate_state(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'Confirmed'}, context=context)
		return True

################################################################FOR Read only No of Years #######################################################	
	def onchange_dates(self, cr, uid,ids,context=None):
		this = self.browse(cr,uid, ids[0], context=None)		
		date_start = this.date_start
		eos_date = this.eos_date		
		if (date_start and eos_date) and (date_start <= eos_date):
			service_date = self._get_service_period(date_start, eos_date)
			diff_day = self._get_number_of_years(date_start, eos_date)
			result = round(math.floor(diff_day))
#			result = service_date	
		else:
			result = 0
		return result
####################################################################FOR  Readonly##########################################################
	def onchange_service_period(self, cr, uid,ids,context=None):
		this = self.browse(cr,uid, ids[0], context=None)		
		date_start = this.date_start
		eos_date = this.eos_date		
		if (date_start and eos_date) and (date_start <= eos_date):
			service_date = self._get_service_period(date_start, eos_date)
			result = service_date
		else:
			result = 0
		return result
			
	def onchange_amount_readonly(self, cr, uid,ids,context=None):
		this = self.browse(cr,uid, ids[0], context=None)
#		noy = self.onchange_dates(cr,uid,ids,context)
		nom = int(this.no_of_month)
		nod = int(this.no_of_days)
		noy = int(this.noy)	
		salary = this.salary
		gender = this.gender
		eos_type = this.eos_type
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(noy))
	 	if eos_type == 'Resigned':
			if noy < 2 :
				amount = 0.00
				return amount
			if noy >= 2 and noy < 5:
				amount = (salary * noy) * (1.0/3.0)
				return amount
			if noy >= 5 and noy < 10:
				amount = (salary * noy) * (2.0/3.0)
				return amount
			if noy >= 10:
				amount = (salary * noy)
				return amount
	 	if eos_type == 'End of Contract' or eos_type == 'Dismissal' or eos_type == 'Retirement or Death':
			if noy < 5:
				amount = (salary * noy) * (1.0/2.0)
				return amount	
			if noy >= 5:
				amount = (salary * noy)
				return amount
	 	if eos_type == 'Force Majeure':
			if nod <= 0:
				amount = 0.00				
				#value ={'amount':amount}
				return amount								         		    	
				
			if nod > 0:
				amount = (salary)				
				return amount							         		    	
			
	 	if eos_type == 'Marriage' and gender == 'female':
			if nom >=1 and nom < 180:
				if nom >=1 and nom < 180:
					amount=0.00
					return amount
			if nom >= 180:
				amount = (salary)				
				return amount
	 	if eos_type == 'Child Birth' and gender == 'female':
			if nom >=1 and nom < 90 :
				if nom >=1 and nom < 90:
					amount = 0.00
					return amount
			if nom >= 90:
				amount = (salary) 
				return amount
		
#		return True 



#################################################################################################################################################
ijarah_hr_emp_eos()
