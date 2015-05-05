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

class ijarah_hr_emp_deduct(osv.osv):

	def create(self, cr, uid, vals,context=None):		
		name = vals['name']
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
                vals['salary'] = this.contract_id.basic_salary # name.dbfieldname			
                vals['emp_name'] = this.name_related # name.dbfieldname			
                vals['job_id'] = this.job_id.id # name.dbfieldname			
#		vals['assign_name']= str(prod.designation.name)		
		return super(ijarah_hr_emp_deduct,self).create(cr, uid, vals, context)
	
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
				             'job_id':this.job_id.id # name.dbfieldname			
					})		

		result = super(ijarah_hr_emp_deduct, self).write(cr, uid, ids, vals, context=context)	
		return result

	def _get_number_of_days(self, for_month, month_end_date):
	
		DATETIME_FORMAT = "%Y-%m-%d"		
		from_dt = datetime.strptime(for_month, DATETIME_FORMAT)
		to_dt = datetime.strptime(month_end_date, DATETIME_FORMAT)
		timedelta = to_dt - from_dt
		diff_day = timedelta.days + float(timedelta.seconds) / 86400
		return diff_day		

	_name = "ijarah.hr.emp.deduct"
	_columns = {
		'name'	: fields.many2one("hr.employee","Employee No",required=True,domain="[('activate','=',True)]",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'emp_name':fields.char("Employee Name",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'job_id':fields.many2one("hr.job","Job Title",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'salary':fields.float("Salary",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'note':fields.text("Note",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'for_month':fields.date("For Month",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'month_end_date':fields.date("Date End",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'month_days':fields.integer("Days in Month",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'deduct_amount':fields.float('Deduction Amount',states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'state': fields.selection([('Draft', 'Draft'),('Open', 'Open'),('Done', 'Done')],'Status',  readonly=True,),
		'deduct_rule':fields.selection([('No of Days', 'No of Days'),('Fixed Amount', 'Fixed Amount')],'Deduction Type'),
		'no_of_days':fields.integer("No of Days",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'amount_per_days':fields.float("Amount Per Day",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'fixed_amount':fields.float("Fixed Amount",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'paid':fields.boolean("Paid",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
	}
	_defaults = {			
		'state'  : lambda * a :'Draft',
        	'for_month': lambda *a: time.strftime('%Y-%m-01'),
		'month_end_date': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
		'paid': False,	
	}
	
	def unlink(self, cr, uid, ids, context=None):
		ded = self.pool.get('ijarah.hr.emp.deduct').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in ded:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Deduction(s) which are already Opened or Done state !'))
#		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		return super(ijarah_hr_emp_deduct, self).unlink(cr, uid, ids, context=context)        			
#		return True
        
    		
	def validate_state(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'Open'}, context=context)
		return True
		         		    	
	def onchange_empno(self, cr, uid,ids,name,for_month,month_end_date,context=None):
		if name:		 
			this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
			contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
			diff_day = self._get_number_of_days(for_month, month_end_date)
			value ={'salary':this.contract_id.basic_salary,'emp_name':this.name_related,'job_id':this.job_id.id,
				'month_days':round(math.floor(diff_day+1)) }
			return {'value': value}

	def onchange_deduct_rule(self, cr, uid,ids,name,salary,month_days,deduct_rule,context=None):

		if deduct_rule:
			sal = salary
			md = month_days
			return	{'value':{'deduct_amount':0.00,'no_of_days':0,'amount_per_days':sal / md}}
		return True

	def onchange_nod(self, cr, uid,ids,amount_per_days,no_of_days,context=None):
			nod = no_of_days
			amount_per_day = amount_per_days
			value ={'deduct_amount':nod * amount_per_day }
			return {'value': value}

	def onchange_fixed_amount(self, cr, uid,ids,fixed_amount,context=None):
			fd = fixed_amount
			value ={'deduct_amount':fd }
			return {'value': value}


		
ijarah_hr_emp_deduct()
