from openerp.osv import osv, fields
from datetime import datetime,time
from openerp.addons import jasper_reports
from lxml import etree    
import datetime
import time
import math
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from datetime import timedelta
from dateutil import relativedelta
from datetime import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

class ijarah_hr_emp_ot(osv.osv):

	def create(self, cr, uid, vals,context=None):		
		name = vals['name']
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
                vals['salary'] = this.contract_id.basic_salary # name.dbfieldname			
                vals['emp_name'] = this.name_related # name.dbfieldname			
                vals['job_id'] = this.job_id.id # name.dbfieldname			
#		vals['assign_name']= str(prod.designation.name)		
		return super(ijarah_hr_emp_ot,self).create(cr, uid, vals, context)
	
	def write(self, cr, uid, ids, vals, context=None):						
		name = vals.get('name')
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
		res={}	
		if vals.get('name'):
			vals['salary'] = this.contract_id.basic_salary # name.dbfieldname			
			vals['emp_name'] = this.name_related # name.dbfieldname			
			vals['job_id'] = this.job_id.id # name.dbfieldname			
			res.update({'salary': this.contract_id.basic_salary , 'emp_name':this.name_related,			
				             'job_id':this.job_id.id ,# name.dbfieldname			
					})		

		result = super(ijarah_hr_emp_ot, self).write(cr, uid, ids, vals, context=context)	
		return result

	def _get_number_of_days(self, date_from, date_to):
	
		DATETIME_FORMAT = "%Y-%m-%d"		
		from_dt = datetime.strptime(date_from, DATETIME_FORMAT)
		to_dt = datetime.strptime(date_to, DATETIME_FORMAT)
		timedelta = to_dt - from_dt
		diff_day = timedelta.days + float(timedelta.seconds) / 86400
		return diff_day		

	_name = "ijarah.hr.emp.ot"
	_columns = {
		'name'	: fields.many2one("hr.employee","Employee No",required=True,domain="[('activate','=',True)]",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'emp_name':fields.char("Employee Name",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'job_id':fields.many2one("hr.job","Job Title",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'salary':fields.float("Salary",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'note':fields.text("Note",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'date_from':fields.date("Date From",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'date_to':fields.date("Date To",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'ot_amount':fields.float('OverTime Amount',states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'state': fields.selection([('Draft', 'Draft'),('Open', 'Open'),('Done', 'Done')],'Status',  readonly=True,),
		'ot_rule':fields.selection([('Hours', 'Hours'),('Amount', 'Amount')],'OT Type'),
		'no_of_hours':fields.integer("No of Hours",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'fixed_amount':fields.float("Fixed Amount",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'hours_rules':fields.selection([('1', '1'),('2', '1.5')],'Hourly Rules',states={'Open':[('readonly',True)],'Done':[('readonly',True)]},readonly="True"),
		'hourly_charge':fields.float("Hourly Charge",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'paid':fields.boolean("Paid",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
	}
	_defaults = {			
		'state'  : lambda * a :'Draft',
        	'date_from': lambda *a: time.strftime('%Y-%m-01'),
		'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
		'paid':False,
		'hours_rules':	lambda * a :'2',
	}
	'''
	def unlink(self, cr, uid, ids, context=None):
		ot = self.pool.get('ijarah.hr.emp.ot').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in ot:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Deduction(s) which are already Opened or Done state !'))
		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		return True
        '''
    		
	def validate_state(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'Open'}, context=context)
		return True
		         		    	
	def onchange_empno(self, cr, uid,ids,name,date_from,date_to,context=None):
		if name:		 
			this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
			contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
			diff_day = self._get_number_of_days(date_from, date_to)
			value ={'salary':this.contract_id.basic_salary,'emp_name':this.name_related,'job_id':this.job_id.id}
			return {'value': value}

	def onchange_ot_rule(self, cr, uid,ids,ot_rule,context=None):
		if ot_rule == 'Amount':	
			return	{'value':{'ot_amount':0.00,'hourly_charge':0.00,'no_of_hours':0,'hours_rules':None}}
		if ot_rule == 'Hours':
			return	{'value':{'ot_amount':0.00,'hourly_charge':0.00,'no_of_hours':0,'hours_rules':'2'}}
		return True

	def onchange_hours_rules(self, cr, uid,ids,no_of_hours,hours_rules,context=None):
		if no_of_hours:	
			noh = no_of_hours 
			hr = hours_rules
			if hours_rules == '1':			
				value ={'hourly_charge': noh * 1}
			elif hours_rules == '2':
				value ={'hourly_charge': noh * 1.5 }
			return {'value': value}
		return True
	def onchange_hourly_charge(self, cr, uid,ids,salary,hourly_charge,context=None):
		if hourly_charge:	
			hc = hourly_charge
 			sal = salary
			calc1 = (sal / 30.00 / 8.00 )
			value ={'ot_amount': hc * calc1}
			return {'value': value}
		return True
ijarah_hr_emp_ot()
